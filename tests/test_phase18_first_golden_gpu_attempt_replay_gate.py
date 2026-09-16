from pathlib import Path
import hashlib
import tempfile
import unittest
from unittest.mock import patch

from tools.phase18_run_first_genuine_golden_v6_canonical_attested import (
    CANONICAL_LAUNCHER,
    CANONICAL_WORKFLOW,
    ROOT,
    _attempt_contract_blockers,
    run,
)


GOOD_SHA = "a" * 40
CLOSED_AUTHORITIES = {
    "authoritative_gate": False,
    "network_download_authorized": False,
    "generation_authorized": False,
    "publication_ready": False,
    "seeds_2_to_4_authorized": False,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FirstGoldenGpuAttemptReplayGateTests(unittest.TestCase):
    def _ready_pre_gpu(self) -> dict[str, object]:
        return {
            "schema": "pul7sar-phase18-first-golden-attested-pre-gpu-run-v1",
            "expected_commit": GOOD_SHA,
            "ready_for_authoritative_golden_preflight": True,
            "receipt_attested": True,
            "blockers": [],
            **CLOSED_AUTHORITIES,
        }

    def _ready_handoff(self) -> dict[str, object]:
        return {
            "schema": "pul7sar-phase18-first-golden-gpu-handoff-v1",
            "expected_commit": GOOD_SHA,
            "branch_required": "phase18/story-intelligence",
            "cost_mode_required": "$0-local",
            "offline_required": True,
            "eligible_for_authoritative_golden_preflight": True,
            "blockers": [],
            **CLOSED_AUTHORITIES,
        }

    def _ready_attempt(self, handoff: Path) -> dict[str, object]:
        return {
            "schema": "pul7sar-phase18-first-golden-gpu-attempt-contract-v1",
            "expected_commit": GOOD_SHA,
            "branch_required": "phase18/story-intelligence",
            "cost_mode_required": "$0-local",
            "offline_required": True,
            "attempt_contract_ready": True,
            "blockers": [],
            "workflow_dispatch_performed": False,
            "png_created": False,
            "source_handoff_sha256": sha256(handoff),
            "canonical_workflow_sha256": sha256(ROOT / CANONICAL_WORKFLOW),
            "canonical_launcher_sha256": sha256(ROOT / CANONICAL_LAUNCHER),
            **CLOSED_AUTHORITIES,
        }

    def test_content_replay_accepts_exact_current_bytes(self) -> None:
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            handoff = Path(temp_dir) / "handoff.json"
            handoff.write_text("{}\n", encoding="utf-8")
            attempt = self._ready_attempt(handoff)
            self.assertEqual(
                _attempt_contract_blockers(
                    attempt=attempt,
                    expected_commit=GOOD_SHA,
                    handoff_target=handoff.resolve(),
                ),
                [],
            )

    def test_content_replay_rejects_handoff_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            handoff = Path(temp_dir) / "handoff.json"
            handoff.write_text("{}\n", encoding="utf-8")
            attempt = self._ready_attempt(handoff)
            handoff.write_text('{"drift":true}\n', encoding="utf-8")
            blockers = _attempt_contract_blockers(
                attempt=attempt,
                expected_commit=GOOD_SHA,
                handoff_target=handoff.resolve(),
            )
            self.assertIn("GPU_ATTEMPT_CONTENT_DRIFT_SOURCE_HANDOFF_SHA256", blockers)

    def test_attempt_contract_drift_blocks_generation(self) -> None:
        ready = self._ready_pre_gpu()
        handoff_payload = self._ready_handoff()
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            root = Path(temp_dir)
            output = root / "canonical-output.json"
            receipt = root / "receipt.json"
            attestation = root / "attestation.json"
            summary = root / "summary.json"
            handoff = root / "handoff.json"
            attempt = root / "attempt.json"

            drifted_attempt = {
                "schema": "pul7sar-phase18-first-golden-gpu-attempt-contract-v1",
                "expected_commit": GOOD_SHA,
                "branch_required": "phase18/story-intelligence",
                "cost_mode_required": "$0-local",
                "offline_required": True,
                "attempt_contract_ready": True,
                "blockers": [],
                "workflow_dispatch_performed": False,
                "png_created": False,
                "source_handoff_sha256": "0" * 64,
                "canonical_workflow_sha256": sha256(ROOT / CANONICAL_WORKFLOW),
                "canonical_launcher_sha256": sha256(ROOT / CANONICAL_LAUNCHER),
                **CLOSED_AUTHORITIES,
            }

            with patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.run_attested_pre_gpu",
                return_value=ready,
            ), patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.build_gpu_handoff",
                return_value=handoff_payload,
            ), patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.build_gpu_attempt_contract",
                return_value=drifted_attempt,
            ), patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.subprocess.run"
            ) as generation:
                result = run(
                    expected_commit=GOOD_SHA,
                    output_path=output,
                    receipt_path=receipt,
                    attestation_path=attestation,
                    summary_path=summary,
                    handoff_path=handoff,
                    attempt_contract_path=attempt,
                )

            self.assertFalse(result["ready"])
            self.assertFalse(result["canonical_generation_started"])
            self.assertIn("GPU_ATTEMPT_CONTENT_DRIFT_SOURCE_HANDOFF_SHA256", result["blockers"])
            for field, expected in CLOSED_AUTHORITIES.items():
                self.assertIs(result.get(field), expected, field)
            self.assertTrue(attempt.is_file())
            generation.assert_not_called()

    def test_attempt_contract_path_participates_in_collision_guard(self) -> None:
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            root = Path(temp_dir)
            same = root / "same.json"
            with self.assertRaisesRegex(RuntimeError, "OUTPUT_PATH_COLLISION"):
                run(
                    expected_commit=GOOD_SHA,
                    output_path=root / "output.json",
                    receipt_path=root / "receipt.json",
                    attestation_path=root / "attestation.json",
                    summary_path=root / "summary.json",
                    handoff_path=same,
                    attempt_contract_path=same,
                )


if __name__ == "__main__":
    unittest.main()
