import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from engine.intelligence.flux2_offload_capability import Flux2OffloadCapabilityProbe
import tools.phase18_preflight_flux2_offload as preflight


class _SequentialPipeline:
    def enable_sequential_cpu_offload(self):
        return None

    def enable_model_cpu_offload(self):
        return None


class _ModelOnlyPipeline:
    def enable_model_cpu_offload(self):
        return None


class _NoOffloadPipeline:
    pass


class Flux2OffloadCapabilityTests(unittest.TestCase):
    def test_low_vram_host_requires_and_accepts_sequential_offload(self):
        module = SimpleNamespace(Flux2KleinPipeline=_SequentialPipeline, __version__="0.test")
        report = Flux2OffloadCapabilityProbe(diffusers_module=module).inspect(total_vram_gb=14.6)
        self.assertTrue(report.ready)
        self.assertTrue(report.low_vram_host)
        self.assertTrue(report.sequential_cpu_offload_available)
        self.assertEqual(report.selected_safe_mode, "sequential_cpu")
        self.assertFalse(report.model_loaded)
        self.assertFalse(report.downloads_performed)
        self.assertFalse(report.publication_ready)

    def test_low_vram_model_only_pipeline_is_blocked(self):
        module = SimpleNamespace(Flux2KleinPipeline=_ModelOnlyPipeline, __version__="0.test")
        report = Flux2OffloadCapabilityProbe(diffusers_module=module).inspect(total_vram_gb=14.6)
        self.assertFalse(report.ready)
        self.assertIn("sequential_cpu_offload_required_on_low_vram_host", report.reasons)
        self.assertIsNone(report.selected_safe_mode)

    def test_high_vram_model_offload_is_safe_fallback(self):
        module = SimpleNamespace(Flux2KleinPipeline=_ModelOnlyPipeline, __version__="0.test")
        report = Flux2OffloadCapabilityProbe(diffusers_module=module).inspect(total_vram_gb=24.0)
        self.assertTrue(report.ready)
        self.assertFalse(report.low_vram_host)
        self.assertEqual(report.selected_safe_mode, "model_cpu")

    def test_missing_total_vram_fails_closed(self):
        module = SimpleNamespace(Flux2KleinPipeline=_SequentialPipeline, __version__="0.test")
        report = Flux2OffloadCapabilityProbe(diffusers_module=module).inspect(total_vram_gb=None)
        self.assertFalse(report.ready)
        self.assertIn("total_vram_unproven", report.reasons)

    def test_pipeline_without_offload_api_is_blocked(self):
        module = SimpleNamespace(Flux2KleinPipeline=_NoOffloadPipeline, __version__="0.test")
        report = Flux2OffloadCapabilityProbe(diffusers_module=module).inspect(total_vram_gb=24.0)
        self.assertFalse(report.ready)
        self.assertIn("no_supported_cpu_offload_mode", report.reasons)

    def test_preflight_receipt_is_zero_cost_and_has_no_execution_authority(self):
        with tempfile.TemporaryDirectory(dir=preflight.ROOT) as temp:
            root = Path(temp)
            host_path = root / "qualification.json"
            output = root / "offload.json"
            host_path.write_text(json.dumps({
                "eligible": True,
                "model_id": "black-forest-labs/FLUX.2-klein-4B",
                "runtime_kind": "local_cuda",
                "cuda_available": True,
                "bf16_supported": True,
                "cost_mode": "$0-local",
                "gpu_vram_gb": 24.0,
            }), encoding="utf-8")
            report = SimpleNamespace(
                ready=True,
                model_id="black-forest-labs/FLUX.2-klein-4B",
                diffusers_version="0.test",
                pipeline_available=True,
                sequential_cpu_offload_available=True,
                model_cpu_offload_available=True,
                total_vram_gb=24.0,
                model_offload_minimum_total_vram_gb=16.0,
                low_vram_host=False,
                selected_safe_mode="sequential_cpu",
                reasons=(),
            )
            with (
                patch.object(preflight, "_branch", return_value="phase18/story-intelligence"),
                patch.object(preflight, "Flux2OffloadCapabilityProbe") as probe_cls,
            ):
                probe_cls.return_value.inspect.return_value = report
                payload = preflight.run(host_receipt=host_path, output=output)
            self.assertTrue(output.is_file())
            self.assertEqual(payload["schema"], "pul7sar-phase18-flux2-offload-preflight-v1")
            self.assertEqual(payload["selected_safe_mode"], "sequential_cpu")
            self.assertFalse(payload["model_loaded"])
            self.assertFalse(payload["downloads_performed"])
            self.assertFalse(payload["generation_authorized"])
            self.assertFalse(payload["queue_mutated"])
            self.assertFalse(payload["png_created"])
            self.assertFalse(payload["semantic_approved"])
            self.assertFalse(payload["golden_quality_approved"])
            self.assertFalse(payload["publication_ready"])

    def test_preflight_rejects_host_identity_drift_before_probe(self):
        with tempfile.TemporaryDirectory(dir=preflight.ROOT) as temp:
            root = Path(temp)
            host_path = root / "qualification.json"
            host_path.write_text(json.dumps({
                "eligible": True,
                "model_id": "wrong/model",
                "runtime_kind": "local_cuda",
                "cuda_available": True,
                "bf16_supported": True,
                "cost_mode": "$0-local",
                "gpu_vram_gb": 24.0,
            }), encoding="utf-8")
            with (
                patch.object(preflight, "_branch", return_value="phase18/story-intelligence"),
                patch.object(preflight, "Flux2OffloadCapabilityProbe") as probe_cls,
            ):
                with self.assertRaisesRegex(RuntimeError, "MODEL_IDENTITY_DRIFT"):
                    preflight.run(host_receipt=host_path, output=root / "out.json")
                probe_cls.assert_not_called()


if __name__ == "__main__":
    unittest.main()
