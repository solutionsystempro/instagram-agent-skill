# Changelog

## 1.1.0

Modifications by Ian Ryan Kirk on top of Jake Schincariol's 1.0. The skills,
lexicon, hook formulas, rubric and measurement are unchanged unless listed
here.

### Fixed

- **Windows crash on emoji.** On Windows, piped output defaulted to cp1252, so
  any emoji in a hook, caption or swipe row crashed `hookscore.py`,
  `swipe.py` and `caption.py` with `UnicodeEncodeError`. All six tools now use
  UTF-8 for stdin, stdout and stderr, and read files as `utf-8-sig` so a BOM
  from Notepad or Excel does not corrupt the first line or header.
- **`humanize.py` deleted a leading ellipsis.** A line opening on "...and he
  asked for a refund", which is hook formula #21, lost its ellipsis as
  "orphaned punctuation", and the next word was capitalised.
- **`humanize.py` raised capitals that were never lost.** The sentence-capital
  restore from 1.0's last commit applied to every lower-case sentence start,
  so "e.g. the" became "e.g. The" and "iPhone" became "IPhone". It now only
  raises starts that the writer did not already have, and skips camel-case
  brand words. The original fix (capital back after a deleted opener such as
  "Stop scrolling,") still works and has a test.
- **`humanize.py` flattened indentation**, despite the comment saying deeper
  indents were kept, removed the space before ":)", and pulled punctuation up
  across line breaks.
- **`caption.py` hashtag and emoji counts.** Hashtags with non-ASCII letters
  (`#café`) were not counted. Skin-tone modifiers and U+FE0F were counted as
  extra emoji. An empty caption now says it is empty. A caption that fits 2,200
  by code points but not if emoji count as two UTF-16 units now gets a WARN,
  since it is not certain which count Instagram uses.
- **`swipe.py` misread short-form counts.** "412K" parsed as 412 and "1.2M" as
  12, which is how Instagram displays counts. `--out swipe.md` with no folder
  crashed.
- **`beats.py`** could print "0:60.0" as a timecode, and `--wpm 0` divided by
  zero.
- **`swipe.py` mislabelled mixed baselines.** One row with an account median
  made the whole report say "baseline: account median", even for rows that
  fell back to follower count. Each row now records and shows the baseline it
  used (`med` or `fol`), and the header says "account median", "follower
  count", or "mixed" with the count of each.
- CRLF input normalised in `humanize.py` and `caption.py` for library callers.

### Added

- `tests/`: a standard-library `unittest` suite, 47 tests. They cover each
  tool's main path and the edge cases above, plus repo checks: manifests
  parse, versions agree, and the README lists exactly the skills that exist.
  Run it with `python -m unittest discover -s tests -v`.
- This changelog.
- Windows install instructions in the README.

### Changed

- **Trigger descriptions.** Every skill's description now names Instagram and
  the specific job. Several fired on generic phrases ("slides", "plan my week",
  "how do I follow up", "reply to these", "humanize") that would load them in
  sessions about other platforms or presentations.
- **Tool paths.** SKILL.md commands use `python "${CLAUDE_SKILL_DIR}/tool.py"`
  instead of `python3 tool.py`, so they work on Windows and when the pack is
  installed as a plugin or run from a project root. Cross-skill references to
  `hooks.json` use `${CLAUDE_SKILL_DIR}/../ig-reel/hooks.json`.
- **Official sources first.** `/ig-viral` now works from pasted data, then the
  Instagram Graph API, then a user-driven browser last, and no longer tells
  Claude to run yt-dlp against YouTube. It points to the YouTube Data API
  instead. `/ig-audit` names Insights, Meta Business Suite exports and the
  Graph API as sources. `/ig-dm` and `/ig-reply` state that the skill never
  sends a DM or posts a reply itself.
- **No keyword auto-DMs.** `/ig-reply`, `/ig-dm`, `/ig-story` and the README
  said keyword auto-replies set up in Meta's tools could run without review.
  They no longer recommend or set up auto-replies or auto-DMs. If the user
  already runs Meta's own automation, that is their configuration, outside
  this pack, which only drafts copy a human reviews and sends one at a time.
- README: credit to the original, a note that the measurement section is
  Jake's from 1.0 and was not re-run, the tool count corrected from five to
  six, a Tests section, and this list.
- LICENSE: added a modifications copyright line. Jake's line is unchanged.
- Version 1.1.0 in `plugin.json` and `marketplace.json`.

### Not changed

- **The five-hashtag cap.** The 1.0 linter enforces five hashtags per post,
  citing Instagram's December 2025 change. That was kept as written. If
  Instagram's limit has moved, change `HASHTAG_LIMIT` in `caption.py`.
- The scoring weights, thresholds and lexicon. No new evidence was gathered,
  so there was no basis to retune them.
- Plugin and marketplace URLs still point to the original repository.
