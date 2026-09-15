from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tools.phase18_attest_first_golden_pre_gpu_receipt import attest


HEAD = "a" * 40


def ready_receipt() -> dict[str, object]:
    return {
        "schema": "pul7sar-phase18-first-golden-pre-gpu-probe-v1",
        "expected_commit": HEAD,
        "cost_mode_required": "$0-local",
        "source_identity_ready": True,
        "execution_environment_evaluated": True,
        "ready_for_authoritative_golden_preflight": True,
        "blockers": [],
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
        "source_identity": {
            "source_identity_ready": True,
            "expected_commit": HEAD,
            "head_commit": HEAD,
            "branch_observed": "phase18/story-intelligence",
            "tracked_worktree_clean": True,
            "main_py_modified": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        },
        "execution_environment": {
            "ready_for_authoritative_golden_preflight": True,
            "network_download_authorized": False,
            "generation_authorized": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        },
    }


class FirstGoldenPreGpuReceiptAttestationTests(unittest.TestCase):
    def write_receipt(self, payload: dict[str, object]) -> Path:
        temp = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".json",
            prefix="phase18-pre-gpu-",
            dir=Path.cwd(),
            delete=False,
        )
        with temp:
            json.dump(payload, temp, sort_keys=True)
            temp.write("\n")
        self.addCleanup(lambda: Path(temp.name).unlink(missing_ok=True))
        return Path(temp.name)

    def test_ready_receipt_is_bound_to_exact_bytes_and_commit(self):
        path = self.write_receipt(ready_receipt())
        payload = attest(receipt_path=path, expected_commit=HEAD)
        self.assertTrue(payload["receipt_attested"])
        self.assertTrue(payload["ready_for_authoritative_golden_preflight"])
        self.assertEqual(payload["blockers"], [])
        self.assertEqual(payload["expected_commit"], HEAD)
        self.assertEqual(len(payload["receipt_sha256"]), 64)
        self.assertGreater(payload["receipt_bytes"], 0)
        self.assertFalse(payload["authoritative_gate"])
        self.assertFalse(payload["network_download_authorized"])
        self.assertFalse(payload["generation_authorized"])
        self.assertFalse(payload["publication_ready"])
        self.assertFalse(payload["seeds_2_to_4_authorized"])

    def test_expected_commit_drift_fails_closed(self):
        receipt = ready_receipt()
        receipt["expected_commit"] = "b" * 40
        path = self.write_receipt(receipt)
        payload = attest(receipt_path=path, expected_commit=HEAD)
        self.assertIn("PRE_GPU_RECEIPT_EXPECTED_COMMIT_DRIFT", payload["blockers"])
        self.assertFalse(payload["receipt_attested"])

    def test_nested_head_commit_drift_fails_closed(self):
        receipt = ready_receipt()
        receipt["source_identity"]["head_commit"] = "b" * 40
        path = self.write_receipt(receipt)
        payload = attest(receipt_path=path, expected_commit=HEAD)
        self.assertIn("PRE_GPU_SOURCE_HEAD_COMMIT_DRIFT", payload["blockers"])
        self.assertFalse(payload["receipt_attested"])

    def test_dirty_worktree_or_main_py_drift_fails_closed(self):
        receipt = ready_receipt()
        receipt["source_identity"]["tracked_worktree_clean"] = False
        receipt["source_identity"]["main_py_modified"] = True
        path = self.write_receipt(receipt)
        payload = attest(receipt_path=path, expected_commit=HEAD)
        self.assertIn("PRE_GPU_SOURCE_WORKTREE_NOT_CLEAN", payload["blockers"])
        self.assertIn("PRE_GPU_SOURCE_MAIN_PY_DRIFT", payload["blockers"])
        self.assertFalse(payload["receipt_attested"])

    def test_nested_authority_drift_fails_closed(self):
        receipt = ready_receipt()
        receipt["execution_environment"]["generation_authorized"] = True
        path = self.write_receipt(receipt)
        payload = attest(receipt_path=path, expected_commit=HEAD)
        self.assertIn("EXECUTION_GENERATION_AUTHORITY_DRIFT", payload["blockers"])
        self.assertFalse(payload["receipt_attested"])

    def test_not_ready_receipt_cannot_be_attested(self):
        receipt = ready_receipt()
        receipt["ready_for_authoritative_golden_preflight"] = False
        receipt["blockers"] = ["FIRST_GOLDEN_EXECUTION_ENVIRONMENT_NOT_READY"]
        path = self.write_receipt(receipt)
        payload = attest(receipt_path=path, expected_commit=HEAD)
        self.assertIn("PRE_GPU_RECEIPT_NOT_READY", payload["blockers"])
        self.assertIn("PRE_GPU_RECEIPT_CONTAINS_BLOCKERS", payload["blockers"])
        self.assertFalse(payload["receipt_attested"])

    def test_invalid_expected_commit_fails_closed(self):
        path = self.write_receipt(ready_receipt())
        payload = attest(receipt_path=path, expected_commit="phase18/story-intelligence")
        self.assertIn("EXPECTED_COMMIT_INVALID", payload["blockers"])
        self.assertFalse(payload["receipt_attested"])


if __name__ == "__main__":
    unittest.main()
