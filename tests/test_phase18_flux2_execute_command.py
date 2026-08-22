import json
import tempfile
import unittest
from pathlib import Path

from tools.phase18_flux2_execute import _request_from_json


class Flux2ExecuteCommandTests(unittest.TestCase):
    def write(self, data):
        temp = tempfile.TemporaryDirectory()
        path = Path(temp.name) / "request.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return temp, path

    def valid(self):
        return {
            "handoff_version": "pul7sar-local-generation-v1",
            "provider_id": "local-flux2-klein-4b",
            "model_id": "black-forest-labs/FLUX.2-klein-4B",
            "backend": "diffusers",
            "prompt": "premium clean sports editorial base scene",
            "native_negative_constraints": [],
            "width": 1024,
            "height": 1024,
            "seed": 77,
            "request_id": "proof-77",
            "reference_asset_ids": [],
            "metadata": {"cost_mode": "$0-local"},
        }

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
        temp, path = self.write(data)
        try:
            with self.assertRaisesRegex(ValueError, "\$0-local"):
                _request_from_json(str(path))
        finally:
            temp.cleanup()

    def test_missing_request_fields_are_rejected(self):
        data = self.valid()
        del data["seed"]
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


if __name__ == "__main__":
    unittest.main()
