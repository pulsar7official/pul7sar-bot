import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.hybrid_human_review_decision import HybridHumanReviewDecisionGate


PNG = b"\x89PNG\r\n\x1a\n" + b"phase18-human-review"


class HybridHumanReviewDecisionTests(unittest.TestCase):
    def _fixture(self, root: Path):
        review_dir = root / "output" / "review"
        review_dir.mkdir(parents=True)
        base = review_dir / "01-proven-base.png"
        hybrid = review_dir / "02-semantic-approved-hybrid.png"
        base.write_bytes(PNG + b"-base")
        hybrid.write_bytes(PNG + b"-hybrid")
        gate = HybridHumanReviewDecisionGate(root=root)
        bundle = {
            "schema": "pul7sar-hybrid-human-review-bundle-v1",
            "status": "HYBRID_HUMAN_REVIEW_BUNDLE_READY",
            "candidate": 1,
            "review_base_png": str(base),
            "review_hybrid_png": str(hybrid),
            "base_png_sha256": gate._sha256(base),
            "hybrid_png_sha256": gate._sha256(hybrid),
            "semantic_layer_gate_approved": True,
            "hybrid_semantic_review_approved": True,
            "human_visual_review_required": True,
            "automatic_selection_performed": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        bundle_path = root / "output" / "hybrid-human-review-bundle.json"
        bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
        return gate, bundle_path, base, hybrid

    @staticmethod
    def _complete(template, *, decision="accept", value=True):
        template["checks"] = {key: value for key in template["checks"]}
        template["decision"] = decision
        template["review_note"] = "explicit human visual judgment"
        return template

    def test_acceptance_is_bound_to_exact_review_bytes_and_keeps_downstream_gates_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            gate, bundle, _, _ = self._fixture(root)
            review = root / "output" / "review-template.json"
            review.write_text(json.dumps(self._complete(gate.build_template(bundle_path=bundle))), encoding="utf-8")
            result = gate.evaluate(bundle_path=bundle, review_path=review, output_path=root / "output" / "decision.json")
            self.assertEqual(result["status"], "HYBRID_HUMAN_REVIEW_ACCEPTED")
            self.assertTrue(result["human_visual_review_approved"])
            self.assertFalse(result["automatic_selection_performed"])
            self.assertFalse(result["golden_quality_approved"])
            self.assertFalse(result["publication_ready"])

    def test_acceptance_requires_every_visual_integration_check(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            gate, bundle, _, _ = self._fixture(root)
            payload = self._complete(gate.build_template(bundle_path=bundle))
            payload["checks"]["pitch_perspective_valid"] = False
            review = root / "output" / "review-template.json"
            review.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "ACCEPT_REQUIRES_ALL_CHECKS"):
                gate.evaluate(bundle_path=bundle, review_path=review, output_path=root / "output" / "decision.json")

    def test_rejection_is_recorded_without_granting_golden_or_publication_authority(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            gate, bundle, _, _ = self._fixture(root)
            payload = self._complete(gate.build_template(bundle_path=bundle), decision="reject")
            payload["checks"]["photographic_integration_valid"] = False
            review = root / "output" / "review-template.json"
            review.write_text(json.dumps(payload), encoding="utf-8")
            result = gate.evaluate(bundle_path=bundle, review_path=review, output_path=root / "output" / "decision.json")
            self.assertEqual(result["status"], "HYBRID_HUMAN_REVIEW_REJECTED")
            self.assertFalse(result["human_visual_review_approved"])
            self.assertFalse(result["golden_quality_approved"])
            self.assertFalse(result["publication_ready"])

    def test_hybrid_tampering_after_bundle_creation_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            gate, bundle, _, hybrid = self._fixture(root)
            template = gate.build_template(bundle_path=bundle)
            hybrid.write_bytes(PNG + b"-tampered")
            review = root / "output" / "review-template.json"
            review.write_text(json.dumps(self._complete(template)), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "HYBRID_SHA256_MISMATCH"):
                gate.evaluate(bundle_path=bundle, review_path=review, output_path=root / "output" / "decision.json")

    def test_incomplete_checklist_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            gate, bundle, _, _ = self._fixture(root)
            payload = gate.build_template(bundle_path=bundle)
            payload["decision"] = "reject"
            review = root / "output" / "review-template.json"
            review.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "CHECK_INCOMPLETE"):
                gate.evaluate(bundle_path=bundle, review_path=review, output_path=root / "output" / "decision.json")

    def test_output_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            gate, bundle, _, _ = self._fixture(root)
            review = root / "output" / "review-template.json"
            review.write_text(json.dumps(self._complete(gate.build_template(bundle_path=bundle))), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "OUTPUT_ESCAPES_REPOSITORY"):
                gate.evaluate(bundle_path=bundle, review_path=review, output_path=Path(outside) / "decision.json")


if __name__ == "__main__":
    unittest.main()
