import json
import tempfile
import unittest
from pathlib import Path

from tools.phase18_review_golden_batch import REVIEW_VERSION, evaluate


class ReviewGoldenBatchTests(unittest.TestCase):
    def write_inputs(self, root, reviews, *, review_version=REVIEW_VERSION):
        root = Path(root)
        execution = {
            "status": "REAL_VISUAL_PROOF_BATCH_GENERATED",
            "cost_mode": "$0-local",
            "candidates": [
                {"request_id": "a", "seed": 1, "png": "a.png", "metadata": "a.json"},
                {"request_id": "b", "seed": 2, "png": "b.png", "metadata": "b.json"},
            ],
        }
        execution_path = root / "execution.json"
        review_path = root / "review.json"
        execution_path.write_text(json.dumps(execution), encoding="utf-8")
        review_path.write_text(json.dumps({"review_version": review_version, "candidates": reviews}), encoding="utf-8")
        return execution_path, review_path

    def review(self, request_id, seed, score, blockers=None):
        return {
            "request_id": request_id,
            "seed": seed,
            "scores": {
                "editorial_realism": score,
                "composition_hierarchy": score,
                "stadium_depth": score,
                "controlled_lighting": score,
                "protected_zone_cleanliness": score,
                "platform_crop_strength": score,
            },
            "blockers": blockers or {},
        }

    def test_selects_highest_approved_visual(self):
        with tempfile.TemporaryDirectory() as temp:
            execution, review = self.write_inputs(temp, [
                self.review("a", 1, 7.8),
                self.review("b", 2, 8.7),
            ])
            result = evaluate(str(execution), str(review))
            self.assertEqual(result["status"], "GOLDEN_VISUAL_SELECTED")
            self.assertEqual(result["selected"]["request_id"], "b")

    def test_blocker_beats_numeric_score(self):
        with tempfile.TemporaryDirectory() as temp:
            execution, review = self.write_inputs(temp, [
                self.review("a", 1, 9.9, {"pseudo_text_or_gibberish": True}),
                self.review("b", 2, 8.1),
            ])
            result = evaluate(str(execution), str(review))
            self.assertEqual(result["selected"]["request_id"], "b")
            self.assertIn("a", result["rejected_request_ids"])

    def test_review_must_cover_every_generated_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            execution, review = self.write_inputs(temp, [self.review("a", 1, 8.0)])
            with self.assertRaisesRegex(ValueError, "cover every"):
                evaluate(str(execution), str(review))

    def test_seed_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            execution, review = self.write_inputs(temp, [
                self.review("a", 999, 8.0), self.review("b", 2, 8.0)
            ])
            with self.assertRaisesRegex(ValueError, "seed mismatch"):
                evaluate(str(execution), str(review))

    def test_null_score_from_unedited_template_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            first = self.review("a", 1, 8.0)
            first["scores"]["editorial_realism"] = None
            execution, review = self.write_inputs(temp, [first, self.review("b", 2, 8.0)])
            with self.assertRaisesRegex(ValueError, "still null"):
                evaluate(str(execution), str(review))

    def test_unknown_review_version_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            execution, review = self.write_inputs(
                temp,
                [self.review("a", 1, 8.0), self.review("b", 2, 8.0)],
                review_version="future-review",
            )
            with self.assertRaisesRegex(ValueError, "review version"):
                evaluate(str(execution), str(review))

    def test_unknown_blocker_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            first = self.review("a", 1, 8.0, {"mystery_blocker": True})
            execution, review = self.write_inputs(temp, [first, self.review("b", 2, 8.0)])
            with self.assertRaisesRegex(ValueError, "unknown review blockers"):
                evaluate(str(execution), str(review))


if __name__ == "__main__":
    unittest.main()
