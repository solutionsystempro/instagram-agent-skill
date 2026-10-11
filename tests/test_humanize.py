# Copyright (c) 2026 Ian Ryan Kirk. MIT License.
import unittest

from helpers import load, run_cli

humanize = load("ig-human", "humanize")
LEX = humanize.load_lexicon()


def clean(text):
    return humanize.humanize(text, LEX)[0]


class HumanizeTest(unittest.TestCase):
    def test_strips_em_dash_slop_and_invisibles(self):
        out, report = humanize.humanize(
            "We leverage robust tools — it’s crucial.​", LEX)
        self.assertNotIn("—", out)
        self.assertNotIn("​", out)
        self.assertNotIn("’", out)
        self.assertNotIn("leverage", out.lower())
        self.assertTrue(report["lexical"])
        self.assertTrue(report["invisible"])

    def test_urls_are_untouched(self):
        url = "https://example.com/leverage—robust"
        self.assertIn(url, clean(f"See {url} for more."))

    def test_capital_restored_after_deleted_opener(self):
        # The fix in "Restore sentence capitals after a deleted opener".
        out = clean("We ship fast. It works.\nStop scrolling, we tried this. Ask us.")
        self.assertIn("We tried this.", out)

    def test_lowercase_voice_is_left_lowercase(self):
        out = clean("all lower case here. stop scrolling, we tried it. ask us.")
        self.assertIn("we tried it", out)
        self.assertNotIn("We tried", out)

    def test_existing_lowercase_starts_are_not_raised(self):
        text = "We ship fast. Use a tool, e.g. the template. It works.\niPhone sales are up."
        out = clean(text)
        self.assertIn("e.g. the template", out)
        self.assertIn("\niPhone", out)

    def test_leading_ellipsis_survives(self):
        # Hook formula #21 opens mid-sentence on purpose.
        self.assertEqual(clean("...and he asked for a refund nine days later."),
                         "...and he asked for a refund nine days later.\n")
        self.assertIn("\n...and he asked", clean("I said no.\n...and he asked again."))

    def test_indentation_and_emoticons_are_kept(self):
        self.assertIn("\n    - indented", clean("Steps:\n    - indented\n    - item"))
        self.assertIn("great :)", clean("great :) see you"))

    def test_crlf_input(self):
        self.assertEqual(clean("Line one\r\nLine two — done\r\n"),
                         "Line one\nLine two, done\n")

    def test_empty_input(self):
        out, report = humanize.humanize("", LEX)
        self.assertEqual(out, "\n")
        self.assertFalse(any(report.values()))

    def test_cli_handles_emoji_through_a_pipe(self):
        p = run_cli("ig-human", "humanize.py", "-", stdin="Done \U0001F525 — really.\n")
        self.assertEqual(p.returncode, 0, p.stderr.decode("utf-8", "replace"))
        out = p.stdout.decode("utf-8").replace("\r\n", "\n")   # Windows text mode
        self.assertEqual(out, "Done \U0001F525, really.\n")


if __name__ == "__main__":
    unittest.main()
