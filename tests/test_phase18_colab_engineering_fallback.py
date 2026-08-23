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

    def test_engineering_proof_is_never_publication_ready(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            latest = root / "latest.json"
            base_png = root / "base.png"
            hybrid_dir = root / "hybrid"
            base_png.write_bytes(b"fake-png")
            latest.write_text(json.dumps({
                "manifest_version": "pul7sar-golden-batch-v5",
                "hybrid_surface_replacement_required": True,
                "png": str(base_png),
            }), encoding="utf-8")

            receipt = SimpleNamespace(
                generated_pitch_markings_replaced=True,
                surface_opacity=255,
                input_sha256="a" * 64,
                output_sha256="b" * 64,
            )
            integrity = SimpleNamespace(valid=True, failures=())

            class FakeComposer:
                def compose_file(self, **kwargs):
                    Path(kwargs["output_path"]).write_bytes(b"hybrid")
                    return receipt

            class FakeIntegrityGate:
                def validate_football(self, value):
                    if value is not receipt:
                        raise AssertionError("unexpected receipt")
                    return integrity

            with (
                patch.object(one_command, "LATEST", latest),
                patch.object(one_command, "HYBRID_DIR", hybrid_dir),
                patch.object(one_command, "FootballHybridComposer", return_value=FakeComposer()),
                patch.object(one_command, "HybridArtifactIntegrityGate", return_value=FakeIntegrityGate()),
                patch.object(one_command, "_display", return_value=False),
            ):
                payload = one_command._compose_engineering_proof(1, semantic_blocker="qwen inference failed")

            self.assertEqual(payload["status"], "GOLDEN_HYBRID_ENGINEERING_PROOF")
            self.assertFalse(payload["publication_ready"])
            self.assertFalse(payload["visual_inspection"]["automatic_visual_qa_ready"])
            self.assertFalse(payload["visual_inspection"]["publication_visual_gate_ready"])
            self.assertFalse(payload["hybrid_quality"]["approved"])
            self.assertEqual(payload["semantic_visual_inspection"]["status"], "SEMANTIC_QA_BLOCKED")


if __name__ == "__main__":
    unittest.main()
