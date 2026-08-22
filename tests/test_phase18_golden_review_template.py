import json
import tempfile
import unittest
from pathlib import Path

from tools.phase18_build_golden_review_template import BLOCKER_FIELDS, SCORE_FIELDS, build_template


class GoldenReviewTemplateTests(unittest.TestCase):
    def write_execution(self, root, *, status="REAL_VISUAL_PROOF_BATCH_GENERATED", cost="$0-local"):
        data = {
            "status": status,
            "cost_mode": cost,
            "candidates": [
                {"request_id": "candidate-a", "seed": 101, "png": "a.png", "metadata": "a.json"},
                {"request_id": "candidate-b", "seed": 102, "png": "b.png", "metadata": "b.json"},
            ],
        }
        path = Path(root) / "execution.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_template_preserves_ids_seeds_and_real_proof_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.write_execution(temp)
            template = build_template(str(path))
            self.assertEqual(template["review_version"], "pul7sar-golden-visual-review-v1")
            self.assertEqual([item["request_id"] for item in template["candidates"]], ["candidate-a", "candidate-b"])
            self.assertEqual([item["seed"] for item in template["candidates"]], [101, 102])
            self.assertEqual(template["candidates"][0]["png"], "a.png")

    def test_scores_are_never_pre_fabricated(self):
        with tempfile.TemporaryDirectory() as temp:
            template = build_template(str(self.write_execution(temp)))
            for candidate in template["candidates"]:
                self.assertEqual(set(candidate["scores"]), set(SCORE_FIELDS))
                self.assertTrue(all(value is None for value in candidate["scores"].values()))
                self.assertEqual(set(candidate["blockers"]), set(BLOCKER_FIELDS))
                self.assertTrue(all(value is False for value in candidate["blockers"].values()))

    def test_non_real_or_non_zero_cost_batch_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            bad_status = self.write_execution(temp, status="SIMULATED")
            with self.assertRaisesRegex(ValueError, "real visual proof"):
                build_template(str(bad_status))
            bad_cost = self.write_execution(temp, cost="paid")
            with self.assertRaisesRegex(ValueError, "\\$0-local"):
                build_template(str(bad_cost))


if __name__ == "__main__":
    unittest.main()
