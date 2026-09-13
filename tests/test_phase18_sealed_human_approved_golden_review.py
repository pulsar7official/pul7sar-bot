import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from engine.intelligence.first_golden_review_packet_integrity import (
    FirstGoldenReviewPacketIntegrity,
    verification_payload,
)
from engine.intelligence.sealed_human_approved_golden_review import SealedHumanApprovedGoldenReviewGate


PNG = b"\x89PNG\r\n\x1a\n" + b"golden"


class _FakeGolden:
    def build_template(self, **kwargs):
        return {
            "review_version": "pul7sar-human-approved-golden-review-v1",
            "status": "HUMAN_APPROVED_GOLDEN_VISUAL_REVIEW_TEMPLATE",
            "golden_quality_approved": False,
            "publication_ready": False,
        }

    def evaluate(self, **kwargs):
        return {
            "status": "HUMAN_APPROVED_GOLDEN_VISUAL_APPROVED",
            "golden_quality_approved": True,
            "publication_ready": False,
        }


class SealedHumanApprovedGoldenReviewTests(unittest.TestCase):
    def _fixture(self, root: Path):
        admission = root / "original-scene-runtime-admission.json"
        admission.write_text(json.dumps({
            "schema": "pul7sar-golden-original-scene-admission-v1",
            "status": "GOLDEN_ORIGINAL_SCENE_RUNTIME_ADMITTED",
            "candidate": 1,
            "cost_mode": "$0-local",
            "semantic_inspection_required": True,
            "generated_branding_allowed": False,
            "generated_exact_facts_allowed": False,
            "generated_sport_geometry_allowed": False,
            "queue_mutated": False,
            "png_created": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }), encoding="utf-8")

        evidence = {}
        for name in ("first_png_result", "hybrid_handoff", "hybrid_semantic_continuation", "human_review_bundle", "human_review_template"):
            path = root / f"{name}.json"
            path.write_text(json.dumps({"name": name}), encoding="utf-8")
            evidence[name] = str(path)
        base = root / "base.png"
        hybrid = root / "hybrid.png"
        base.write_bytes(PNG + b"base")
        hybrid.write_bytes(PNG + b"hybrid")

        integrity = FirstGoldenReviewPacketIntegrity(root=root)
        sha = integrity._sha256
        packet = root / "packet.json"
        packet.write_text(json.dumps({
            "schema": "pul7sar-first-golden-human-review-packet-v2",
            "status": "FIRST_GOLDEN_CANDIDATE_READY_FOR_HUMAN_REVIEW",
            "branch": "phase18/story-intelligence",
            "candidate": 1,
            "cost_mode": "$0-local",
            "original_scene_runtime_admission": str(admission),
            "original_scene_runtime_admission_sha256": sha(admission),
            **evidence,
            "review_base_png": str(base),
            "review_hybrid_png": str(hybrid),
            "review_base_png_sha256": sha(base),
            "review_hybrid_png_sha256": sha(hybrid),
            "human_visual_review_required": True,
            "automatic_selection_performed": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }), encoding="utf-8")

        manifest = integrity.build_manifest(packet_path=packet)
        manifest_path = root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        decision = integrity.verify_manifest(manifest=manifest)
        self.assertTrue(decision.verified)
        verification = verification_payload(decision)
        verification_path = root / "verification.json"
        verification_path.write_text(json.dumps(verification), encoding="utf-8")
        sealed = root / "sealed.json"
        sealed.write_text(json.dumps({
            "schema": "pul7sar-first-golden-human-review-sealed-v1",
            "status": "FIRST_GOLDEN_CANDIDATE_READY_FOR_VERIFIED_HUMAN_REVIEW",
            "branch": "phase18/story-intelligence",
            "candidate": 1,
            "cost_mode": "$0-local",
            "integrity_manifest": str(manifest_path),
            "integrity_verification": str(verification_path),
            "manifest_sha256": decision.manifest_sha256,
            "human_visual_review_required": True,
            "automatic_selection_performed": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }), encoding="utf-8")
        return sealed, admission

    def test_template_binds_replay_verified_seal_and_original_scene(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sealed, _ = self._fixture(root)
            gate = SealedHumanApprovedGoldenReviewGate(root=root)
            gate._golden = _FakeGolden()
            payload = gate.build_template(
                sealed_packet_path=sealed,
                handoff_path="unused.json",
                continuation_path="unused.json",
                human_decision_path="unused.json",
            )
            self.assertTrue(payload["sealed_packet_verified"])
            self.assertTrue(payload["original_scene_runtime_admission_bound"])
            self.assertEqual(len(payload["sealed_packet_sha256"]), 64)
            self.assertFalse(payload["publication_ready"])

    def test_admission_tampering_after_seal_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sealed, admission = self._fixture(root)
            admission.write_text("{}", encoding="utf-8")
            gate = SealedHumanApprovedGoldenReviewGate(root=root)
            gate._golden = _FakeGolden()
            with self.assertRaisesRegex(RuntimeError, "MANIFEST_REPLAY_FAILED"):
                gate.build_template(
                    sealed_packet_path=sealed,
                    handoff_path="unused.json",
                    continuation_path="unused.json",
                    human_decision_path="unused.json",
                )

    def test_evaluate_requires_review_to_bind_same_seal(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sealed, _ = self._fixture(root)
            gate = SealedHumanApprovedGoldenReviewGate(root=root)
            gate._golden = _FakeGolden()
            template = gate.build_template(
                sealed_packet_path=sealed,
                handoff_path="unused.json",
                continuation_path="unused.json",
                human_decision_path="unused.json",
            )
            review = root / "review.json"
            review.write_text(json.dumps(template), encoding="utf-8")
            template["manifest_sha256"] = "0" * 64
            review.write_text(json.dumps(template), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "BINDING_MISMATCH:manifest_sha256"):
                gate.evaluate(
                    sealed_packet_path=sealed,
                    handoff_path="unused.json",
                    continuation_path="unused.json",
                    human_decision_path="unused.json",
                    review_path=review,
                    output_dir=root / "out",
                )

    def test_sealed_gate_never_self_authorizes_publication(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sealed, _ = self._fixture(root)
            gate = SealedHumanApprovedGoldenReviewGate(root=root)
            gate._golden = _FakeGolden()
            template = gate.build_template(
                sealed_packet_path=sealed,
                handoff_path="unused.json",
                continuation_path="unused.json",
                human_decision_path="unused.json",
            )
            review = root / "review.json"
            review.write_text(json.dumps(template), encoding="utf-8")
            result = gate.evaluate(
                sealed_packet_path=sealed,
                handoff_path="unused.json",
                continuation_path="unused.json",
                human_decision_path="unused.json",
                review_path=review,
                output_dir=root / "out",
            )
            self.assertTrue(result["golden_quality_approved"])
            self.assertFalse(result["publication_ready"])
            self.assertTrue(result["sealed_packet_verified"])


if __name__ == "__main__":
    unittest.main()
