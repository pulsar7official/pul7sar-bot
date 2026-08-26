import unittest
from types import SimpleNamespace
from unittest.mock import patch

from engine.intelligence.flux2_klein_diffusers import (
    Flux2KleinDiffusersProbe,
    Flux2KleinInferenceConfig,
    Flux2KleinPipelineWrapper,
    build_flux2_klein_pipeline_factory,
)


class _FakeGenerator:
    def __init__(self, device):
        self.device = device
        self.seed = None

    def manual_seed(self, seed):
        self.seed = seed
        return self


class _FakeCuda:
    def __init__(self, total_vram_gb=24.0, *, available=True, expose_properties=True):
        self.total_vram_gb = total_vram_gb
        self.available = available
        self.expose_properties = expose_properties

    def is_available(self):
        return self.available

    def get_device_properties(self, index):
        if not self.expose_properties:
            raise RuntimeError("device properties unavailable")
        return SimpleNamespace(total_memory=int(self.total_vram_gb * (1024 ** 3)))


class _FakeTorch:
    float16 = "fp16"
    bfloat16 = "bf16"
    float32 = "fp32"
    Generator = _FakeGenerator
    cuda = _FakeCuda()


class _Result:
    def __init__(self, image):
        self.images = [image]


class _Pipe:
    def __init__(self, *, sequential=True):
        self.offloaded = False
        self.sequential_offloaded = False
        self.calls = []
        if not sequential:
            self.enable_sequential_cpu_offload = None

    def enable_model_cpu_offload(self):
        self.offloaded = True

    def enable_sequential_cpu_offload(self):
        self.sequential_offloaded = True

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return _Result("IMAGE")


