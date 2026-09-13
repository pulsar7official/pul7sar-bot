import unittest

from engine.intelligence.local_backend import LocalBackendKind, LocalBackendReadinessGate, LocalBackendSnapshot
from engine.intelligence.local_generation_provenance import LocalGenerationProvenance
from engine.intelligence.local_runtime import RuntimeHardwareSnapshot, RuntimeKind
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


class LocalBackendTests(unittest.TestCase):
    def runtime(self, *, cuda=True, vram=16.0):
        return RuntimeHardwareSnapshot(
            kind=RuntimeKind.LOCAL_CUDA if cuda else RuntimeKind.LOCAL_CPU,
            torch_available=True,
            cuda_available=cuda,
            gpu_name="test-gpu" if cuda else None,
            gpu_vram_gb=vram if cuda else None,
        )

    def test_diffusers_ready_when_runtime_and_backend_are_ready(self):
        decision = LocalBackendReadinessGate().evaluate(
            model=FLUX2_KLEIN_4B_LOCAL,
            runtime=self.runtime(),
            backend=LocalBackendSnapshot(LocalBackendKind.DIFFUSERS, True, version="0.test"),
        )
        self.assertTrue(decision.ready)

    def test_missing_backend_fails_closed(self):
        decision = LocalBackendReadinessGate().evaluate(
            model=FLUX2_KLEIN_4B_LOCAL,
            runtime=self.runtime(),
            backend=LocalBackendSnapshot(LocalBackendKind.DIFFUSERS, False),
        )
        self.assertFalse(decision.ready)
        self.assertTrue(any("unavailable" in item for item in decision.failures))

    def test_insufficient_vram_fails_closed(self):
        decision = LocalBackendReadinessGate().evaluate(
            model=FLUX2_KLEIN_4B_LOCAL,
            runtime=self.runtime(vram=8.0),
            backend=LocalBackendSnapshot(LocalBackendKind.DIFFUSERS, True, version="0.test"),
        )
        self.assertFalse(decision.ready)

    def test_comfyui_requires_explicit_local_endpoint(self):
        decision = LocalBackendReadinessGate().evaluate(
            model=FLUX2_KLEIN_4B_LOCAL,
            runtime=self.runtime(),
            backend=LocalBackendSnapshot(LocalBackendKind.COMFYUI, True),
        )
        self.assertFalse(decision.ready)
        self.assertIn("ComfyUI backend requires an explicit local endpoint", decision.failures)

    def test_provenance_preserves_seed_and_request(self):
        provenance = LocalGenerationProvenance(
            provider_id="local-flux",
            model_id=FLUX2_KLEIN_4B_LOCAL.model_id,
            backend="diffusers",
            seed=712345,
            request_id="local-001",
            width=1080,
            height=1920,
        )
        data = provenance.as_provider_metadata()
        self.assertEqual(data["seed"], 712345)
        self.assertEqual(data["request_id"], "local-001")
        self.assertEqual(data["model"], FLUX2_KLEIN_4B_LOCAL.model_id)


if __name__ == "__main__":
    unittest.main()
