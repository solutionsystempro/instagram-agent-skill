"""Consistency checks: manifests parse, versions agree, and the README
lists exactly the skills that exist."""

import json
import os
import re
import unittest

from helpers import ROOT, SKILLS

WORDS = {13: "Thirteen"}


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return fh.read()


def skill_dirs():
    return sorted(d for d in os.listdir(SKILLS)
                  if os.path.isfile(os.path.join(SKILLS, d, "SKILL.md")))


class RepoTest(unittest.TestCase):
    def test_manifests_parse_and_versions_agree(self):
        plugin = json.loads(read(".claude-plugin", "plugin.json"))
        market = json.loads(read(".claude-plugin", "marketplace.json"))
        entry = next(p for p in market["plugins"] if p["name"] == plugin["name"])
        self.assertEqual(plugin["version"], entry["version"])

    def test_data_files_parse(self):
        for path in (("ig-reel", "hooks.json"), ("ig-human", "slop.json"),
                     ("ig-profile", "rubric.json")):
            json.loads(read("skills", *path))

    def test_rubric_totals_100(self):
        rubric = json.loads(read("skills", "ig-profile", "rubric.json"))
        self.assertEqual(sum(i["points"] for i in rubric["items"]), 100)

    def test_skill_names_match_folders(self):
        for d in skill_dirs():
            front = read("skills", d, "SKILL.md").split("---")[1]
            self.assertRegex(front, rf"(?m)^name: {re.escape(d)}$")
            self.assertIn("Instagram", front, f"{d} description should name the platform")

    def test_readme_lists_every_skill_and_no_others(self):
        readme = read("README.md")
        listed = set(re.findall(r"(?m)^\| `/(ig-[a-z]+)` \|", readme))
        self.assertEqual(listed, set(skill_dirs()))
        self.assertIn(WORDS[len(skill_dirs())] + " Claude skills", readme)

    def test_skill_docs_do_not_call_python3_directly(self):
        for d in skill_dirs():
            self.assertNotRegex(read("skills", d, "SKILL.md"), r"(?m)^python3 ",
                                f"{d}: use python \"${{CLAUDE_SKILL_DIR}}/...\"")


if __name__ == "__main__":
    unittest.main()
