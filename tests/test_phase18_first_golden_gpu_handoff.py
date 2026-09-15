import json
from pathlib import Path
import tempfile
import unittest

from tools.phase18_build_first_golden_gpu_handoff import (
    CANONICAL_WORKFLOW,
    HOST_READINESS_WORKFLOW,
    REQUIRED_RUNNER_LABELS,
    build,
)


class Phase18FirstGoldenGpuHandoffTests(unittest.TestCase):
    def _ready_summary(self, expected_commit: str) -> dict[str, object]:
        return {
            "schema": "pul7sar-phase18-first-golden-attested-pre-gpu-run-v1",
            "expected_commit": expected_commit,
            "ready_for_authoritative_golden_preflight": True,
            "receipt_attested": True,
            "blockers": [],
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }

    def _write_summary(self, payload: dict[str, object]) -> Path:
        root = Path(__file__).resolve().parents[1]
        target = root / "output" / "phase18_gpu_smoke" / "test-first-golden-handoff-summary.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload), encoding="utf-8")
        self.addCleanup(lambda: target.unlink(missing_ok=True))
        return target

    def test_ready_attested_summary_produces_preflight_eligible_closed_handoff(self):
        expected_commit = "a" * 40
        path = self._write_summary(self._ready_summary(expected_commit))
        result = build(expected_commit=expected_commit, attested_summary_path=path)

        self.assertTrue(result["eligible_for_authoritative_golden_preflight"])
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["canonical_workflow"], CANONICAL_WORKFLOW)
        self.assertEqual(result["host_readiness_workflow"], HOST_READINESS_WORKFLOW)
        self.assertEqual(result["required_runner_labels"], REQUIRED_RUNNER_LABELS)
        self.assertEqual(result["cost_mode_required"], "$0-local")
        self.assertTrue(result["offline_required"])
        for field in (
            "authoritative_gate",
            "network_download_authorized",
            "generation_authorized",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ):
            self.assertIs(result[field], False)

    def test_commit_drift_fails_closed(self):
        expected_commit = "b" * 40
        path = self._write_summary(self._ready_summary("c" * 40))
        result = build(expected_commit=expected_commit, attested_summary_path=path)
        self.assertFalse(result["eligible_for_authoritative_golden_preflight"])
        self.assertIn("ATTESTED_PRE_GPU_COMMIT_DRIFT", result["blockers"])
        self.assertIs(result["generation_authorized"], False)

    def test_authority_drift_fails_closed(self):
        expected_commit = "d" * 40
        payload = self._ready_summary(expected_commit)
        payload["generation_authorized"] = True
        path = self._write_summary(payload)
        result = build(expected_commit=expected_commit, attested_summary_path=path)
        self.assertFalse(result["eligible_for_authoritative_golden_preflight"])
        self.assertIn("ATTESTED_PRE_GPU_GENERATION_AUTHORIZED_DRIFT", result["blockers"])
        self.assertIs(result["publication_ready"], False)

    def test_remaining_pre_gpu_blockers_fail_closed(self):
        expected_commit = "e" * 40
        payload = self._ready_summary(expected_commit)
        payload["ready_for_authoritative_golden_preflight"] = False
        payload["blockers"] = ["CUDA_UNAVAILABLE"]
        path = self._write_summary(payload)
        result = build(expected_commit=expected_commit, attested_summary_path=path)
        self.assertFalse(result["eligible_for_authoritative_golden_preflight"])
        self.assertIn("ATTESTED_PRE_GPU_NOT_READY", result["blockers"])
        self.assertIn("ATTESTED_PRE_GPU_BLOCKERS_REMAIN", result["blockers"])

    def test_invalid_expected_commit_fails_closed(self):
        path = self._write_summary(self._ready_summary("f" * 40))
        result = build(expected_commit="not-a-sha", attested_summary_path=path)
        self.assertFalse(result["eligible_for_authoritative_golden_preflight"])
        self.assertIn("EXPECTED_COMMIT_INVALID", result["blockers"])

    def test_missing_summary_fails_closed(self):
        root = Path(__file__).resolve().parents[1]
        missing = root / "output" / "phase18_gpu_smoke" / "definitely-missing-handoff-summary.json"
        missing.unlink(missing_ok=True)
        result = build(expected_commit="1" * 40, attested_summary_path=missing)
        self.assertFalse(result["eligible_for_authoritative_golden_preflight"])
        self.assertIn("ATTESTED_PRE_GPU_SUMMARY_MISSING", result["blockers"])


if __name__ == "__main__":
    unittest.main()
