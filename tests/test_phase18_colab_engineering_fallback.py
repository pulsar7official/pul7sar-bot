import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import tools.phase18_colab_bootstrap as bootstrap
import tools.phase18_colab_one_command as one_command


class ColabEngineeringFallbackTests(unittest.TestCase):
    def test_bootstrap_semantic_probe_failure_is_nonfatal(self):
        completed = SimpleNamespace(returncode=1)
        with patch.object(bootstrap, "_run", return_value=completed):
            self.assertFalse(bootstrap._fresh_process_probe())

    def test_bootstrap_cuda_failure_remains_fatal(self):
        completed = SimpleNamespace(returncode=2)
        with patch.object(bootstrap, "_run", return_value=completed):
            with self.assertRaisesRegex(RuntimeError, "CUDA_NOT_AVAILABLE"):
                bootstrap._fresh_process_probe()

    def test_engineering_proof_is_never_publication_ready_and_never_adds_pitch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            latest = root / "latest.json"
            base_png = root / "base.png"
            proof_dir = root / "editorial"
            base_png.write_bytes(b"fake-png")
            latest.write_text(json.dumps({
                "manifest_version": "pul7sar-golden-batch-v6",
                "benchmark": "golden-visual-season-opener-editorial-v6",
                "visual_grammar_surface_visibility": "context_only",
                "hybrid_surface_replacement_required": False,
                "football_camera_preset": "editorial_environmental_oblique",
                "focal_anchor": one_command.EXPECTED_FOCAL_ANCHOR,
                "copy_negative_space": one_command.EXPECTED_COPY_NEGATIVE_SPACE,
                "brand_quiet_zone": one_command.EXPECTED_BRAND_QUIET_ZONE,
                "png": str(base_png),
            }), encoding="utf-8")

            with (
                patch.object(one_command, "LATEST", latest),
                patch.object(one_command, "PROOF_DIR", proof_dir),
                patch.object(one_command, "_display", return_value=False),
            ):
                payload = one_command._engineering_proof(1, semantic_blocker="qwen inference failed")

            self.assertEqual(payload["status"], "GOLDEN_EDITORIAL_ENGINEERING_PROOF")
            self.assertFalse(payload["publication_ready"])
            self.assertFalse(payload["deterministic_pitch_applied"])
            self.assertFalse(payload["pitch_replacement_required"])
            self.assertEqual(payload["visual_grammar_surface_visibility"], "context_only")
            self.assertEqual(payload["focal_anchor"], one_command.EXPECTED_FOCAL_ANCHOR)
            self.assertEqual(payload["copy_negative_space"], one_command.EXPECTED_COPY_NEGATIVE_SPACE)
            self.assertEqual(payload["brand_quiet_zone"], one_command.EXPECTED_BRAND_QUIET_ZONE)
            self.assertEqual(payload["semantic_visual_inspection"]["status"], "SEMANTIC_QA_BLOCKED")
            self.assertTrue((proof_dir / "candidate-01-golden-editorial-v6-engineering-receipt.json").is_file())


if __name__ == "__main__":
    unittest.main()
