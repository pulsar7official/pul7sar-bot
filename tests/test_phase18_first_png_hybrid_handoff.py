import hashlib
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.first_png_hybrid_handoff import (
    EXPECTED_STATUS,
    FirstPngHybridHandoffBuilder,
)
from engine.intelligence.golden_smoke import GoldenSmokeCandidate


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FirstPngHybridHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.png = self.root / "candidate.png"
        self.executor = self.root / "executor.json"
        self.metadata = self.root / "metadata.json"
        self.png.write_bytes(b"\x89PNG\r\n\x1a\nreal-golden-bytes")
        self.executor.write_text('{"status":"REAL_VISUAL_PROOF_GENERATED"}', encoding="utf-8")
        self.metadata.write_text('{"proof":"locked"}', encoding="utf-8")
        self.candidate = GoldenSmokeCandidate(
            manifest_path=self.root / "manifest.json",
            handoff_path=self.root / "candidate-01.json",
            candidate=1,
            seed=7007001,
            request_id="golden-general-season-opener-v5-001",
            payload_sha256="a" * 64,
            provider_id="local-diffusers",
            model_id="black-forest-labs/FLUX.2-klein-4B",
        )
        self.manifest = {
            "manifest_version": "pul7sar-golden-batch-v5",
            "benchmark": "golden-hybrid-v5",
            "composition_grammar": "single_continuous_scene",
            "sport_geometry": "deterministic_football_pitch_projective_v1",
            "generated_sport_geometry_allowed": False,
            "hybrid_surface_replacement_required": True,
            "football_camera_preset": "high_wide_central",
            "generated_branding_allowed": False,
            "brand_composition_policy": "dynamic_deterministic_after_generation",
            "cost_mode": "$0-local",
        }
        self.postflight = {
            "status": "FIRST_GOLDEN_PNG_PROVENANCE_POSTFLIGHT_VERIFIED",
            "candidate": 1,
            "request_id": self.candidate.request_id,
            "seed": self.candidate.seed,
            "model_id": self.candidate.model_id,
            "payload_sha256": self.candidate.payload_sha256,
            "cost_mode": "$0-local",
            "resolved_dtype": "bfloat16",
            "png": str(self.png),
            "png_sha256": sha256(self.png),
            "executor_result": str(self.executor),
            "executor_result_sha256": sha256(self.executor),
            "proof_metadata": str(self.metadata),
            "proof_metadata_sha256": sha256(self.metadata),
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }

    def tearDown(self):
        self.temp.cleanup()

    def build(self):
        return FirstPngHybridHandoffBuilder().build(
            repository_root=self.root,
            candidate=self.candidate,
            manifest=self.manifest,
            postflight=self.postflight,
            branch="phase18/story-intelligence",
        )

    def test_builds_handoff_for_exact_provenance_locked_bytes(self):
        payload = self.build()
        self.assertEqual(payload["status"], EXPECTED_STATUS)
        self.assertEqual(payload["base_png_sha256"], sha256(self.png))
        self.assertEqual(payload["png"], str(self.png))
        self.assertTrue(payload["hybrid_surface_replacement_required"])
        self.assertFalse(payload["semantic_layer_gate_approved"])
        self.assertFalse(payload["hybrid_semantic_review_approved"])
        self.assertFalse(payload["golden_quality_approved"])
        self.assertFalse(payload["publication_ready"])

    def test_rejects_postflight_authority_drift(self):
        self.postflight["semantic_approved"] = True
        with self.assertRaisesRegex(RuntimeError, "POSTFLIGHT_DRIFT"):
            self.build()

    def test_rejects_png_tampering_after_postflight(self):
        self.png.write_bytes(self.png.read_bytes() + b"tampered")
        with self.assertRaisesRegex(RuntimeError, "PNG_SHA256_MISMATCH"):
            self.build()

    def test_rejects_executor_tampering_after_postflight(self):
        self.executor.write_text('{"status":"changed"}', encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "EXECUTOR_SHA256_MISMATCH"):
            self.build()

    def test_rejects_stale_golden_manifest_contract(self):
        self.manifest["manifest_version"] = "pul7sar-golden-batch-v4"
        with self.assertRaisesRegex(RuntimeError, "MANIFEST_DRIFT"):
            self.build()

    def test_rejects_main_branch(self):
        with self.assertRaisesRegex(RuntimeError, "BRANCH_BLOCKED"):
            FirstPngHybridHandoffBuilder().build(
                repository_root=self.root,
                candidate=self.candidate,
                manifest=self.manifest,
                postflight=self.postflight,
                branch="main",
            )


if __name__ == "__main__":
    unittest.main()
