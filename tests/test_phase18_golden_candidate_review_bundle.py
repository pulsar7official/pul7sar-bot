import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.golden_candidate_review_bundle import GoldenCandidateReviewBundleBuilder


class GoldenCandidateReviewBundleTests(unittest.TestCase):
    def _write_fixture(self, root: Path, *, candidate: int = 1, publication_ready: bool = False):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")

        base = root / "output" / "proof.png"
        base.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (640, 800), (31, 77, 42)).save(base)
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
        }
        summary.write_text(json.dumps(payload), encoding="utf-8")
        return summary, base

    def test_builds_cpu_review_bundle_without_mutating_genuine_base(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            summary, base = self._write_fixture(root)
            before = base.read_bytes()
            payload = GoldenCandidateReviewBundleBuilder().build(
                repository_root=str(root),
                summary_path=str(summary),
                output_dir=str(root / "output" / "review"),
                expected_candidate=1,
            )
            self.assertEqual(payload["status"], "GOLDEN_CANDIDATE_REVIEW_BUNDLE_READY")
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
            summary, _ = self._write_fixture(root, candidate=2)
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
            summary, _ = self._write_fixture(root, publication_ready=True)
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
            summary, _ = self._write_fixture(root)
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

    def test_rejects_repository_path_escape(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            summary, _ = self._write_fixture(root)
            with self.assertRaisesRegex(RuntimeError, "ESCAPES_REPOSITORY"):
                GoldenCandidateReviewBundleBuilder().build(
                    repository_root=str(root),
                    summary_path=str(summary),
                    output_dir=str(Path(outside) / "review"),
                    expected_candidate=1,
                )


if __name__ == "__main__":
    unittest.main()
