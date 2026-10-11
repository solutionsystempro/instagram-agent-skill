import unittest

from helpers import load

detect = load("ig-human", "detect")
humanize = load("ig-human", "humanize")
LEX = humanize.load_lexicon()

SLOP = (
    "In today’s fast-paced world, it’s crucial to leverage robust, seamless "
    "solutions — delve into the transformative landscape. Moreover, unlock the "
    "potential of innovation. Furthermore, embrace a holistic paradigm. Additionally, "
    "navigate the ever-evolving journey. Stop scrolling and follow for more."
)
HUMAN = (
    "I raised my prices 40% in March. Lost one client. Just one, and he was the guy "
    "who emailed me at 11pm every Sunday about fonts. I didn't miss him. My income "
    "went from $6,200 a month to $8,900 by June, and I'm working fewer hours. "
    "Took me eight months to stop being scared of it. You'll be scared too. Do it anyway."
)


class DetectTest(unittest.TestCase):
    def test_human_text_scores_above_slop(self):
        _, slop_score, slop_verdict = detect.run(SLOP, LEX)
        _, human_score, _ = detect.run(HUMAN, LEX)
        self.assertGreater(human_score, slop_score + 20)
        self.assertEqual(slop_verdict, "FLAGGED")

    def test_scores_stay_in_range(self):
        results, overall, _ = detect.run(SLOP + "​" * 20, LEX)
        for score, _ in results.values():
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)
        self.assertGreaterEqual(overall, 0)

    def test_humanize_improves_the_score(self):
        _, before, _ = detect.run(SLOP, LEX)
        _, after, _ = detect.run(humanize.humanize(SLOP, LEX)[0], LEX)
        self.assertGreater(after, before)

    def test_empty_text_does_not_crash(self):
        results, overall, verdict = detect.run("", LEX)
        self.assertEqual(set(results), set(detect.CHECKS))
        self.assertIn(verdict, ("PASS", "REVIEW", "FLAGGED"))


if __name__ == "__main__":
    unittest.main()
