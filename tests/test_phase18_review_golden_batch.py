import json
import tempfile
import unittest
from dataclasses import fields
from pathlib import Path

from engine.intelligence.golden_visual_quality import GoldenVisualBlockers
from tools.phase18_review_golden_batch import REVIEW_VERSION, _BLOCKER_FIELDS, evaluate


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
        complete_blockers = {field: False for field in _BLOCKER_FIELDS}
        if blockers:
            complete_blockers.update(blockers)
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
            "blockers": complete_blockers,
        }

    def test_blocker_schema_tracks_dataclass_without_drift(self):
        self.assertEqual(set(_BLOCKER_FIELDS), {item.name for item in fields(GoldenVisualBlockers)})
        self.assertEqual(REVIEW_VERSION, "pul7sar-golden-visual-review-v2")

    def test_selects_highest_approved_visual(self):
        with tempfile.TemporaryDirectory() as temp:
            execution, review = self.write_inputs(temp, [
                self.review("a", 1, 8.4),
                self.review("b", 2, 8.7),
            ])
            result = evaluate(str(execution), str(review))
            self.assertEqual(result["status"], "GOLDEN_VISUAL_SELECTED")
            self.assertEqual(result["selected"]["request_id"], "b")
            self.assertEqual(result["selected"]["quality_tier"], "golden")

    def test_elite_quality_tier_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            execution, review = self.write_inputs(temp, [
                self.review("a", 1, 8.7),
                self.review("b", 2, 9.2),
            ])
            result = evaluate(str(execution), str(review))
            self.assertEqual(result["selected"]["request_id"], "b")
            self.assertEqual(result["selected"]["quality_tier"], "elite")

    def test_blocker_beats_numeric_score(self):
        with tempfile.TemporaryDirectory() as temp:
            execution, review = self.write_inputs(temp, [
                self.review("a", 1, 9.9, {"pseudo_text_or_gibberish": True}),
                self.review("b", 2, 8.6),
            ])
            result = evaluate(str(execution), str(review))
            self.assertEqual(result["selected"]["request_id"], "b")
            self.assertIn("a", result["rejected_request_ids"])
            blocked = next(item for item in result["ranked"] if item["request_id"] == "a")
            self.assertEqual(blocked["quality_tier"], "below_golden")

    def test_generated_platform_brand_blocker_cannot_be_silently_waived(self):
        with tempfile.TemporaryDirectory() as temp:
            execution, review = self.write_inputs(temp, [
                self.review("a", 1, 9.9, {"generated_platform_brand_or_wordmark": True}),
                self.review("b", 2, 8.6),
            ])
            result = evaluate(str(execution), str(review))
            self.assertEqual(result["selected"]["request_id"], "b")
            blocked = next(item for item in result["ranked"] if item["request_id"] == "a")
            self.assertIn("generated_platform_brand_or_wordmark", blocked["blockers"])

    def test_broken_sport_surface_geometry_blocker_cannot_be_silently_waived(self):
        with tempfile.TemporaryDirectory() as temp:
            execution, review = self.write_inputs(temp, [
                self.review("a", 1, 9.9, {"broken_sport_surface_geometry": True}),
                self.review("b", 2, 8.6),
            ])
            result = evaluate(str(execution), str(review))
            self.assertEqual(result["selected"]["request_id"], "b")
            blocked = next(item for item in result["ranked"] if item["request_id"] == "a")
            self.assertIn("broken_sport_surface_geometry", blocked["blockers"])

    def test_missing_blocker_field_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            first = self.review("a", 1, 8.6)
            first["blockers"].pop("broken_sport_surface_geometry")
            execution, review = self.write_inputs(temp, [first, self.review("b", 2, 8.6)])
            with self.assertRaisesRegex(ValueError, "blocker schema mismatch"):
                evaluate(str(execution), str(review))

    def test_review_must_cover_every_generated_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            execution, review = self.write_inputs(temp, [self.review("a", 1, 8.6)])
            with self.assertRaisesRegex(ValueError, "cover every"):
                evaluate(str(execution), str(review))

    def test_seed_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            execution, review = self.write_inputs(temp, [
                self.review("a", 999, 8.6), self.review("b", 2, 8.6)
            ])
            with self.assertRaisesRegex(ValueError, "seed mismatch"):
                evaluate(str(execution), str(review))

    def test_null_score_from_unedited_template_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            first = self.review("a", 1, 8.6)
            first["scores"]["editorial_realism"] = None
            execution, review = self.write_inputs(temp, [first, self.review("b", 2, 8.6)])
            with self.assertRaisesRegex(ValueError, "still null"):
                evaluate(str(execution), str(review))

    def test_stale_v1_review_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            execution, review = self.write_inputs(
                temp,
                [self.review("a", 1, 8.6), self.review("b", 2, 8.6)],
                review_version="pul7sar-golden-visual-review-v1",
            )
            with self.assertRaisesRegex(ValueError, "review version"):
                evaluate(str(execution), str(review))

    def test_unknown_review_version_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            execution, review = self.write_inputs(
                temp,
                [self.review("a", 1, 8.6), self.review("b", 2, 8.6)],
                review_version="future-review",
            )
            with self.assertRaisesRegex(ValueError, "review version"):
                evaluate(str(execution), str(review))

    def test_unknown_blocker_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            first = self.review("a", 1, 8.6)
            first["blockers"]["mystery_blocker"] = True
            execution, review = self.write_inputs(temp, [first, self.review("b", 2, 8.6)])
            with self.assertRaisesRegex(ValueError, "blocker schema mismatch"):
                evaluate(str(execution), str(review))


if __name__ == "__main__":
    unittest.main()
