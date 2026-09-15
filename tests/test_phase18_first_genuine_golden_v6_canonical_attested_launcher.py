from pathlib import Path
import hashlib
import json
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
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class FirstGenuineGoldenV6CanonicalAttestedLauncherTests(unittest.TestCase):
    def _paths(self, root: Path) -> tuple[Path, Path, Path, Path, Path]:
        return (
            root / "canonical-output.json",
            root / "pre-gpu-receipt.json",
            root / "pre-gpu-attestation.json",
            root / "pre-gpu-summary.json",
            root / "gpu-handoff.json",
        )

    def assert_authorities_closed(self, result: dict[str, object]) -> None:
        for field, expected in CLOSED_AUTHORITIES.items():
            self.assertIs(result.get(field), expected, field)

    def _ready_pre_gpu(self) -> dict[str, object]:
        return {
            "schema": "pul7sar-phase18-first-golden-attested-pre-gpu-run-v1",
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

    def _write_valid_resource_lock(self, output: Path) -> tuple[Path, str]:
        png = output.parent / "candidate-01.png"
        png.write_bytes(PNG_SIGNATURE + b"phase18-genuine-golden-candidate")
        png_sha = hashlib.sha256(png.read_bytes()).hexdigest()
        payload = {
            "schema": "pul7sar-first-genuine-golden-v6-resource-lock-v4",
            "status": "FIRST_GENUINE_GOLDEN_V6_MODEL_CACHE_RESOURCE_RUNTIME_SEMANTIC_LOCK_VERIFIED",
            "branch": "phase18/story-intelligence",
            "candidate": 1,
            "cost_mode": "$0-local",
            "gpu_eligible": True,
            "native_bf16_proven": True,
            "network_download_authorized": False,
            "local_files_only": True,
            "semantic_preflight_bound": True,
            "runtime_stable_across_generation": True,
            "png": str(png.resolve()),
            "png_sha256": png_sha,
            "png_bytes": png.stat().st_size,
            "human_visual_review_required": True,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        output.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        return png.resolve(), png_sha

    def test_invalid_commit_fails_before_pre_gpu_handoff_or_generation(self) -> None:
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            output, receipt, attestation, summary, handoff = self._paths(Path(temp_dir))
            with patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.run_attested_pre_gpu"
            ) as pre_gpu, patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.build_gpu_handoff"
            ) as gpu_handoff, patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.subprocess.run"
            ) as generation:
                result = run(
                    expected_commit="not-a-sha",
                    output_path=output,
                    receipt_path=receipt,
                    attestation_path=attestation,
                    summary_path=summary,
                    handoff_path=handoff,
                )
            self.assertFalse(result["ready"])
            self.assertFalse(result["canonical_generation_started"])
            self.assertIn("EXPECTED_COMMIT_INVALID", result["blockers"])
            self.assert_authorities_closed(result)
            pre_gpu.assert_not_called()
            gpu_handoff.assert_not_called()
            generation.assert_not_called()

    def test_pre_gpu_failure_blocks_handoff_and_canonical_generation(self) -> None:
        failed = {
            "schema": "pul7sar-phase18-first-golden-attested-pre-gpu-run-v1",
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
            output, receipt, attestation, summary, handoff = self._paths(Path(temp_dir))
            with patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.run_attested_pre_gpu",
                return_value=failed,
            ), patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.build_gpu_handoff"
            ) as gpu_handoff, patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.subprocess.run"
            ) as generation:
                result = run(
                    expected_commit=GOOD_SHA,
                    output_path=output,
                    receipt_path=receipt,
                    attestation_path=attestation,
                    summary_path=summary,
                    handoff_path=handoff,
                )
            self.assertFalse(result["ready"])
            self.assertFalse(result["canonical_generation_started"])
            self.assert_authorities_closed(result)
            gpu_handoff.assert_not_called()
            generation.assert_not_called()
            self.assertTrue(summary.is_file())
            self.assertFalse(handoff.exists())

    def test_authority_drift_blocks_handoff_and_canonical_generation(self) -> None:
        drifted = self._ready_pre_gpu()
        drifted["generation_authorized"] = True
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            output, receipt, attestation, summary, handoff = self._paths(Path(temp_dir))
            with patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.run_attested_pre_gpu",
                return_value=drifted,
            ), patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.build_gpu_handoff"
            ) as gpu_handoff, patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.subprocess.run"
            ) as generation:
                result = run(
                    expected_commit=GOOD_SHA,
                    output_path=output,
                    receipt_path=receipt,
                    attestation_path=attestation,
                    summary_path=summary,
                    handoff_path=handoff,
                )
            self.assertFalse(result["ready"])
            self.assertIn("ATTESTED_PRE_GPU_AUTHORITY_DRIFT_GENERATION_AUTHORIZED", result["blockers"])
            self.assert_authorities_closed(result)
            gpu_handoff.assert_not_called()
            generation.assert_not_called()

    def test_handoff_failure_blocks_canonical_generation(self) -> None:
        ready = self._ready_pre_gpu()
        blocked_handoff = {
            "schema": "pul7sar-phase18-first-golden-gpu-handoff-v1",
            "expected_commit": GOOD_SHA,
            "branch_required": "phase18/story-intelligence",
            "cost_mode_required": "$0-local",
            "offline_required": True,
            "eligible_for_authoritative_golden_preflight": False,
            "blockers": ["HOST_READINESS_WORKFLOW_MISSING"],
            **CLOSED_AUTHORITIES,
        }
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            output, receipt, attestation, summary, handoff = self._paths(Path(temp_dir))
            with patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.run_attested_pre_gpu",
                return_value=ready,
            ), patch(
                "tools.phase18_run_first_genuine_golden_v6_canonical_attested.build_gpu_handoff",
                return_value=blocked_handoff,
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
                )
            self.assertFalse(result["ready"])
            self.assertFalse(result["canonical_generation_started"])
            self.assertIn("GPU_HANDOFF_NOT_ELIGIBLE", result["blockers"])
            self.assertIn("GPU_HANDOFF_BLOCKERS_REMAIN", result["blockers"])
            self.assert_authorities_closed(result)
            self.assertTrue(handoff.is_file())
            generation.assert_not_called()

    def test_ready_pre_gpu_builds_handoff_and_replays_valid_output(self) -> None:
        ready = self._ready_pre_gpu()
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            output, receipt, attestation, summary, handoff = self._paths(Path(temp_dir))
            captured: dict[str, object] = {}

            def fake_generation(command, cwd, check):
                self.assertTrue(check)
                self.assertEqual(cwd, Path(__file__).resolve().parents[1])
                self.assertTrue(handoff.is_file(), "GPU handoff must exist before generation starts")
                self.assertIn("phase18_colab_first_genuine_resources_locked.py", command[1])
                self.assertEqual(command[-2], "--output")
                png, png_sha = self._write_valid_resource_lock(Path(command[-1]))
                captured["png"] = png
                captured["png_sha"] = png_sha

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
                    handoff_path=handoff,
                )
            self.assertTrue(result["ready"])
            self.assertTrue(result["canonical_generation_started"])
            self.assertEqual(Path(str(result["gpu_handoff"])), handoff.resolve())
            self.assertEqual(Path(str(result["canonical_png"])), captured["png"])
            self.assertEqual(result["canonical_png_sha256"], captured["png_sha"])
            self.assertEqual(result["blockers"], [])
            self.assert_authorities_closed(result)
            self.assertTrue(handoff.is_file())
            generation.assert_called_once()

    def test_generation_returning_unverified_resource_lock_is_not_ready(self) -> None:
        ready = self._ready_pre_gpu()
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            output, receipt, attestation, summary, handoff = self._paths(Path(temp_dir))

            def fake_generation(command, cwd, check):
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
                    handoff_path=handoff,
                )
            self.assertTrue(result["canonical_generation_started"])
            self.assertFalse(result["ready"])
            self.assertIn("CANONICAL_OUTPUT_SCHEMA_DRIFT", result["blockers"])
            self.assertIn("CANONICAL_OUTPUT_PNG_PATH_MISSING", result["blockers"])
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
                    handoff_path=root / "handoff.json",
                )


if __name__ == "__main__":
    unittest.main()
