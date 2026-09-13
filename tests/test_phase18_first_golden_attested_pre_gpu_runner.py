from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import tools.phase18_run_first_golden_pre_gpu_attested as runner


SHA = "a" * 40


def _ready_receipt() -> dict[str, object]:
    return {
        "schema": "pul7sar-phase18-first-golden-pre-gpu-probe-v1",
        "ready_for_authoritative_golden_preflight": True,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def _ready_attestation() -> dict[str, object]:
    return {
        "schema": "pul7sar-phase18-first-golden-pre-gpu-attestation-v1",
        "receipt_attested": True,
        "ready_for_authoritative_golden_preflight": True,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


class FirstGoldenAttestedPreGpuRunnerTests(unittest.TestCase):
    def test_runner_writes_receipt_before_attestation_and_returns_ready(self) -> None:
        order: list[str] = []

        def fake_inspect(*, expected_commit: str) -> dict[str, object]:
            self.assertEqual(expected_commit, SHA)
            order.append("inspect")
            return _ready_receipt()

        def fake_attest(*, receipt_path: Path, expected_commit: str) -> dict[str, object]:
            self.assertEqual(expected_commit, SHA)
            self.assertTrue(receipt_path.is_file())
            order.append("attest")
            return _ready_attestation()

        with tempfile.TemporaryDirectory() as tmp, patch.object(runner, "ROOT", Path(tmp)), patch.object(
            runner, "inspect_pre_gpu", fake_inspect
        ), patch.object(runner, "attest", fake_attest):
            result = runner.run(
                expected_commit=SHA,
                receipt_path=Path("out/receipt.json"),
                attestation_path=Path("out/attestation.json"),
            )

        self.assertEqual(order, ["inspect", "attest"])
        self.assertIs(result["ready_for_authoritative_golden_preflight"], True)
        self.assertIs(result["receipt_attested"], True)
        self.assertEqual(result["blockers"], [])
        self.assertIs(result["generation_authorized"], False)
        self.assertIs(result["publication_ready"], False)
        self.assertIs(result["seeds_2_to_4_authorized"], False)

    def test_runner_fails_closed_when_pre_gpu_receipt_is_not_ready(self) -> None:
        receipt = _ready_receipt()
        receipt["ready_for_authoritative_golden_preflight"] = False

        with tempfile.TemporaryDirectory() as tmp, patch.object(runner, "ROOT", Path(tmp)), patch.object(
            runner, "inspect_pre_gpu", lambda **_: receipt
        ), patch.object(runner, "attest", lambda **_: _ready_attestation()):
            result = runner.run(
                expected_commit=SHA,
                receipt_path=Path("receipt.json"),
                attestation_path=Path("attestation.json"),
            )

        self.assertIs(result["ready_for_authoritative_golden_preflight"], False)
        self.assertIn("PRE_GPU_RECEIPT_NOT_READY", result["blockers"])

    def test_runner_fails_closed_when_attestation_does_not_verify(self) -> None:
        attestation = _ready_attestation()
        attestation["receipt_attested"] = False

        with tempfile.TemporaryDirectory() as tmp, patch.object(runner, "ROOT", Path(tmp)), patch.object(
            runner, "inspect_pre_gpu", lambda **_: _ready_receipt()
        ), patch.object(runner, "attest", lambda **_: attestation):
            result = runner.run(
                expected_commit=SHA,
                receipt_path=Path("receipt.json"),
                attestation_path=Path("attestation.json"),
            )

        self.assertIs(result["ready_for_authoritative_golden_preflight"], False)
        self.assertIn("PRE_GPU_RECEIPT_NOT_ATTESTED", result["blockers"])

    def test_runner_rejects_authority_drift(self) -> None:
        receipt = _ready_receipt()
        receipt["generation_authorized"] = True

        with tempfile.TemporaryDirectory() as tmp, patch.object(runner, "ROOT", Path(tmp)), patch.object(
            runner, "inspect_pre_gpu", lambda **_: receipt
        ), patch.object(runner, "attest", lambda **_: _ready_attestation()):
            result = runner.run(
                expected_commit=SHA,
                receipt_path=Path("receipt.json"),
                attestation_path=Path("attestation.json"),
            )

        self.assertIs(result["ready_for_authoritative_golden_preflight"], False)
        self.assertIn("RECEIPT_GENERATION_AUTHORITY_DRIFT", result["blockers"])

    def test_runner_rejects_invalid_expected_commit_without_running_probes(self) -> None:
        def forbidden(**_: object) -> dict[str, object]:
            raise AssertionError("probe must not run for invalid immutable commit")

        with tempfile.TemporaryDirectory() as tmp, patch.object(runner, "ROOT", Path(tmp)), patch.object(
            runner, "inspect_pre_gpu", forbidden
        ), patch.object(runner, "attest", forbidden):
            result = runner.run(
                expected_commit="not-a-sha",
                receipt_path=Path("receipt.json"),
                attestation_path=Path("attestation.json"),
            )

        self.assertIs(result["ready_for_authoritative_golden_preflight"], False)
        self.assertEqual(result["blockers"], ["EXPECTED_COMMIT_INVALID"])

    def test_runner_rejects_same_receipt_and_attestation_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, patch.object(runner, "ROOT", Path(tmp)):
            with self.assertRaisesRegex(RuntimeError, "MUST_DIFFER"):
                runner.run(
                    expected_commit=SHA,
                    receipt_path=Path("same.json"),
                    attestation_path=Path("same.json"),
                )

    def test_runner_rejects_output_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(runner, "ROOT", root):
                with self.assertRaisesRegex(RuntimeError, "ESCAPES_REPOSITORY"):
                    runner.run(
                        expected_commit=SHA,
                        receipt_path=root.parent / "outside.json",
                        attestation_path=Path("attestation.json"),
                    )


if __name__ == "__main__":
    unittest.main()
