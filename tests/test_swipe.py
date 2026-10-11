import os
import tempfile
import unittest

from helpers import load, run_cli

swipe = load("ig-viral", "swipe")

TSV = (
    "﻿account\tfollowers\tmedian\tviews\thook\n"
    "@a\t48K\t11,000\t412K\tnobody tells you that your first 30 reels are supposed to flop\n"
    "@b\t2M\t900000\t1.2M\tin this video I am going to show you my morning routine \U0001F525\n"
    "@c\t4000\t3000\t180000\tsteal this four line follow up it took me two years\n"
)


class SwipeTest(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".tsv")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(TSV)

    def tearDown(self):
        os.remove(self.path)

    def test_parse_count_short_forms(self):
        self.assertEqual(swipe.parse_count("412K"), 412_000)
        self.assertEqual(swipe.parse_count("1.2M"), 1_200_000)
        self.assertEqual(swipe.parse_count("412,000"), 412_000)
        self.assertIsNone(swipe.parse_count(""))

    def test_ranks_by_outlier_not_views(self):
        rows = swipe.read_rows(self.path)
        self.assertEqual(rows[0]["account"], "@a")      # BOM stripped from header
        a = swipe.analyse(rows, swipe.load_formulas(swipe.HOOKS))
        self.assertEqual([r["account"] for r in a["reels"]], ["@c", "@a", "@b"])
        self.assertEqual(a["reels"][0]["outlier"], 60.0)
        self.assertEqual(a["reels"][1]["formula"], "Nobody Tells You")
        self.assertEqual(a["baseline"], "account median")

    def test_missing_hooks_file_degrades(self):
        a = swipe.analyse(swipe.read_rows(self.path), swipe.load_formulas("no/such/file.json"))
        self.assertEqual(a["unclassified"], 3)

    def test_rows_without_views_are_skipped(self):
        fd, path = tempfile.mkstemp(suffix=".tsv")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write("account\tviews\thook\n@x\t\tno views here\n")
        try:
            self.assertEqual(swipe.read_rows(path), [])
        finally:
            os.remove(path)

    def test_cli_writes_markdown_to_a_bare_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = run_cli("ig-viral", "swipe.py", self.path, "--out", "swipe.md", cwd=tmp)
            self.assertEqual(p.returncode, 0, p.stderr.decode("utf-8", "replace"))
            with open(os.path.join(tmp, "swipe.md"), encoding="utf-8") as fh:
                self.assertIn("# Swipe file", fh.read())
            self.assertIn("\U0001F525", p.stdout.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
