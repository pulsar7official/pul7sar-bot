from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.phase18_run_first_genuine_golden_v6_canonical_attested import run


GOOD_SHA = "a" * 40
CLOSED_AUTHORITIES = {
    "authoritative_gate": False,
    "network_download_authorized": False,
    "generation_authorized": False,
    "publication_ready": False,
    "seeds_2_to_4_authorized": False,
}


class FirstGenuineGoldenV6CanonicalAttestedLauncherTests(unittest.TestCase):
    def _paths(self, root: Path) -> tuple[Path, Path, Path, Path]:
        return (
            root / "canonical-output.json",
            root / "pre-gpu-receipt.json",
            root / "pre-gpu-attestation.json",
            root / "pre-gpu-summary.json",
        )

    def assert_authorities_closed(self, result: dict[str, object]) -> None:
        for field, expected in CLOSED_AUTHORITIES.items():
            self.assertIs(result.get(field), expected, field)

    def test_invalid_commit_fails_before_pre_gpu_or_generation(self) -> None:
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            output, receipt, attestation, summary = self._paths(Path(temp_dir))
            with patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.run_attested_pre_gpu"
            ) as pre_gpu, patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.subprocess.run"
            ) as generation:
                result = run(
                    expected_commit="not-a-sha",
                    output_path=output,
                    receipt_path=receipt,
                    attestation_path=attestation,
                    summary_path=summary,
                )
            self.assertFalse(result["ready"])
            self.assertFalse(result["canonical_generation_started"])
            self.assertIn("EXPECTED_COMMIT_INVALID", result["blockers"])
            self.assert_authorities_closed(result)
            pre_gpu.assert_not_called()
            generation.assert_not_called()

    def test_pre_gpu_failure_blocks_canonical_generation(self) -> None:
        failed = {
            "expected_commit": GOOD_SHA,
            "ready_for_authoritative_golden_preflight": False,
            "receipt_attested": False,
            "blockers": ["CUDA_NOT_AVAILABLE"],
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            output, receipt, attestation, summary = self._paths(Path(temp_dir))
            with patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.run_attested_pre_gpu",
                return_value=failed,
            ), patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.subprocess.run"
            ) as generation:
                result = run(
                    expected_commit=GOOD_SHA,
                    output_path=output,
                    receipt_path=receipt,
                    attestation_path=attestation,
                    summary_path=summary,
                )
            self.assertFalse(result["ready"])
            self.assertFalse(result["canonical_generation_started"])
            self.assert_authorities_closed(result)
            generation.assert_not_called()
            self.assertTrue(summary.is_file())

    def test_authority_drift_blocks_canonical_generation(self) -> None:
        drifted = {
            "expected_commit": GOOD_SHA,
            "ready_for_authoritative_golden_preflight": True,
            "receipt_attested": True,
            "blockers": [],
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": True,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            output, receipt, attestation, summary = self._paths(Path(temp_dir))
            with patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.run_attested_pre_gpu",
                return_value=drifted,
            ), patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.subprocess.run"
            ) as generation:
                result = run(
                    expected_commit=GOOD_SHA,
                    output_path=output,
                    receipt_path=receipt,
                    attestation_path=attestation,
                    summary_path=summary,
                )
            self.assertFalse(result["ready"])
            self.assertIn("ATTESTED_PRE_GPU_AUTHORITY_DRIFT_GENERATION_AUTHORIZED", result["blockers"])
            self.assert_authorities_closed(result)
            generation.assert_not_called()

    def test_ready_pre_gpu_delegates_to_existing_canonical_entrypoint(self) -> None:
        ready = {
            "expected_commit": GOOD_SHA,
            "ready_for_authoritative_golden_preflight": True,
            "receipt_attested": True,
            "blockers": [],
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            output, receipt, attestation, summary = self._paths(Path(temp_dir))

            def fake_generation(command, cwd, check):
                self.assertTrue(check)
                self.assertEqual(cwd, Path(__file__).resolve().parents[1])
                self.assertIn("phase18_colab_first_genuine_resources_locked.py", command[1])
                self.assertEqual(command[-2], "--output")
                Path(command[-1]).write_text("{}\n", encoding="utf-8")

            with patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.run_attested_pre_gpu",
                return_value=ready,
            ), patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.subprocess.run",
                side_effect=fake_generation,
            ) as generation:
                result = run(
                    expected_commit=GOOD_SHA,
                    output_path=output,
                    receipt_path=receipt,
                    attestation_path=attestation,
                    summary_path=summary,
                )
            self.assertTrue(result["ready"])
            self.assertTrue(result["canonical_generation_started"])
            self.assert_authorities_closed(result)
            generation.assert_called_once()

    def test_output_paths_must_be_distinct(self) -> None:
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            root = Path(temp_dir)
            same = root / "same.json"
            with self.assertRaisesRegex(RuntimeError, "OUTPUT_PATH_COLLISION"):
                run(
                    expected_commit=GOOD_SHA,
                    output_path=same,
                    receipt_path=same,
                    attestation_path=root / "attestation.json",
                    summary_path=root / "summary.json",
                )


if __name__ == "__main__":
    unittest.main()
