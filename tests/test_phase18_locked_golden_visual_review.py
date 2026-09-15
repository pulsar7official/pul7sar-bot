import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.locked_golden_visual_review import (
    LOCKED_GOLDEN_REVIEW_VERSION,
    LockedGoldenVisualReviewGate,
)


class LockedGoldenVisualReviewTests(unittest.TestCase):
    def make_semantic(self, root: Path, *, approved=True):
        png = root / "locked.png"
        png.write_bytes(b"locked-real-artifact-bytes")
        import hashlib
        sha = hashlib.sha256(png.read_bytes()).hexdigest()
        payload = {
            "status": "FOOTBALL_PITCH_SEMANTIC_REVIEW_COMPLETE",
            "candidate": 1,
            "request_id": "golden-v5-candidate-01",
            "seed": 7007001,
            "locked_png": str(png),
            "locked_png_sha256": sha,
            "semantic_approved": approved,
            "semantic_failures": [] if approved else ["sport_geometry_alignment_invalid"],
            "golden_quality_approved": False,
            "publication_ready": False,
            "gates_not_waived": [
                "fact_lock",
                "identity_verification",
                "sentiment_neutrality",
                "semantic_layer_ownership",
                "semantic_publication",
                "golden_visual_quality",
                "exact_brand_integrity",
                "typography_integrity",
                "publication_readiness",
            ],
        }
        receipt = root / "semantic.json"
        receipt.write_text(json.dumps(payload), encoding="utf-8")
        return receipt, png

    @staticmethod
    def complete_review(template, score=8.7):
        review = json.loads(json.dumps(template))
        review["scores"] = {field: score for field in review["scores"]}
        return review

    def test_template_is_bound_to_semantically_approved_locked_png(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            semantic, png = self.make_semantic(root)
            template = LockedGoldenVisualReviewGate().build_template(semantic_review_path=str(semantic))
            self.assertEqual(template["review_version"], LOCKED_GOLDEN_REVIEW_VERSION)
            self.assertEqual(template["locked_png"], str(png.resolve()))
            self.assertFalse(template["publication_ready"])
            self.assertTrue(all(value is None for value in template["scores"].values()))
            self.assertIn("generated_platform_brand_or_wordmark", template["blockers"])
            self.assertIn("broken_sport_surface_geometry", template["blockers"])

    def test_semantic_failure_blocks_template_before_human_scoring(self):
        with tempfile.TemporaryDirectory() as temp:
            semantic, _ = self.make_semantic(Path(temp), approved=False)
            with self.assertRaisesRegex(RuntimeError, "SEMANTIC_REVIEW_NOT_APPROVED"):
                LockedGoldenVisualReviewGate().build_template(semantic_review_path=str(semantic))

    def test_clean_golden_review_can_approve_but_never_publish(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            semantic, _ = self.make_semantic(root)
            gate = LockedGoldenVisualReviewGate()
            review = self.complete_review(gate.build_template(semantic_review_path=str(semantic)), score=8.7)
            review_path = root / "review.json"
            review_path.write_text(json.dumps(review), encoding="utf-8")
            result = gate.evaluate(
                semantic_review_path=str(semantic),
                review_path=str(review_path),
                output_dir=str(root / "out"),
            )
            self.assertTrue(result["golden_quality_approved"])
            self.assertEqual(result["quality_tier"], "golden")
            self.assertFalse(result["publication_ready"])

    def test_generated_platform_brand_hard_blocker_beats_99_score(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            semantic, _ = self.make_semantic(root)
            gate = LockedGoldenVisualReviewGate()
            review = self.complete_review(gate.build_template(semantic_review_path=str(semantic)), score=9.9)
            review["blockers"]["generated_platform_brand_or_wordmark"] = True
            review_path = root / "review.json"
            review_path.write_text(json.dumps(review), encoding="utf-8")
            result = gate.evaluate(
                semantic_review_path=str(semantic),
                review_path=str(review_path),
                output_dir=str(root / "out"),
            )
            self.assertFalse(result["golden_quality_approved"])
            self.assertIn("generated_platform_brand_or_wordmark", result["blockers"])
            self.assertFalse(result["publication_ready"])

    def test_missing_blocker_field_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            semantic, _ = self.make_semantic(root)
            gate = LockedGoldenVisualReviewGate()
            review = self.complete_review(gate.build_template(semantic_review_path=str(semantic)))
            review["blockers"].pop("broken_sport_surface_geometry")
            review_path = root / "review.json"
            review_path.write_text(json.dumps(review), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "BLOCKER_SCHEMA_MISMATCH"):
                gate.evaluate(
                    semantic_review_path=str(semantic),
                    review_path=str(review_path),
                    output_dir=str(root / "out"),
                )

    def test_png_tampering_after_semantic_review_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            semantic, png = self.make_semantic(root)
            gate = LockedGoldenVisualReviewGate()
            template = gate.build_template(semantic_review_path=str(semantic))
            review = self.complete_review(template)
            review_path = root / "review.json"
            review_path.write_text(json.dumps(review), encoding="utf-8")
            png.write_bytes(b"tampered-after-semantic-review")
            with self.assertRaisesRegex(RuntimeError, "PNG_SHA256_MISMATCH"):
                gate.evaluate(
                    semantic_review_path=str(semantic),
                    review_path=str(review_path),
                    output_dir=str(root / "out"),
                )

    def test_review_identity_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            semantic, _ = self.make_semantic(root)
            gate = LockedGoldenVisualReviewGate()
            review = self.complete_review(gate.build_template(semantic_review_path=str(semantic)))
            review["request_id"] = "different-request"
            review_path = root / "review.json"
            review_path.write_text(json.dumps(review), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "IDENTITY_MISMATCH"):
                gate.evaluate(
                    semantic_review_path=str(semantic),
                    review_path=str(review_path),
                    output_dir=str(root / "out"),
                )


if __name__ == "__main__":
    unittest.main()
