import unittest

from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.local_backend_execution import (
    LocalBackendGenerationResult, LocalBackendRequestCompiler, LocalBackendResultGate,
)
from engine.intelligence.local_readiness_report import LocalGenerationReadinessReport
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


class LocalBackendExecutionTests(unittest.TestCase):
    def setUp(self):
        self.package = GenerationPackage(
            platform="instagram_story",
            canvas="1080x1920",
            scene_prompt="premium sports editorial scene",
            negative_constraints=("no humiliation", "no fake signing"),
            asset_ids=("pul7sar-logo", "pul7sar-pulse"),
            factual_constraints=("transfer remains at approach stage",),
            layout_boxes={"hero": {"x": 100, "y": 250, "width": 800, "height": 1000}},
            accent_hex="#EF0107",
        )
        self.readiness = LocalGenerationReadinessReport(
            ready=True,
            provider_id=FLUX2_KLEIN_4B_LOCAL.provider_id,
            model_id=FLUX2_KLEIN_4B_LOCAL.model_id,
            backend="diffusers",
            runtime_kind="local_cuda",
            gpu_name="GPU",
            gpu_vram_gb=16.0,
            blockers=(),
            warnings=(),
        )

    def request(self):
        return LocalBackendRequestCompiler().compile(
            package=self.package,
            model=FLUX2_KLEIN_4B_LOCAL,
            readiness=self.readiness,
            backend="diffusers",
            seed=7007,
            request_id="pul7sar-local-001",
            reference_asset_ids=("identity-ref-1",),
        )

    def test_compile_preserves_zero_cost_and_seed(self):
        request = self.request()
        self.assertEqual(request.seed, 7007)
        self.assertEqual(request.metadata["cost_mode"], "$0-local")
        self.assertEqual(request.width, 1080)
        self.assertEqual(request.height, 1920)

    def test_flux_constraints_are_reframed_not_dropped(self):
        request = self.request()
        self.assertEqual(request.native_negative_constraints, ())
        self.assertIn("dignified and respectful", request.prompt)
        self.assertIn("pre-signing", request.prompt)

    def test_request_explicitly_keeps_official_assets_out_of_base_scene(self):
        request = self.request()
        self.assertIn("Do not render PUL7SAR branding", request.prompt)
        self.assertIn("club crests", request.prompt)

    def test_not_ready_report_blocks_generation_request(self):
        blocked = LocalGenerationReadinessReport(
            ready=False,
            provider_id=self.readiness.provider_id,
            model_id=self.readiness.model_id,
            backend="diffusers",
            runtime_kind="local_cpu",
            gpu_name=None,
            gpu_vram_gb=None,
            blockers=("CUDA unavailable",),
            warnings=(),
        )
        with self.assertRaises(ValueError):
            LocalBackendRequestCompiler().compile(
                package=self.package,
                model=FLUX2_KLEIN_4B_LOCAL,
                readiness=blocked,
                backend="diffusers",
                seed=1,
                request_id="blocked",
            )

    def test_result_gate_preserves_exact_provenance(self):
        request = self.request()
        result = LocalBackendGenerationResult(
            provider_id=request.provider_id,
            model_id=request.model_id,
            backend=request.backend,
            output_ref="file:///tmp/base.png",
            width=request.width,
            height=request.height,
            seed=request.seed,
            request_id=request.request_id,
            metadata={"backend_version": "test"},
        )
        provenance = LocalBackendResultGate().validate(request, result)
        self.assertEqual(provenance.seed, 7007)
        self.assertEqual(provenance.request_id, "pul7sar-local-001")

    def test_backend_cannot_change_seed(self):
        request = self.request()
        result = LocalBackendGenerationResult(
            request.provider_id, request.model_id, request.backend,
            "file:///tmp/base.png", request.width, request.height,
            request.seed + 1, request.request_id,
        )
        with self.assertRaises(ValueError):
            LocalBackendResultGate().validate(request, result)

    def test_backend_cannot_change_dimensions(self):
        request = self.request()
        result = LocalBackendGenerationResult(
            request.provider_id, request.model_id, request.backend,
            "file:///tmp/base.png", 1024, 1024,
            request.seed, request.request_id,
        )
        with self.assertRaises(ValueError):
            LocalBackendResultGate().validate(request, result)


if __name__ == "__main__":
    unittest.main()
