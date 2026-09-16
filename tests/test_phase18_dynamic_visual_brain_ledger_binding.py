import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.dynamic_visual_brain_ledger_binding import (
    DynamicVisualBrainLedgerBindingGate,
)
from engine.intelligence.dynamic_visual_brain_queue_critic_binding import (
    DynamicVisualBrainQueueCriticBindingGate,
)
from engine.intelligence.visual_benchmark_suite import PHASE18_VISUAL_BENCHMARKS
from engine.intelligence.visual_validation_ledger import (
    build_canonical_visual_validation_ledger,
    validate_visual_validation_ledger,
)


class DynamicVisualBrainLedgerBindingTests(unittest.TestCase):
    def _benchmark_id(self):
        return PHASE18_VISUAL_BENCHMARKS[0].benchmark_id

    def _checks(self):
        return {
            "factual_integrity_passed": True,
            "identity_integrity_passed": True,
            "sentiment_neutrality_passed": True,
            "sport_geometry_passed": True,
            "protected_zones_passed": True,
            "platform_crop_passed": True,
            "semantic_qa_passed": True,
            "provenance_passed": False,
        }

    def _binding_payload(self, png_sha, *, critic_approved=True, critic_rejections=None):
        return {
            "contract": DynamicVisualBrainQueueCriticBindingGate.CONTRACT,
            "status": DynamicVisualBrainQueueCriticBindingGate.STATUS,
            "branch": "phase18/story-intelligence",
            "job_id": "dynamic-job-1",
            "job_state": "succeeded",
            "job_attempt": 1,
            "request_id": "dynamic-request-1",
            "seed": 1087,
            "provider_id": "local_diffusers",
            "model_id": "black-forest-labs/FLUX.2-klein-4B",
            "cost_mode": "$0-local",
            "story_fingerprint": "story-fingerprint-1",
            "competition_sha256": "1" * 64,
            "selected_concept_id": "dynamic-preview-tunnel",
            "selected_concept_sha256": "2" * 64,
            "renderer_prompt_sha256": "3" * 64,
            "original_scene_request_sha256": "4" * 64,
            "handoff_payload_sha256": "5" * 64,
            "queue_binding_sha256": "6" * 64,
            "durable_job_sha256": "7" * 64,
            "handoff_file_sha256": "8" * 64,
            "generation_result_sha256": "9" * 64,
            "critic_binding_sha256": "a" * 64,
            "png_sha256": png_sha,
            "critic_approved": critic_approved,
            "critic_rejections": critic_rejections or [],
            "semantic_inspection_required": True,
            "human_visual_review_required": True,
            "golden_quality_approved": False,
            "publication_ready": False,
        }

    def _make_bound(self, root, *, critic_approved=True, critic_rejections=None):
        png = root / "output" / "candidate.png"
        png.parent.mkdir(parents=True, exist_ok=True)
        png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"dynamic-candidate")
        import hashlib
        digest = hashlib.sha256(png.read_bytes()).hexdigest()
        binding = root / "output" / "queue-critic.json"
        binding.write_text(json.dumps(self._binding_payload(
            digest,
            critic_approved=critic_approved,
            critic_rejections=critic_rejections,
        )), encoding="utf-8")
        receipt = DynamicVisualBrainLedgerBindingGate.verify(
            benchmark_id=self._benchmark_id(),
            queue_critic_binding_path="output/queue-critic.json",
            candidate_png_path="output/candidate.png",
            repository_root=str(root),
        )
        return png, binding, receipt

    def test_exact_durable_critic_png_is_bound_for_ledger_without_publication_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, _, receipt = self._make_bound(root)
            payload = receipt.to_dict()
            self.assertEqual(payload["contract"], DynamicVisualBrainLedgerBindingGate.CONTRACT)
            self.assertTrue(payload["critic_approved"])
            self.assertTrue(payload["provenance_passed"])
            self.assertTrue(payload["human_visual_review_required"])
            self.assertFalse(payload["golden_quality_approved"])
            self.assertFalse(payload["publication_ready"])

    def test_png_tampering_after_queue_critic_binding_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            png, binding, _ = self._make_bound(root)
            png.write_bytes(png.read_bytes() + b"tamper")
            with self.assertRaisesRegex(ValueError, "PNG_SHA_DRIFT"):
                DynamicVisualBrainLedgerBindingGate.verify(
                    benchmark_id=self._benchmark_id(),
                    queue_critic_binding_path=str(binding.relative_to(root)),
                    candidate_png_path=str(png.relative_to(root)),
                    repository_root=str(root),
                )

    def test_accepted_ledger_review_requires_critic_approval_and_injects_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, _, receipt = self._make_bound(root)
            ledger = build_canonical_visual_validation_ledger()
            updated = DynamicVisualBrainLedgerBindingGate.record_review(
                ledger,
                binding=receipt.to_dict(),
                status="accepted",
                checks=self._checks(),
                owner_visual_accepted=True,
                golden_quality_score=9.1,
            )
            case = next(item for item in updated["cases"] if item["benchmark_id"] == self._benchmark_id())
            self.assertTrue(case["checks"]["provenance_passed"])
            self.assertEqual(case["candidate"]["sha256"], receipt.png_sha256)
            self.assertFalse(updated["publication_ready"])
            validate_visual_validation_ledger(updated)

    def test_critic_rejection_can_be_recorded_as_rejected_but_never_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, _, receipt = self._make_bound(
                root,
                critic_approved=False,
                critic_rejections=["broken_sport_surface_geometry"],
            )
            ledger = build_canonical_visual_validation_ledger()
            with self.assertRaisesRegex(ValueError, "CRITIC_APPROVAL_REQUIRED"):
                DynamicVisualBrainLedgerBindingGate.record_review(
                    ledger,
                    binding=receipt.to_dict(),
                    status="accepted",
                    checks=self._checks(),
                    owner_visual_accepted=True,
                    golden_quality_score=9.9,
                )
            updated = DynamicVisualBrainLedgerBindingGate.record_review(
                ledger,
                binding=receipt.to_dict(),
                status="rejected",
                checks=self._checks(),
                owner_visual_accepted=False,
                golden_quality_score=7.0,
                hard_blockers=("broken_sport_surface_geometry",),
                rejection_reasons=("visual critic rejected the generated geometry",),
            )
            summary = validate_visual_validation_ledger(updated)
            self.assertEqual(summary["rejected"], 1)
            self.assertFalse(summary["publication_ready"])

    def test_candidate_outside_repository_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            other = Path(outside) / "candidate.png"
            other.write_bytes(b"\x89PNG\r\n\x1a\n" + b"outside")
            import hashlib
            digest = hashlib.sha256(other.read_bytes()).hexdigest()
            binding = root / "binding.json"
            binding.write_text(json.dumps(self._binding_payload(digest)), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "CANDIDATE_PNG_OUTSIDE_REPOSITORY"):
                DynamicVisualBrainLedgerBindingGate.verify(
                    benchmark_id=self._benchmark_id(),
                    queue_critic_binding_path="binding.json",
                    candidate_png_path=str(other),
                    repository_root=str(root),
                )


if __name__ == "__main__":
    unittest.main()
