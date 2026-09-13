from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
    QWEN25_VL_3B_MODEL_ID,
    QWEN25_VL_3B_REVISION,
)
from tools.phase18_verify_local_only_model_receipts import (
    STATUS,
    verify_flux_receipt,
    verify_qwen_receipt,
    verify_receipts,
)


class Phase18LocalOnlyModelReceiptVerifierTests(unittest.TestCase):
    def _qwen(self) -> dict[str, object]:
        return {
            "schema": "pul7sar-phase18-qwen-model-cache-v2",
            "ready": True,
            "revision_pinned": True,
            "cost_mode": "$0-local",
            "downloaded_now": False,
            "network_download_authorized": False,
            "local_files_only": True,
            "model_id": QWEN25_VL_3B_MODEL_ID,
            "model_revision": QWEN25_VL_3B_REVISION,
            "resolved_snapshot_revision": QWEN25_VL_3B_REVISION,
            "snapshot_path": f"/cache/models--Qwen--Qwen2.5-VL-3B-Instruct/snapshots/{QWEN25_VL_3B_REVISION}",
        }

    def _flux(self) -> dict[str, object]:
        return {
            "schema": "pul7sar-phase18-model-cache-v2",
            "ready": True,
            "revision_pinned": True,
            "cost_mode": "$0-local",
            "downloaded_now": False,
            "network_download_authorized": False,
            "local_files_only": True,
            "model_id": FLUX2_KLEIN_4B_MODEL_ID,
            "model_revision": FLUX2_KLEIN_4B_REVISION,
            "resolved_snapshot_revision": FLUX2_KLEIN_4B_REVISION,
            "snapshot_path": f"/cache/models--black-forest-labs--FLUX.2-klein-4B/snapshots/{FLUX2_KLEIN_4B_REVISION}",
        }

    def test_qwen_receipt_requires_explicit_no_network_authority(self) -> None:
        payload = self._qwen()
        payload["network_download_authorized"] = True
        with self.assertRaisesRegex(RuntimeError, "QWEN_NETWORK_DOWNLOAD_AUTHORITY_DRIFT"):
            verify_qwen_receipt(payload)

    def test_qwen_receipt_requires_local_files_only(self) -> None:
        payload = self._qwen()
        payload["local_files_only"] = False
        with self.assertRaisesRegex(RuntimeError, "QWEN_LOCAL_FILES_ONLY_UNPROVEN"):
            verify_qwen_receipt(payload)

    def test_flux_receipt_requires_explicit_no_network_authority(self) -> None:
        payload = self._flux()
        payload.pop("network_download_authorized")
        with self.assertRaisesRegex(RuntimeError, "FLUX_NETWORK_DOWNLOAD_AUTHORITY_DRIFT"):
            verify_flux_receipt(payload)

    def test_flux_receipt_requires_local_files_only(self) -> None:
        payload = self._flux()
        payload.pop("local_files_only")
        with self.assertRaisesRegex(RuntimeError, "FLUX_LOCAL_FILES_ONLY_UNPROVEN"):
            verify_flux_receipt(payload)

    def test_revision_drift_still_fails_closed(self) -> None:
        payload = self._flux()
        payload["resolved_snapshot_revision"] = "0" * 40
        with self.assertRaisesRegex(RuntimeError, "FLUX_RESOLVED_REVISION_DRIFT"):
            verify_flux_receipt(payload)

    def test_combined_verification_keeps_generation_and_publication_closed(self) -> None:
        import json

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            qwen_path = root / "qwen.json"
            flux_path = root / "flux.json"
            qwen_path.write_text(json.dumps(self._qwen()), encoding="utf-8")
            flux_path.write_text(json.dumps(self._flux()), encoding="utf-8")

            result = verify_receipts(qwen_path, flux_path)

        self.assertEqual(result["status"], STATUS)
        self.assertEqual(result["cost_mode"], "$0-local")
        self.assertIs(result["network_download_authorized"], False)
        self.assertIs(result["local_files_only"], True)
        self.assertIs(result["generation_authorized"], False)
        self.assertIs(result["publication_ready"], False)
        self.assertIs(result["seeds_2_to_4_authorized"], False)


if __name__ == "__main__":
    unittest.main()
