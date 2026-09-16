from __future__ import annotations

import os
from pathlib import Path
import unittest
from unittest.mock import patch

from tools import phase18_run_first_genuine_golden_v6_authoritative_entrypoint as entry


class AuthoritativeEntrypointTests(unittest.TestCase):
    SHA = "a" * 40

    def _env(self):
        return patch.dict(os.environ, {
            "PUL7SAR_PHASE18_COST_MODE": "$0-local",
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
        }, clear=False)

    def test_capture_precedes_fresh_and_authorities_stay_closed(self):
        order = []

        def fake_capture(**kwargs):
            order.append("capture")
            self.assertEqual(kwargs["source_sha"], self.SHA)
            return {"ready": True, "binding": "bound.json"}

        def fake_fresh(**kwargs):
            order.append("fresh")
            self.assertEqual(kwargs["expected_commit"], self.SHA)
            self.assertTrue(str(kwargs["network_evidence_path"]).endswith("first-genuine-golden-v6-zero-cost-network-guard.json"))
            self.assertTrue(str(kwargs["runner_identity_path"]).endswith("first-genuine-golden-v6-runner-identity.json"))
            self.assertTrue(str(kwargs["snapshot_inventory_path"]).endswith("first-genuine-golden-v6-approved-snapshot-inventory.json"))
            self.assertTrue(str(kwargs["execution_blocker_path"]).endswith("first-genuine-golden-v6-execution-blocker-probe.json"))
            return {"ready": True, "blockers": [], "canonical_png": "candidate.png", "canonical_png_sha256": "f" * 64}

        with self._env(), patch.object(entry, "capture", side_effect=fake_capture), patch.object(entry, "run_fresh", side_effect=fake_fresh):
            result = entry.run(expected_commit=self.SHA, output_path=Path("output/candidate.png"))

        self.assertEqual(order, ["capture", "fresh"])
        self.assertTrue(result["ready"])
        for field in ("authoritative_gate", "network_download_authorized", "generation_authorized", "publication_ready", "seeds_2_to_4_authorized"):
            self.assertFalse(result[field])

    def test_capture_failure_prevents_fresh_launcher(self):
        with self._env(), patch.object(entry, "capture", return_value={"ready": False}), patch.object(entry, "run_fresh") as fresh:
            with self.assertRaisesRegex(RuntimeError, "CAPTURE_NOT_READY"):
                entry.run(expected_commit=self.SHA, output_path=Path("output/candidate.png"))
            fresh.assert_not_called()

    def test_offline_contract_fails_before_capture(self):
        with patch.dict(os.environ, {"PUL7SAR_PHASE18_COST_MODE": "$0-local", "HF_HUB_OFFLINE": "0", "TRANSFORMERS_OFFLINE": "1"}, clear=False), patch.object(entry, "capture") as capture:
            with self.assertRaisesRegex(RuntimeError, "REQUIRES_OFFLINE"):
                entry.run(expected_commit=self.SHA, output_path=Path("output/candidate.png"))
            capture.assert_not_called()

    def test_malformed_sha_fails_before_capture(self):
        with self._env(), patch.object(entry, "capture") as capture:
            with self.assertRaisesRegex(RuntimeError, "SOURCE_SHA_INVALID"):
                entry.run(expected_commit="bad", output_path=Path("output/candidate.png"))
            capture.assert_not_called()


if __name__ == "__main__":
    unittest.main()
