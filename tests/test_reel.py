import unittest

from helpers import load, run_cli

hookscore = load("ig-reel", "hookscore")
beats = load("ig-reel", "beats")


class HookscoreTest(unittest.TestCase):
    def test_concrete_hook_beats_greeting(self):
        _, strong, verdict, flags = hookscore.run("I lost $18,000 because of one missing contract.")
        _, weak, _, weak_flags = hookscore.run("Hey guys, today I wanted to talk about content strategy")
        self.assertGreater(strong, weak)
        self.assertEqual(verdict, "STRONG")
        self.assertFalse(flags)
        self.assertTrue(any("Greeting" in f for f in weak_flags))

    def test_spoken_numbers_count_as_specific(self):
        score, _ = hookscore.check_specificity("I made zero dollars from three books")
        self.assertGreater(score, 15)

    def test_empty_hook_does_not_crash(self):
        _, overall, verdict, _ = hookscore.run("")
        self.assertEqual(verdict, "WEAK")
        self.assertGreaterEqual(overall, 0)

    def test_cli_handles_emoji_through_a_pipe(self):
        p = run_cli("ig-reel", "hookscore.py", "-",
                    stdin="Stop scrolling \U0001F525\nI lost $18,000 on one contract.\n")
        self.assertIn(p.returncode, (0, 1), p.stderr.decode("utf-8", "replace"))
        self.assertIn("HOOK RANKING", p.stdout.decode("utf-8"))

    def test_cli_empty_input_exits_2(self):
        self.assertEqual(run_cli("ig-reel", "hookscore.py", "-", stdin="").returncode, 2)


class BeatsTest(unittest.TestCase):
    SCRIPT = ("I lost $18,000 because of one missing contract.\n"
              "Section 4. Payment on delivery, not on approval.\n"
              "That one word change is worth $18,000 to me.\n")

    def test_beat_sheet_labels_and_loop(self):
        a = beats.analyse(self.SCRIPT, wpm=165, target=30)
        self.assertEqual(len(a["beats"]), 3)
        self.assertEqual(a["beats"][0]["label"], "HOOK")
        self.assertEqual(a["beats"][-1]["label"], "CTA")
        self.assertTrue(any(n.startswith("Loops:") and "$18,000" in n for n in a["notes"]))

    def test_long_beat_is_flagged(self):
        a = beats.analyse("Short hook with 5 words.\n" + " ".join(["word"] * 30) + "\n")
        self.assertTrue(a["beats"][1]["flags"])

    def test_empty_script(self):
        self.assertIsNone(beats.analyse("\n  \n"))

    def test_timecode_rolls_over_cleanly(self):
        self.assertEqual(beats.tc(59.96), "1:00.0")


if __name__ == "__main__":
    unittest.main()
