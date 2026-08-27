import unittest
from pathlib import Path

from engine.intelligence.approved_model_revisions import FLUX2_KLEIN_4B_MODEL_ID
from tools.phase18_colab_first_genuine_offload_locked import _validate_host, _validate_offload


class FirstGenuineGoldenV6OffloadLockTests(unittest.TestCase):
    def _host(self, *, total_vram: float = 14.6) -> dict[str, object]:
        return {
            "eligible": True,
            "model_id": FLUX2_KLEIN_4B_MODEL_ID,
            "gpu_name": "NVIDIA Test GPU",
            "gpu_vram_gb": total_vram,
            "gpu_free_vram_gb": total_vram,
            "bf16_supported": True,
            "compute_capability": "8.0",
            "torch_available": True,
            "cuda_available": True,
            "runtime_kind": "local_cuda",
            "required_vram_gb": 13.0,
            "cost_mode": "$0-local",
        }

    def _offload(self, *, total_vram: float = 14.6, selected: str = "sequential_cpu") -> dict[str, object]:
        low = total_vram <= 16.0
        return {
            "schema": "pul7sar-phase18-flux2-offload-preflight-v1",
            "branch": "phase18/story-intelligence",
            "ready": True,
            "model_id": FLUX2_KLEIN_4B_MODEL_ID,
            "diffusers_version": "0.35.2",
            "pipeline_available": True,
            "sequential_cpu_offload_available": True,
            "model_cpu_offload_available": True,
            "gpu_vram_gb": total_vram,
            "model_offload_minimum_total_vram_gb": 16.0,
            "low_vram_host": low,
            "selected_safe_mode": selected,
            "reasons": [],
            "cost_mode": "$0-local",
            "model_loaded": False,
            "downloads_performed": False,
            "generation_authorized": False,
            "queue_mutated": False,
            "png_created": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }

    def test_low_vram_host_requires_sequential_offload(self):
        host = self._host(total_vram=14.6)
        _validate_host(host)
        _validate_offload(self._offload(total_vram=14.6, selected="sequential_cpu"), host)

        unsafe = self._offload(total_vram=14.6, selected="model_cpu")
        with self.assertRaisesRegex(RuntimeError, "LOW_VRAM_SEQUENTIAL_NOT_PROVEN"):
            _validate_offload(unsafe, host)

    def test_high_vram_host_may_use_verified_model_cpu_fallback(self):
        host = self._host(total_vram=24.0)
        offload = self._offload(total_vram=24.0, selected="model_cpu")
        offload["low_vram_host"] = False
        _validate_host(host)
        _validate_offload(offload, host)

    def test_authority_drift_is_rejected(self):
        host = self._host()
        offload = self._offload()
        offload["generation_authorized"] = True
        with self.assertRaisesRegex(RuntimeError, "AUTHORITY_DRIFT:generation_authorized"):
            _validate_offload(offload, host)

    def test_total_vram_must_match_qualification_receipt(self):
        host = self._host(total_vram=14.6)
        offload = self._offload(total_vram=24.0)
        offload["low_vram_host"] = False
        with self.assertRaisesRegex(RuntimeError, "TOTAL_VRAM_HOST_DRIFT"):
            _validate_offload(offload, host)

    def test_wrapper_orders_offload_before_resource_model_work(self):
        text = Path("tools/phase18_colab_first_genuine_offload_locked.py").read_text(encoding="utf-8")
        qualify = text.index("phase18_qualify_gpu_host.py")
        offload = text.index("phase18_preflight_flux2_offload.py")
        inner = text.index("phase18_colab_first_genuine_resources_locked.py")
        self.assertLess(qualify, offload)
        self.assertLess(offload, inner)
        self.assertIn("pul7sar-first-genuine-golden-v6-offload-lock-v1", text)
        self.assertIn("FIRST_GENUINE_GOLDEN_V6_PREMODEL_OFFLOAD_RESOURCE_LOCK_VERIFIED", text)
        self.assertIn('"human_visual_review_approved": False', text)
        self.assertIn('"golden_quality_approved": False', text)
        self.assertIn('"publication_ready": False', text)
        self.assertIn('"seeds_2_to_4_authorized": False', text)


if __name__ == "__main__":
    unittest.main()
