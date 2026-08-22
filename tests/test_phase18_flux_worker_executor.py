import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engine.intelligence.flux_worker_executor import Flux2SubprocessConfig, Flux2SubprocessLockedExecutor
from engine.intelligence.generation_jobs import GenerationJob
from engine.intelligence.local_backend_execution import LocalBackendGenerationRequest
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff


PROVIDER = "local-flux2-klein-4b"
MODEL = "black-forest-labs/FLUX.2-klein-4B"


class Flux2SubprocessLockedExecutorTests(unittest.TestCase):
    def _fixture(self, root: Path):
        request = LocalBackendGenerationRequest(
            provider_id=PROVIDER,
            model_id=MODEL,
            backend="diffusers",
            prompt="premium editorial football stadium scene",
            native_negative_constraints=("fake logos", "pseudo-text"),
            width=1088,
            height=1360,
            seed=7007001,
            request_id="golden-001",
            metadata={"cost_mode": "$0-local"},
        )
        handoff = root / "handoff.json"
        LocalGenerationHandoff.write(request, str(handoff))
        payload = json.loads(handoff.read_text(encoding="utf-8"))
        tool = root / "tools" / "phase18_flux2_execute.py"
        tool.parent.mkdir(parents=True)
        tool.write_text("# test stub\n", encoding="utf-8")
        job = GenerationJob(
            job_id="job-golden-001",
            request_id=request.request_id,
            handoff_path=str(handoff),
            payload_sha256=payload["payload_sha256"],
            provider_id=PROVIDER,
            model_id=MODEL,
            attempt=1,
        )
        return job

    def test_rejects_job_hash_drift_before_subprocess(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job = self._fixture(root)
            drifted = GenerationJob(
                job_id=job.job_id,
                request_id=job.request_id,
                handoff_path=job.handoff_path,
                payload_sha256="b" * 64,
                provider_id=job.provider_id,
                model_id=job.model_id,
                attempt=1,
            )
            executor = Flux2SubprocessLockedExecutor(Flux2SubprocessConfig(repository_root=str(root)))
            with self.assertRaises(ValueError):
                executor.execute(drifted)

    @patch("engine.intelligence.flux_worker_executor.subprocess.run")
    def test_success_requires_real_png_and_bfloat16(self, run_mock):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job = self._fixture(root)
            png = root / "proof.png"
            png.write_bytes(b"real-file-marker")

            def fake_run(command, **kwargs):
                result_path = Path(command[command.index("--result") + 1])
                result_path.parent.mkdir(parents=True, exist_ok=True)
                result_path.write_text(json.dumps({
                    "status": "REAL_VISUAL_PROOF_GENERATED",
                    "png": str(png),
                    "provider_id": PROVIDER,
                    "model_id": MODEL,
                    "request_id": job.request_id,
                    "resolved_dtype": "bfloat16",
                }), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

            run_mock.side_effect = fake_run
            executor = Flux2SubprocessLockedExecutor(Flux2SubprocessConfig(repository_root=str(root)))
            result = executor.execute(job)
            self.assertTrue(result.succeeded)
            self.assertEqual(result.result_path, str(png))
            self.assertEqual(result.payload_sha256, job.payload_sha256)

    @patch("engine.intelligence.flux_worker_executor.subprocess.run")
    def test_success_exit_without_result_file_fails_closed(self, run_mock):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job = self._fixture(root)
            run_mock.return_value = subprocess.CompletedProcess([], 0, stdout="ok", stderr="")
            executor = Flux2SubprocessLockedExecutor(Flux2SubprocessConfig(repository_root=str(root)))
            result = executor.execute(job)
            self.assertFalse(result.succeeded)
            self.assertEqual(result.failure_code, "executor_result_missing")
            self.assertFalse(result.retryable)

    @patch("engine.intelligence.flux_worker_executor.subprocess.run")
    def test_non_bfloat16_result_is_terminal_quality_failure(self, run_mock):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job = self._fixture(root)

            def fake_run(command, **kwargs):
                result_path = Path(command[command.index("--result") + 1])
                result_path.parent.mkdir(parents=True, exist_ok=True)
                result_path.write_text(json.dumps({
                    "status": "REAL_VISUAL_PROOF_GENERATED",
                    "png": "proof.png",
                    "provider_id": PROVIDER,
                    "model_id": MODEL,
                    "request_id": job.request_id,
                    "resolved_dtype": "float16",
                }), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

            run_mock.side_effect = fake_run
            executor = Flux2SubprocessLockedExecutor(Flux2SubprocessConfig(repository_root=str(root)))
            result = executor.execute(job)
            self.assertEqual(result.failure_code, "golden_dtype_drift")
            self.assertFalse(result.retryable)

    @patch("engine.intelligence.flux_worker_executor.subprocess.run")
    def test_cuda_oom_is_classified_retryable(self, run_mock):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job = self._fixture(root)
            run_mock.return_value = subprocess.CompletedProcess([], 1, stdout="", stderr="CUDA out of memory")
            executor = Flux2SubprocessLockedExecutor(Flux2SubprocessConfig(repository_root=str(root)))
            result = executor.execute(job)
            self.assertEqual(result.failure_code, "flux_execution_failed")
            self.assertTrue(result.retryable)

    @patch("engine.intelligence.flux_worker_executor.subprocess.run")
    def test_timeout_is_retryable(self, run_mock):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job = self._fixture(root)
            run_mock.side_effect = subprocess.TimeoutExpired(cmd="flux", timeout=10)
            executor = Flux2SubprocessLockedExecutor(Flux2SubprocessConfig(repository_root=str(root), timeout_seconds=10))
            result = executor.execute(job)
            self.assertEqual(result.failure_code, "executor_timeout")
            self.assertTrue(result.retryable)


if __name__ == "__main__":
    unittest.main()
