# Copyright (c) 2026 Ian Ryan Kirk. MIT License.
import unittest

from helpers import load, run_cli

caption = load("ig-caption", "caption")

GOOD = (
    "I lost $18,000 on one missing clause.\n\n"
    "Here is the clause I now put in every client contract.\n\n"
    "Comment CONTRACT and I will send it.\n\n"
    "#freelance #contracts"
)


def check(result, name):
    return next(c for c in result["checks"] if c["check"] == name)


class CaptionTest(unittest.TestCase):
    def test_clean_caption_is_ready(self):
        a = caption.analyse(GOOD, keywords=["client contract"])
        self.assertEqual(a["verdict"], "READY", a["checks"])
        self.assertEqual(a["hashtags"], ["#freelance", "#contracts"])
        self.assertEqual(a["asks"], ["comment a keyword"])
        self.assertTrue(a["visible"].startswith("I lost $18,000"))

    def test_visible_window_cuts_at_125(self):
        a = caption.analyse("x" * 300)
        self.assertTrue(a["truncated"])
        self.assertEqual(len(a["visible"]), caption.TRUNCATE)

    def test_hashtag_cap_is_enforced(self):
        tags = " ".join(f"#tag{i}" for i in range(caption.HASHTAG_LIMIT + 1))
        a = caption.analyse("Real first line with a number 4.\n\n" + tags)
        self.assertEqual(check(a, "HASHTAGS")["status"], "FAIL")

    def test_unicode_hashtag_counts(self):
        a = caption.analyse("Paris in 3 days.\n\n#café #日本")
        self.assertEqual(a["hashtags"], ["#café", "#日本"])

    def test_over_limit_fails(self):
        a = caption.analyse("a" * (caption.LIMIT + 1))
        self.assertEqual(check(a, "LENGTH")["status"], "FAIL")

    def test_emoji_that_count_double_warn_at_the_limit(self):
        # Fits by code points, not by UTF-16 units.
        text = "a" * (caption.LIMIT - 10) + "\U0001F525" * 10
        a = caption.analyse(text)
        self.assertEqual(check(a, "LENGTH")["status"], "WARN")

    def test_skin_tone_and_variation_selector_are_one_emoji(self):
        a = caption.analyse("Done in 5 minutes \U0001F44D\U0001F3FD ❤️")
        self.assertEqual(a["emoji"], 2)

    def test_empty_caption(self):
        a = caption.analyse("")
        self.assertEqual(a["verdict"], "FIX")
        self.assertEqual(check(a, "FIRST LINE")["detail"], "the caption is empty")

    def test_crlf_is_not_counted(self):
        self.assertEqual(caption.analyse("ab\r\ncd")["characters"], 5)

    def test_cli_handles_emoji_through_a_pipe(self):
        p = run_cli("ig-caption", "caption.py", "-", stdin="Fire \U0001F525 in 3 days.\n")
        self.assertIn(p.returncode, (0, 1), p.stderr.decode("utf-8", "replace"))
        self.assertIn("\U0001F525", p.stdout.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
