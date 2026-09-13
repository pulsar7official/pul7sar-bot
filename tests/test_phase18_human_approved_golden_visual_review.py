import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.human_approved_golden_visual_review import HumanApprovedGoldenVisualReviewGate


PNG = b"\x89PNG\r\n\x1a\nphase18-human-golden"


class HumanApprovedGoldenVisualReviewTests(unittest.TestCase):
    def fixture(self, root: Path, *, accepted: bool = True):
        base = root / "base.png"
        hybrid = root / "hybrid.png"
        review_hybrid = root / "review-hybrid.png"
        base.write_bytes(PNG + b"-base")
        hybrid.write_bytes(PNG + b"-hybrid")
        review_hybrid.write_bytes(hybrid.read_bytes())
        base_sha = hashlib.sha256(base.read_bytes()).hexdigest()
        hybrid_sha = hashlib.sha256(hybrid.read_bytes()).hexdigest()

        handoff = {
            "status": "FIRST_GOLDEN_PNG_HYBRID_HANDOFF_READY",
            "branch": "phase18/story-intelligence",
            "manifest_version": "pul7sar-golden-batch-v5",
            "candidate": 1,
            "request_id": "golden-v5-candidate-01",
            "seed": 7007001,
            "cost_mode": "$0-local",
            "resolved_dtype": "bfloat16",
            "png": str(base),
            "base_png_sha256": base_sha,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        continuation = {
            "status": "FIRST_GOLDEN_HYBRID_SEMANTIC_PROOF_READY",
            "branch": "phase18/story-intelligence",
            "manifest_version": "pul7sar-golden-batch-v5",
            "candidate": 1,
            "base_png": str(base),
            "hybrid_png": str(hybrid),
            "hybrid_png_sha256": hybrid_sha,
            "artifact_integrity": {"valid": True, "input_sha256": base_sha, "output_sha256": hybrid_sha},
            "semantic_layer_gate_approved": True,
            "hybrid_semantic_review_approved": True,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        decision = {
            "schema": "pul7sar-hybrid-human-review-decision-v1",
            "status": "HYBRID_HUMAN_REVIEW_ACCEPTED" if accepted else "HYBRID_HUMAN_REVIEW_REJECTED",
            "candidate": 1,
            "review_hybrid_png": str(review_hybrid),
            "base_png_sha256": base_sha,
            "hybrid_png_sha256": hybrid_sha,
            "human_visual_review_approved": accepted,
            "automatic_selection_performed": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        paths = []
        for name, payload in (("handoff.json", handoff), ("continuation.json", continuation), ("decision.json", decision)):
            path = root / name
            path.write_text(json.dumps(payload), encoding="utf-8")
            paths.append(path)
        return paths, base, hybrid, review_hybrid

    @staticmethod
    def complete(template, score=8.7):
        review = json.loads(json.dumps(template))
        review["scores"] = {key: score for key in review["scores"]}
        return review

    def test_template_requires_accepted_human_decision_and_binds_hybrid_sha(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths, _, hybrid, _ = self.fixture(root)
            gate = HumanApprovedGoldenVisualReviewGate(root=root)
            template = gate.build_template(handoff_path=paths[0], continuation_path=paths[1], human_decision_path=paths[2])
            self.assertTrue(template["human_visual_review_approved"])
            self.assertEqual(template["hybrid_png_sha256"], hashlib.sha256(hybrid.read_bytes()).hexdigest())
            self.assertFalse(template["golden_quality_approved"])
            self.assertFalse(template["publication_ready"])

    def test_rejected_human_decision_blocks_golden_template(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths, _, _, _ = self.fixture(root, accepted=False)
            with self.assertRaisesRegex(RuntimeError, "HUMAN_DECISION_NOT_ACCEPTED"):
                HumanApprovedGoldenVisualReviewGate(root=root).build_template(
                    handoff_path=paths[0], continuation_path=paths[1], human_decision_path=paths[2]
                )

    def test_clean_review_can_approve_golden_but_never_publish(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths, _, _, _ = self.fixture(root)
            gate = HumanApprovedGoldenVisualReviewGate(root=root)
            review = self.complete(gate.build_template(handoff_path=paths[0], continuation_path=paths[1], human_decision_path=paths[2]))
            review_path = root / "review.json"
            review_path.write_text(json.dumps(review), encoding="utf-8")
            result = gate.evaluate(
                handoff_path=paths[0], continuation_path=paths[1], human_decision_path=paths[2],
                review_path=review_path, output_dir=root / "out",
            )
            self.assertTrue(result["golden_quality_approved"])
            self.assertFalse(result["publication_ready"])

    def test_hard_blocker_beats_99_score(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths, _, _, _ = self.fixture(root)
            gate = HumanApprovedGoldenVisualReviewGate(root=root)
            review = self.complete(gate.build_template(handoff_path=paths[0], continuation_path=paths[1], human_decision_path=paths[2]), 9.9)
            review["blockers"]["broken_sport_surface_geometry"] = True
            review_path = root / "review.json"
            review_path.write_text(json.dumps(review), encoding="utf-8")
            result = gate.evaluate(
                handoff_path=paths[0], continuation_path=paths[1], human_decision_path=paths[2],
                review_path=review_path, output_dir=root / "out",
            )
            self.assertFalse(result["golden_quality_approved"])
            self.assertIn("broken_sport_surface_geometry", result["blockers"])

    def test_hybrid_tampering_after_human_acceptance_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths, _, hybrid, _ = self.fixture(root)
            gate = HumanApprovedGoldenVisualReviewGate(root=root)
            gate.build_template(handoff_path=paths[0], continuation_path=paths[1], human_decision_path=paths[2])
            hybrid.write_bytes(PNG + b"-tampered")
            with self.assertRaisesRegex(RuntimeError, "HYBRID_SHA256_MISMATCH"):
                gate.build_template(handoff_path=paths[0], continuation_path=paths[1], human_decision_path=paths[2])

    def test_review_binding_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths, _, _, _ = self.fixture(root)
            gate = HumanApprovedGoldenVisualReviewGate(root=root)
            review = self.complete(gate.build_template(handoff_path=paths[0], continuation_path=paths[1], human_decision_path=paths[2]))
            review["seed"] = 123
            review_path = root / "review.json"
            review_path.write_text(json.dumps(review), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "BINDING_MISMATCH:seed"):
                gate.evaluate(
                    handoff_path=paths[0], continuation_path=paths[1], human_decision_path=paths[2],
                    review_path=review_path, output_dir=root / "out",
                )


if __name__ == "__main__":
    unittest.main()