class Flux2KleinDiffusersTests(unittest.TestCase):
    def test_probe_requires_flux2_klein_pipeline_symbol(self):
        modules = {
            "torch": SimpleNamespace(),
            "diffusers": SimpleNamespace(__version__="test", Flux2KleinPipeline=object()),
        }
        with patch("engine.intelligence.flux2_klein_diffusers.import_module", side_effect=lambda name: modules[name]), \
             patch("engine.intelligence.flux2_klein_diffusers.package_version", return_value="9.9.9"):
            snapshot = Flux2KleinDiffusersProbe().probe()
        self.assertTrue(snapshot.available)
        self.assertEqual(snapshot.version, "9.9.9")
        self.assertIn("Flux2KleinPipeline-present", snapshot.details)

    def test_probe_rejects_old_diffusers_without_flux2_klein_pipeline(self):
        modules = {
            "torch": SimpleNamespace(),
            "diffusers": SimpleNamespace(__version__="old"),
        }
        with patch("engine.intelligence.flux2_klein_diffusers.import_module", side_effect=lambda name: modules[name]), \
             patch("engine.intelligence.flux2_klein_diffusers.package_version", return_value="0.0.1"):
            snapshot = Flux2KleinDiffusersProbe().probe()
        self.assertFalse(snapshot.available)
        self.assertIn("Flux2KleinPipeline-missing", snapshot.details)

    def test_factory_prefers_sequential_cpu_offload(self):
        pipe = _Pipe()
        calls = []

        def loader(model_id, **kwargs):
            calls.append((model_id, kwargs))
            return pipe

        factory = build_flux2_klein_pipeline_factory(
            pipeline_loader=loader,
            torch_module=_FakeTorch,
        )
        wrapper = factory("black-forest-labs/FLUX.2-klein-4B", "bfloat16")
        self.assertIsInstance(wrapper, Flux2KleinPipelineWrapper)
        self.assertTrue(pipe.sequential_offloaded)
        self.assertFalse(pipe.offloaded)
        self.assertEqual(calls[0][0], "black-forest-labs/FLUX.2-klein-4B")
        self.assertEqual(calls[0][1]["torch_dtype"], "bf16")

    def test_factory_allows_model_cpu_offload_only_when_vram_is_above_safety_floor(self):
        pipe = _Pipe(sequential=False)

        def loader(model_id, **kwargs):
            return pipe

        high_vram_torch = SimpleNamespace(
            float16="fp16",
            bfloat16="bf16",
            float32="fp32",
            Generator=_FakeGenerator,
            cuda=_FakeCuda(24.0),
        )
        factory = build_flux2_klein_pipeline_factory(
            pipeline_loader=loader,
            torch_module=high_vram_torch,
        )
        factory("black-forest-labs/FLUX.2-klein-4B", "bfloat16")
        self.assertTrue(pipe.offloaded)
        self.assertFalse(pipe.sequential_offloaded)

    def test_factory_blocks_model_offload_fallback_on_t4_class_vram(self):
        pipe = _Pipe(sequential=False)

        def loader(model_id, **kwargs):
            return pipe

        t4_like_torch = SimpleNamespace(
            float16="fp16",
            bfloat16="bf16",
            float32="fp32",
            Generator=_FakeGenerator,
            cuda=_FakeCuda(14.6),
        )
        factory = build_flux2_klein_pipeline_factory(
            pipeline_loader=loader,
            torch_module=t4_like_torch,
        )
        with self.assertRaisesRegex(RuntimeError, "sequential CPU offload is required on low-VRAM"):
            factory("black-forest-labs/FLUX.2-klein-4B", "bfloat16")
        self.assertFalse(pipe.offloaded)
        self.assertFalse(pipe.sequential_offloaded)

    def test_factory_blocks_model_offload_when_cuda_vram_cannot_be_proven(self):
        pipe = _Pipe(sequential=False)

        def loader(model_id, **kwargs):
            return pipe

        unknown_vram_torch = SimpleNamespace(
            float16="fp16",
            bfloat16="bf16",
            float32="fp32",
            Generator=_FakeGenerator,
            cuda=_FakeCuda(expose_properties=False),
        )
        factory = build_flux2_klein_pipeline_factory(
            pipeline_loader=loader,
            torch_module=unknown_vram_torch,
        )
        with self.assertRaisesRegex(RuntimeError, "CUDA VRAM could not be proven"):
            factory("black-forest-labs/FLUX.2-klein-4B", "bfloat16")
        self.assertFalse(pipe.offloaded)

    def test_factory_can_explicitly_allow_model_offload_without_sequential_preference(self):
        pipe = _Pipe(sequential=False)

        def loader(model_id, **kwargs):
            return pipe

        no_vram_evidence_torch = SimpleNamespace(
            float16="fp16",
            bfloat16="bf16",
            float32="fp32",
            Generator=_FakeGenerator,
        )
        config = Flux2KleinInferenceConfig(prefer_sequential_cpu_offload=False)
        factory = build_flux2_klein_pipeline_factory(
            inference=config,
            pipeline_loader=loader,
            torch_module=no_vram_evidence_torch,
        )
        factory("black-forest-labs/FLUX.2-klein-4B", "bfloat16")
        self.assertTrue(pipe.offloaded)

    def test_invalid_model_offload_safety_floor_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "model_offload_minimum_total_vram_gb"):
            Flux2KleinInferenceConfig(model_offload_minimum_total_vram_gb=0)

    def test_wrapper_maps_seed_official_controls_and_metadata(self):
        pipe = _Pipe()
        wrapper = Flux2KleinPipelineWrapper(
            pipe,
            _FakeTorch,
            Flux2KleinInferenceConfig(),
            offload_mode="sequential_cpu",
        )
        result = wrapper(
            prompt="premium sports scene",
            negative_prompt=None,
            width=1024,
            height=1024,
            seed=77,
            reference_asset_ids=(),
        )
        self.assertEqual(result["image"], "IMAGE")
        self.assertEqual(result["metadata"]["pipeline"], "Flux2KleinPipeline")
        self.assertEqual(result["metadata"]["num_inference_steps"], 4)
        self.assertEqual(result["metadata"]["offload_mode"], "sequential_cpu")
        self.assertEqual(result["metadata"]["native_canvas_alignment"], 16)
        call = pipe.calls[0]
        self.assertEqual(call["guidance_scale"], 1.0)
        self.assertEqual(call["num_inference_steps"], 4)
        self.assertEqual(call["generator"].seed, 77)
        self.assertEqual(call["generator"].device, "cuda")

    def test_non_aligned_native_canvas_is_rejected_before_pipeline_call(self):
        pipe = _Pipe()
        wrapper = Flux2KleinPipelineWrapper(pipe, _FakeTorch, Flux2KleinInferenceConfig())
        with self.assertRaisesRegex(ValueError, "divisible by 16"):
            wrapper(
                prompt="scene",
                negative_prompt=None,
                width=1080,
                height=1350,
                seed=1,
                reference_asset_ids=(),
            )
        self.assertEqual(pipe.calls, [])

    def test_native_negative_prompt_is_rejected(self):
        wrapper = Flux2KleinPipelineWrapper(_Pipe(), _FakeTorch, Flux2KleinInferenceConfig())
        with self.assertRaisesRegex(ValueError, "negative prompts"):
            wrapper(
                prompt="scene",
                negative_prompt="no text",
                width=1024,
                height=1024,
                seed=1,
                reference_asset_ids=(),
            )

    def test_reference_ids_fail_closed_until_asset_path_resolver_exists(self):
        wrapper = Flux2KleinPipelineWrapper(_Pipe(), _FakeTorch, Flux2KleinInferenceConfig())
        with self.assertRaisesRegex(ValueError, "asset-path resolver"):
            wrapper(
                prompt="scene",
                negative_prompt=None,
                width=1024,
                height=1024,
                seed=1,
                reference_asset_ids=("verified-person-ref",),
            )


if __name__ == "__main__":
    unittest.main()
