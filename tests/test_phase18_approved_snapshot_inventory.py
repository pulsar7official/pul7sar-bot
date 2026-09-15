from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
    QWEN25_VL_3B_MODEL_ID,
    QWEN25_VL_3B_REVISION,
)
from tools.phase18_capture_approved_snapshot_inventory import _snapshot_path, inspect


class ApprovedSnapshotInventoryTests(unittest.TestCase):
    def _env(self, cache_root: Path) -> dict[str, str]:
        return {
            "HF_HUB_CACHE": str(cache_root),
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "PUL7SAR_PHASE18_COST_MODE": "$0-local",
        }

    def _populate(self, cache_root: Path, model_id: str, revision: str, name: str, payload: bytes) -> None:
        snapshot = _snapshot_path(cache_root, model_id, revision)
        snapshot.mkdir(parents=True, exist_ok=True)
        (snapshot / name).write_bytes(payload)

    def test_ready_inventory_is_deterministic_for_same_local_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cache = Path(td) / "hub"
            self._populate(cache, QWEN25_VL_3B_MODEL_ID, QWEN25_VL_3B_REVISION, "config.json", b"qwen")
            self._populate(cache, FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION, "config.json", b"flux")
            first = inspect(env=self._env(cache))
            second = inspect(env=self._env(cache))
            self.assertTrue(first["ready"])
            self.assertEqual(first["combined_inventory_sha256"], second["combined_inventory_sha256"])
            self.assertFalse(first["generation_authorized"])
            self.assertFalse(first["network_download_authorized"])
            self.assertFalse(first["publication_ready"])

    def test_missing_flux_snapshot_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cache = Path(td) / "hub"
            self._populate(cache, QWEN25_VL_3B_MODEL_ID, QWEN25_VL_3B_REVISION, "config.json", b"qwen")
            payload = inspect(env=self._env(cache))
            self.assertFalse(payload["ready"])
            self.assertIn("FLUX_APPROVED_SNAPSHOT_INVENTORY_NOT_READY", payload["blockers"])

    def test_file_size_drift_changes_inventory_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cache = Path(td) / "hub"
            self._populate(cache, QWEN25_VL_3B_MODEL_ID, QWEN25_VL_3B_REVISION, "config.json", b"qwen")
            self._populate(cache, FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION, "weights.safetensors", b"1234")
            before = inspect(env=self._env(cache))
            flux_file = _snapshot_path(cache, FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION) / "weights.safetensors"
            flux_file.write_bytes(b"12345678")
            after = inspect(env=self._env(cache))
            self.assertNotEqual(before["flux"]["inventory_sha256"], after["flux"]["inventory_sha256"])

    def test_zero_cost_and_offline_contract_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cache = Path(td) / "hub"
            env = self._env(cache)
            env["HF_HUB_OFFLINE"] = "0"
            env["PUL7SAR_PHASE18_COST_MODE"] = "paid"
            payload = inspect(env=env)
            self.assertFalse(payload["ready"])
            self.assertIn("HF_HUB_OFFLINE_NOT_1", payload["blockers"])
            self.assertIn("ZERO_COST_MODE_NOT_ASSERTED", payload["blockers"])


if __name__ == "__main__":
    unittest.main()
