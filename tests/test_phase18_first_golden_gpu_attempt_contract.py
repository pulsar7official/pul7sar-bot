import json
from pathlib import Path
import tempfile
import unittest

from tools import phase18_prepare_first_golden_gpu_attempt as attempt


ROOT = Path(__file__).resolve().parents[1]


class FirstGoldenGpuAttemptContractTests(unittest.TestCase):
    def setUp(self) -> None:
        output_dir = ROOT / "output/phase18_gpu_smoke"
        output_dir.mkdir(parents=True, exist_ok=True)
        handle = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            prefix="test-first-golden-handoff-",
            dir=output_dir,
            delete=False,
            encoding="utf-8",
        )
        self.path = Path(handle.name)
        handle.close()
        self.expected_commit = "a" * 40

    def tearDown(self) -> None:
        self.path.unlink(missing_ok=True)

    def valid_handoff(self) -> dict[str, object]:
        return {
            "schema": attempt.HANDOFF_SCHEMA,
            "expected_commit": self.expected_commit,
            "branch_required": attempt.EXPECTED_BRANCH,
            "cost_mode_required": "$0-local",
            "offline_required": True,
            "canonical_workflow": attempt.CANONICAL_WORKFLOW,
            "required_runner_labels": list(attempt.REQUIRED_RUNNER_LABELS),
            "eligible_for_authoritative_golden_preflight": True,
            "blockers": [],
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }

    def write(self, payload: dict[str, object]) -> None:
        self.path.write_text(json.dumps(payload), encoding="utf-8")

    def test_valid_handoff_prepares_exact_no_dispatch_canonical_contract(self) -> None:
        self.write(self.valid_handoff())
        payload = attempt.build(expected_commit=self.expected_commit, handoff_path=self.path)

        self.assertTrue(payload["attempt_contract_ready"])
        self.assertEqual(payload["blockers"], [])
        self.assertFalse(payload["workflow_dispatch_performed"])
        self.assertFalse(payload["png_created"])
        for field in attempt.CLOSED_AUTHORITIES:
            self.assertFalse(payload[field])

        command = payload["canonical_command"]
        self.assertEqual(command[0:2], ["python", attempt.CANONICAL_LAUNCHER])
        self.assertIn("--expected-commit", command)
        self.assertIn(self.expected_commit, command)
        self.assertIn("--handoff", command)
        self.assertIn(attempt.DEFAULT_PATHS["gpu_handoff"], command)
        self.assertEqual(payload["required_runner_labels"], attempt.REQUIRED_RUNNER_LABELS)
        self.assertEqual(payload["cost_mode_required"], "$0-local")
        self.assertTrue(payload["offline_required"])

    def test_commit_drift_fails_closed(self) -> None:
        handoff = self.valid_handoff()
        handoff["expected_commit"] = "b" * 40
        self.write(handoff)
        payload = attempt.build(expected_commit=self.expected_commit, handoff_path=self.path)
        self.assertFalse(payload["attempt_contract_ready"])
        self.assertIn("GPU_HANDOFF_COMMIT_DRIFT", payload["blockers"])
        self.assertFalse(payload["generation_authorized"])

    def test_authority_drift_fails_closed(self) -> None:
        handoff = self.valid_handoff()
        handoff["generation_authorized"] = True
        self.write(handoff)
        payload = attempt.build(expected_commit=self.expected_commit, handoff_path=self.path)
        self.assertFalse(payload["attempt_contract_ready"])
        self.assertIn("GPU_HANDOFF_AUTHORITY_DRIFT_GENERATION_AUTHORIZED", payload["blockers"])
        self.assertFalse(payload["generation_authorized"])
        self.assertFalse(payload["publication_ready"])

    def test_runner_label_drift_fails_closed(self) -> None:
        handoff = self.valid_handoff()
        handoff["required_runner_labels"] = ["self-hosted", "gpu"]
        self.write(handoff)
        payload = attempt.build(expected_commit=self.expected_commit, handoff_path=self.path)
        self.assertFalse(payload["attempt_contract_ready"])
        self.assertIn("GPU_HANDOFF_RUNNER_LABEL_DRIFT", payload["blockers"])

    def test_invalid_sha_and_invalid_json_fail_closed(self) -> None:
        self.path.write_text("not-json", encoding="utf-8")
        payload = attempt.build(expected_commit="not-a-sha", handoff_path=self.path)
        self.assertFalse(payload["attempt_contract_ready"])
        self.assertIn("EXPECTED_COMMIT_INVALID", payload["blockers"])
        self.assertIn("GPU_HANDOFF_INVALID_JSON", payload["blockers"])
        self.assertFalse(payload["workflow_dispatch_performed"])
        self.assertFalse(payload["png_created"])


if __name__ == "__main__":
    unittest.main()
