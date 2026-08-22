import tempfile
import unittest
from pathlib import Path

from engine.intelligence.local_backend_execution import LocalBackendGenerationRequest
from engine.intelligence.local_comfyui_adapter import ComfyUIExecutionConfig, ComfyUILocalBackend
from engine.intelligence.local_diffusers_adapter import DiffusersExecutionConfig, DiffusersLocalBackend


class FakeImage:
    def save(self, path):
        Path(path).write_bytes(b"PNG")


class FakeResult:
    image = FakeImage()


class LocalBackendAdapterTests(unittest.TestCase):
    def request(self, backend):
        return LocalBackendGenerationRequest(
            provider_id="local-flux2-klein-4b",
            model_id="black-forest-labs/FLUX.2-klein-4B",
            backend=backend,
            prompt="premium sports editorial base scene",
            native_negative_constraints=(),
            width=1080,
            height=1920,
            seed=712345,
            request_id="req-001",
            reference_asset_ids=("identity-ref-1",),
            metadata={"cost_mode": "$0-local"},
        )

    def test_diffusers_adapter_preserves_locked_contract(self):
        calls = {}

        def factory(model_id, dtype):
            calls["model"] = model_id
            calls["dtype"] = dtype
            def pipeline(**kwargs):
                calls["kwargs"] = kwargs
                return FakeResult()
            return pipeline

        with tempfile.TemporaryDirectory() as tmp:
            backend = DiffusersLocalBackend(DiffusersExecutionConfig(tmp), factory)
            result = backend.generate(self.request("diffusers"))
            self.assertEqual(result.seed, 712345)
            self.assertEqual(result.width, 1080)
            self.assertTrue(Path(result.output_ref).exists())
            self.assertEqual(calls["kwargs"]["reference_asset_ids"], ("identity-ref-1",))

    def test_diffusers_rejects_wrong_backend(self):
        with tempfile.TemporaryDirectory() as tmp:
            backend = DiffusersLocalBackend(DiffusersExecutionConfig(tmp), lambda *_: None)
            with self.assertRaises(ValueError):
                backend.generate(self.request("comfyui"))

    def test_comfyui_config_rejects_remote_endpoint(self):
        with self.assertRaises(ValueError):
            ComfyUIExecutionConfig("https://example.com", "workflow-1")

    def test_comfyui_adapter_preserves_locked_contract(self):
        captured = {}
        def executor(endpoint, workflow_id, payload):
            captured.update(payload)
            return {"output_ref": "file:///tmp/generated.png"}

        backend = ComfyUILocalBackend(
            ComfyUIExecutionConfig("http://127.0.0.1:8188", "workflow-1"),
            executor,
        )
        result = backend.generate(self.request("comfyui"))
        self.assertEqual(result.seed, 712345)
        self.assertEqual(captured["width"], 1080)
        self.assertEqual(captured["request_id"], "req-001")


if __name__ == "__main__":
    unittest.main()
