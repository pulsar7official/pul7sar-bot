import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.local_backend_execution import LocalBackendGenerationRequest
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from tools.phase18_flux2_execute import _request_from_json


class Flux2ExecuteCommandTests(unittest.TestCase):
    def write(self, data):
        temp = tempfile.TemporaryDirectory()
        path = Path(temp.name) / "request.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return temp, path

    def request(self):
        return LocalBackendGenerationRequest(
            provider_id="local-flux2-klein-4b",
            model_id="black-forest-labs/FLUX.2-klein-4B",
            backend="diffusers",
            prompt="premium clean sports editorial base scene",
            native_negative_constraints=(),
            width=1024,
            height=1024,
            seed=77,
            request_id="proof-77",
            reference_asset_ids=(),
            metadata={
                "cost_mode": "$0-local",
                "target_width": 1024,
                "target_height": 1024,
                "canvas_normalization_required": False,
            },
        )

    def valid(self):
        return LocalGenerationHandoff.to_dict(self.request())

    def rehash(self, data):
        payload = dict(data)
        payload.pop("payload_sha256", None)
        data["payload_sha256"] = LocalGenerationHandoff.payload_sha256(payload)
        return data

    def test_loads_locked_zero_cost_request(self):
        temp, path = self.write(self.valid())
        try:
            request = _request_from_json(str(path))
            self.assertEqual(request.seed, 77)
            self.assertEqual(request.metadata["cost_mode"], "$0-local")
        finally:
            temp.cleanup()

    def test_paid_or_unknown_cost_mode_is_rejected(self):
        data = self.valid()
        data["metadata"]["cost_mode"] = "paid"
        self.rehash(data)
        temp, path = self.write(data)
        try:
            with self.assertRaisesRegex(ValueError, "\\$0-local"):
                _request_from_json(str(path))
        finally:
            temp.cleanup()

    def test_missing_request_fields_are_rejected(self):
        data = self.valid()
        del data["seed"]
        self.rehash(data)
        temp, path = self.write(data)
        try:
            with self.assertRaisesRegex(ValueError, "missing generation handoff fields"):
                _request_from_json(str(path))
        finally:
            temp.cleanup()

    def test_unknown_handoff_version_is_rejected(self):
        data = self.valid()
        data["handoff_version"] = "future-version"
        temp, path = self.write(data)
        try:
            with self.assertRaisesRegex(ValueError, "handoff version"):
                _request_from_json(str(path))
        finally:
            temp.cleanup()

    def test_tampered_seed_is_rejected_before_executor_logic(self):
        data = self.valid()
        data["seed"] = 78
        temp, path = self.write(data)
        try:
            with self.assertRaisesRegex(ValueError, "integrity check failed"):
                _request_from_json(str(path))
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
