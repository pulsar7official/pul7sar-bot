import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.local_backend_execution import LocalBackendGenerationRequest
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff


class LocalGenerationHandoffTests(unittest.TestCase):
    def request(self):
        return LocalBackendGenerationRequest(
            provider_id="local-flux2-klein-4b",
            model_id="black-forest-labs/FLUX.2-klein-4B",
            backend="diffusers",
            prompt="premium clean sports editorial base scene",
            native_negative_constraints=(),
            width=1024,
            height=1024,
            seed=712345,
            request_id="golden-proof-001",
            reference_asset_ids=(),
            metadata={"cost_mode": "$0-local", "platform": "instagram_feed"},
        )

    def test_round_trip_preserves_locked_request(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "handoff.json"
            LocalGenerationHandoff.write(self.request(), str(path))
            loaded = LocalGenerationHandoff.read(str(path))
            self.assertEqual(loaded, self.request())
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["handoff_version"], "pul7sar-local-generation-v1")

    def test_non_zero_cost_handoff_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "handoff.json"
            data = LocalGenerationHandoff.to_dict(self.request())
            data["metadata"]["cost_mode"] = "paid"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "\$0-local"):
                LocalGenerationHandoff.read(str(path))


if __name__ == "__main__":
    unittest.main()
