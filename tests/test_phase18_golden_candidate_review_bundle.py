import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.approved_model_revisions import FLUX2_KLEIN_4B_REVISION
from engine.intelligence.golden_candidate_review_bundle import GoldenCandidateReviewBundleBuilder


class GoldenCandidateReviewBundleTests(unittest.TestCase):
    def _write_fixture(self, root: Path, *, candidate: int = 1, publication_ready: bool = False):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")

        base = root / "output" / "phase18_visual_proof" / "proof.png"
        base.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (640, 800), (31, 77, 42)).save(base)
        metadata = base.with_suffix(".json")
        metadata.write_text(json.dumps({
            "provider": "local-flux2-klein-4b",
            "model": "black-forest-labs/FLUX.2-klein-4B",
            "model_revision": FLUX2_KLEIN_4B_REVISION,
            "backend": "diffusers",
            "seed": 7007001,
            "request_id": "golden-hybrid-v5-001",
            "width": 640,
            "height": 800,
            "output_ref": str(base),
            "visual_proof": True,
            "cost_mode": "$0-local",
        }), encoding="utf-8")
        executor = root / "output" / "phase18_visual_proof" / f"colab-candidate-{candidate:02d}-result.json"
        executor.write_text(json.dumps({
            "status": "REAL_VISUAL_PROOF_GENERATED",
            "png": str(base),
            "metadata": str(metadata),
            "request_id": "golden-hybrid-v5-001",
            "seed": 7007001,
            "model_id": "black-forest-labs/FLUX.2-klein-4B",
            "payload_sha256": "a" * 64,
            "resolved_dtype": "bfloat16",
            "cost_mode": "$0-local",
        }), encoding="utf-8")
        summary = root / "output" / "phase18_colab" / "latest.json"
        summary.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "status": "COLAB_REAL_HYBRID_BASE_GENERATED",
            "branch": "phase18/story-intelligence",
            "manifest_version": "pul7sar-golden-batch-v5",
            "candidate": candidate,
            "seed": 7007001,
            "request_id": "golden-hybrid-v5-001",
            "payload_sha256": "a" * 64,
            "model_id": "black-forest-labs/FLUX.2-klein-4B",
            "generated_branding_allowed": False,
            "generated_sport_geometry_allowed": False,
            "hybrid_surface_replacement_required": True,
            "publication_ready": publication_ready,
            "png": str(base),
            "executor_result": str(executor),
        }
        summary.write_text(json.dumps(payload), encoding="utf-8")
        return summary, base, metadata, executor

    def test_builds_cpu_review_bundle_without_mutating_genuine_base(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            summary, base, metadata, executor = self._write_fixture(root)
            before = base.read_bytes()
            payload = GoldenCandidateReviewBundleBuilder().build(
                repository_root=str(root),
                summary_path=str(summary),
                output_dir=str(root / "output" / "review"),
                expected_candidate=1,
            )
            self.assertEqual(payload["status"], "GOLDEN_CANDIDATE_REVIEW_BUNDLE_READY")
            self.assertEqual(payload["generation_provenance_status"], "GENERATION_PROVENANCE_LOCK_VERIFIED")
            self.assertEqual(payload["resolved_dtype"], "bfloat16")
            self.assertEqual(payload["cost_mode"], "$0-local")
            self.assertEqual(len(payload["executor_result_sha256"]), 64)
            self.assertEqual(len(payload["proof_metadata_sha256"]), 64)
            self.assertEqual(Path(payload["executor_result"]), executor.resolve())
            self.assertEqual(Path(payload["proof_metadata"]), metadata.resolve())
            self.assertEqual(payload["pitch_variant_count"], 3)
            self.assertTrue(payload["candidate_pixels_untouched"])
            self.assertFalse(payload["semantic_layer_gate_approved"])
            self.assertFalse(payload["golden_quality_approved"])
            self.assertFalse(payload["publication_ready"])
            self.assertEqual(base.read_bytes(), before)
            self.assertTrue(Path(payload["manifest"]).is_file())
            self.assertTrue(Path(payload["pitch_diagnostics_manifest"]).is_file())

    def test_rejects_candidate_identity_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            summary, _, _, _ = self._write_fixture(root, candidate=2)
            with self.assertRaisesRegex(RuntimeError, "CANDIDATE_MISMATCH"):
                GoldenCandidateReviewBundleBuilder().build(
                    repository_root=str(root),
                    summary_path=str(summary),
                    output_dir=str(root / "output" / "review"),
                    expected_candidate=1,
                )

    def test_rejects_publication_ready_input(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            summary, _, _, _ = self._write_fixture(root, publication_ready=True)
            with self.assertRaisesRegex(RuntimeError, "PUBLICATION_READY"):
                GoldenCandidateReviewBundleBuilder().build(
                    repository_root=str(root),
                    summary_path=str(summary),
                    output_dir=str(root / "output" / "review"),
                    expected_candidate=1,
                )

    def test_rejects_stale_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            summary, _, _, _ = self._write_fixture(root)
            payload = json.loads(summary.read_text(encoding="utf-8"))
            payload["manifest_version"] = "pul7sar-golden-batch-v4"
            summary.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "STALE_MANIFEST"):
                GoldenCandidateReviewBundleBuilder().build(
                    repository_root=str(root),
                    summary_path=str(summary),
                    output_dir=str(root / "output" / "review"),
                    expected_candidate=1,
                )

    def test_rejects_executor_provenance_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            summary, _, _, executor = self._write_fixture(root)
            data = json.loads(executor.read_text(encoding="utf-8"))
            data["resolved_dtype"] = "float16"
            executor.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "DTYPE_DRIFT"):
                GoldenCandidateReviewBundleBuilder().build(
                    repository_root=str(root),
                    summary_path=str(summary),
                    output_dir=str(root / "output" / "review"),
                    expected_candidate=1,
                )

    def test_rejects_repository_path_escape(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            summary, _, _, _ = self._write_fixture(root)
            with self.assertRaisesRegex(RuntimeError, "ESCAPES_REPOSITORY"):
                GoldenCandidateReviewBundleBuilder().build(
                    repository_root=str(root),
                    summary_path=str(summary),
                    output_dir=str(Path(outside) / "review"),
                    expected_candidate=1,
                )


if __name__ == "__main__":
    unittest.main()
