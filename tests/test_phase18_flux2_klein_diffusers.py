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


class _FakeTorch:
    float16 = "fp16"
    bfloat16 = "bf16"
    float32 = "fp32"
    Generator = _FakeGenerator


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

    def test_factory_falls_back_to_model_cpu_offload(self):
        pipe = _Pipe(sequential=False)

        def loader(model_id, **kwargs):
            return pipe

        factory = build_flux2_klein_pipeline_factory(
            pipeline_loader=loader,
            torch_module=_FakeTorch,
        )
        factory("black-forest-labs/FLUX.2-klein-4B", "bfloat16")
        self.assertTrue(pipe.offloaded)
        self.assertFalse(pipe.sequential_offloaded)

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
