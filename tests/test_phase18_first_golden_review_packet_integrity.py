import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.first_golden_review_packet_integrity import (
    FirstGoldenReviewPacketIntegrity,
    verification_payload,
)

PNG = b"\x89PNG\r\n\x1a\n" + b"review-bytes"


class FirstGoldenReviewPacketIntegrityTests(unittest.TestCase):
    def _fixture(self, root: Path):
        output = root / "output" / "phase18_gpu_smoke"
        output.mkdir(parents=True, exist_ok=True)
        review = root / "output" / "phase18_visual_proof" / "hybrid-human-review" / "candidate-01"
        review.mkdir(parents=True, exist_ok=True)

        file_fields = {
            "first_png_result": output / "first-png-result.json",
            "hybrid_handoff": output / "first-png-hybrid-handoff.json",
            "hybrid_semantic_continuation": output / "hybrid-semantic-continuation.json",
            "human_review_bundle": output / "hybrid-human-review-bundle.json",
            "human_review_template": output / "hybrid-human-review-template.json",
            "review_base_png": review / "01-proven-base.png",
            "review_hybrid_png": review / "02-semantic-approved-hybrid.png",
        }
        for field, path in file_fields.items():
            if field.startswith("review_"):
                path.write_bytes(PNG + field.encode("utf-8"))
            else:
                path.write_text(json.dumps({"field": field}), encoding="utf-8")

        integrity = FirstGoldenReviewPacketIntegrity(root=root)
        packet = {
            "schema": "pul7sar-first-golden-human-review-packet-v1",
            "status": "FIRST_GOLDEN_CANDIDATE_READY_FOR_HUMAN_REVIEW",
            "branch": "phase18/story-intelligence",
            "candidate": 1,
            "cost_mode": "$0-local",
            **{key: str(value) for key, value in file_fields.items()},
            "review_base_png_sha256": integrity._sha256(file_fields["review_base_png"]),
            "review_hybrid_png_sha256": integrity._sha256(file_fields["review_hybrid_png"]),
            "human_visual_review_required": True,
            "automatic_selection_performed": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        packet_path = output / "first-golden-human-review-packet.json"
        packet_path.write_text(json.dumps(packet), encoding="utf-8")
        return integrity, packet_path, file_fields

    def test_clean_packet_is_sealed_and_replay_verified(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            integrity, packet_path, file_fields = self._fixture(root)
            manifest = integrity.build_manifest(packet_path=packet_path)
            self.assertEqual(manifest["status"], "FIRST_GOLDEN_REVIEW_PACKET_SEALED")
            self.assertEqual(len(manifest["files"]), 7)
            self.assertFalse(manifest["publication_ready"])
            self.assertFalse(manifest["golden_quality_approved"])
            self.assertFalse(manifest["human_visual_review_approved"])
            self.assertFalse(manifest["seeds_2_to_4_authorized"])
            self.assertEqual(
                {item["path"] for item in manifest["files"]},
                {str(path.resolve()) for path in file_fields.values()},
            )
            decision = integrity.verify_manifest(manifest=manifest)
            self.assertTrue(decision.verified)
            self.assertEqual(decision.failures, ())
            payload = verification_payload(decision)
            self.assertEqual(payload["status"], "FIRST_GOLDEN_REVIEW_PACKET_INTEGRITY_VERIFIED")
            self.assertFalse(payload["publication_ready"])

    def test_receipt_tampering_after_seal_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            integrity, packet_path, file_fields = self._fixture(root)
            manifest = integrity.build_manifest(packet_path=packet_path)
            file_fields["human_review_template"].write_text("tampered", encoding="utf-8")
            decision = integrity.verify_manifest(manifest=manifest)
            self.assertFalse(decision.verified)
            self.assertIn("human_review_template_sha256_mismatch", decision.failures)

    def test_review_png_tampering_after_seal_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            integrity, packet_path, file_fields = self._fixture(root)
            manifest = integrity.build_manifest(packet_path=packet_path)
            file_fields["review_hybrid_png"].write_bytes(PNG + b"changed")
            decision = integrity.verify_manifest(manifest=manifest)
            self.assertFalse(decision.verified)
            self.assertIn("review_hybrid_png_sha256_mismatch", decision.failures)

    def test_packet_cannot_claim_human_golden_or_publication_authority(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            integrity, packet_path, _ = self._fixture(root)
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            for field in ("human_visual_review_approved", "golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized"):
                poisoned = dict(packet)
                poisoned[field] = True
                packet_path.write_text(json.dumps(poisoned), encoding="utf-8")
                with self.subTest(field=field):
                    with self.assertRaisesRegex(RuntimeError, "AUTHORITY_DRIFT"):
                        integrity.build_manifest(packet_path=packet_path)
                packet_path.write_text(json.dumps(packet), encoding="utf-8")

    def test_manifest_digest_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            integrity, packet_path, _ = self._fixture(root)
            manifest = integrity.build_manifest(packet_path=packet_path)
            manifest["candidate"] = 2
            decision = integrity.verify_manifest(manifest=manifest)
            self.assertFalse(decision.verified)
            self.assertIn("candidate_mismatch", decision.failures)
            self.assertIn("manifest_sha256_mismatch", decision.failures)

    def test_evidence_path_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            integrity, packet_path, _ = self._fixture(root)
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            external = Path(outside) / "outside.json"
            external.write_text("{}", encoding="utf-8")
            packet["human_review_template"] = str(external)
            packet_path.write_text(json.dumps(packet), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "ESCAPES_REPOSITORY"):
                integrity.build_manifest(packet_path=packet_path)


if __name__ == "__main__":
    unittest.main()
