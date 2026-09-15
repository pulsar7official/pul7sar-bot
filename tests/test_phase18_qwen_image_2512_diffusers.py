import unittest

from engine.intelligence.qwen_image_2512_diffusers import (
    QwenImage2512InferenceConfig,
    QwenImage2512PipelineWrapper,
    build_qwen_image_2512_pipeline_factory,
)


class FakeGenerator:
    def __init__(self, device):
        self.device = device
        self.seed = None
    def manual_seed(self, seed):
        self.seed = seed
        return self


class FakeCuda:
    @staticmethod
    def is_available():
        return True


class FakeTorch:
    float16 = 'fp16'
    bfloat16 = 'bf16'
    float32 = 'fp32'
    cuda = FakeCuda()
    Generator = FakeGenerator


class FakeImage:
    pass


class FakePipelineResult:
    images = [FakeImage()]


class FakePipe:
    def __init__(self):
        self.calls = []
        self.offload = None
    def enable_model_cpu_offload(self):
        self.offload = 'model'
    def __call__(self, *, prompt, width, height, generator, negative_prompt=None):
        self.calls.append({
            'prompt': prompt, 'width': width, 'height': height,
            'generator': generator, 'negative_prompt': negative_prompt,
        })
        return FakePipelineResult()


class MissingLockedCanvasPipe:
    def __call__(self, *, prompt):
        return FakePipelineResult()


class QwenImage2512DiffusersTests(unittest.TestCase):
    def test_factory_uses_official_dtype_device_map_shape_and_preserves_lock(self):
        captured = {}
        pipe = FakePipe()
        def loader(model_id, **kwargs):
            captured['model_id'] = model_id
            captured.update(kwargs)
            return pipe
        factory = build_qwen_image_2512_pipeline_factory(
            pipeline_loader=loader,
            torch_module=FakeTorch,
        )
        wrapper = factory('Qwen/Qwen-Image-2512', 'bfloat16')
        result = wrapper(
            prompt='cinematic editorial atmosphere',
            negative_prompt='no readable text',
            width=1088,
            height=1360,
            seed=2512,
            reference_asset_ids=(),
        )
        self.assertEqual(captured['model_id'], 'Qwen/Qwen-Image-2512')
        self.assertEqual(captured['dtype'], 'bf16')
        self.assertEqual(captured['device_map'], 'cuda')
        self.assertEqual(pipe.offload, 'model')
        self.assertEqual(pipe.calls[0]['width'], 1088)
        self.assertEqual(pipe.calls[0]['height'], 1360)
        self.assertEqual(pipe.calls[0]['generator'].seed, 2512)
        self.assertEqual(result['metadata']['model_family'], 'Qwen-Image-2512')
        self.assertTrue(result['metadata']['seed_locked'])
        self.assertTrue(result['metadata']['canvas_locked'])

    def test_reference_assets_are_rejected_by_text_to_image_wrapper(self):
        wrapper = QwenImage2512PipelineWrapper(FakePipe(), FakeTorch, QwenImage2512InferenceConfig(), offload_mode='none')
        with self.assertRaisesRegex(ValueError, 'does not consume reference'):
            wrapper(prompt='scene', negative_prompt=None, width=1088, height=1360, seed=1, reference_asset_ids=('ref',))

    def test_pipeline_without_locked_canvas_and_generator_support_fails_closed(self):
        wrapper = QwenImage2512PipelineWrapper(MissingLockedCanvasPipe(), FakeTorch, QwenImage2512InferenceConfig(), offload_mode='none')
        with self.assertRaisesRegex(RuntimeError, 'locked width'):
            wrapper(prompt='scene', negative_prompt=None, width=1088, height=1360, seed=1, reference_asset_ids=())


if __name__ == '__main__':
    unittest.main()
