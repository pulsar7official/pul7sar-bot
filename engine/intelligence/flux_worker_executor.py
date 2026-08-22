"""Locked subprocess adapter from the generic GPU worker to FLUX.2 execution.

The worker never shells out with prompt/model parameters. It passes only the
already SHA-256-locked handoff path plus controlled output paths and dtype, then
validates the dedicated result JSON before returning it to GenerationWorkerService.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys

from engine.intelligence.generation_jobs import GenerationJob
from engine.intelligence.generation_worker import WorkerExecutionResult
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff


_TRANSIENT_MARKERS = (
    "cuda out of memory",
    "out of memory",
    "temporarily unavailable",
    "resource exhausted",
    "connection reset",
    "timeout",
)


@dataclass(frozen=True)
class Flux2SubprocessConfig:
    repository_root: str = "."
    generation_dir: str = "output/phase18_generated"
    proof_dir: str = "output/phase18_visual_proof"
    dtype: str = "auto"
    python_executable: str = sys.executable
    timeout_seconds: int = 1800

    def __post_init__(self) -> None:
        if self.dtype not in {"auto", "bfloat16"}:
            raise ValueError("Golden FLUX executor accepts only auto or bfloat16")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


class Flux2SubprocessLockedExecutor:
    """Production-shaped adapter for one real locked FLUX.2 request."""

    def __init__(self, config: Flux2SubprocessConfig | None = None) -> None:
        self.config = config or Flux2SubprocessConfig()

    def execute(self, job: GenerationJob) -> WorkerExecutionResult:
        handoff_path = Path(job.handoff_path)
        if not handoff_path.is_absolute():
            handoff_path = Path(self.config.repository_root) / handoff_path
        handoff_path = handoff_path.resolve()
        try:
            self._validate_handoff(job, handoff_path)
        except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError) as exc:
            # Integrity/identity failures must never become the worker service's
            # generic retryable executor_exception path.
            return self._failure(job, "handoff_integrity_failure", str(exc), retryable=False)

        tool = (Path(self.config.repository_root) / "tools" / "phase18_flux2_execute.py").resolve()
        if not tool.is_file():
            return self._failure(job, "executor_tool_missing", f"missing executor: {tool}", retryable=False)

        result_root = Path(self.config.repository_root) / "output" / "phase18_worker_results"
        result_root.mkdir(parents=True, exist_ok=True)
        result_path = result_root / f"{job.job_id}-attempt-{job.attempt}.json"

        command = [
            self.config.python_executable,
            str(tool),
            "--request",
            str(handoff_path),
            "--generation-dir",
            self.config.generation_dir,
            "--proof-dir",
            self.config.proof_dir,
            "--dtype",
            self.config.dtype,
            "--result",
            str(result_path),
        ]
        try:
            completed = subprocess.run(
                command,
                cwd=self.config.repository_root,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return self._failure(job, "executor_timeout", str(exc), retryable=True)
        except OSError as exc:
            return self._failure(job, "executor_spawn_failed", str(exc), retryable=True)

        if completed.returncode != 0:
            detail = self._bounded_detail(completed.stderr or completed.stdout)
            return self._failure(
                job,
                "flux_execution_failed",
                detail or f"executor exited with status {completed.returncode}",
                retryable=self._looks_transient(detail),
            )
        if not result_path.is_file():
            return self._failure(job, "executor_result_missing", "FLUX executor returned success without result JSON", retryable=False)

        try:
            payload = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return self._failure(job, "executor_result_invalid", str(exc), retryable=False)

        if payload.get("status") != "REAL_VISUAL_PROOF_GENERATED":
            return self._failure(job, "visual_proof_status_invalid", "executor did not report a real visual proof", retryable=False)
        if payload.get("resolved_dtype") != "bfloat16":
            return self._failure(job, "golden_dtype_drift", "real proof did not remain on bfloat16", retryable=False)

        png = payload.get("png")
        if not isinstance(png, str) or not png.strip():
            return self._failure(job, "visual_proof_path_missing", "real proof result has no PNG path", retryable=False)
        png_path = Path(png)
        if not png_path.is_absolute():
            png_path = Path(self.config.repository_root) / png_path
        if not png_path.is_file():
            return self._failure(job, "visual_proof_file_missing", f"result PNG does not exist: {png}", retryable=False)

        return WorkerExecutionResult(
            request_id=str(payload.get("request_id", "")),
            payload_sha256=job.payload_sha256,
            provider_id=str(payload.get("provider_id", "")),
            model_id=str(payload.get("model_id", "")),
            result_path=str(png),
        )

    @staticmethod
    def _validate_handoff(job: GenerationJob, path: Path) -> None:
        if not path.is_file():
            raise FileNotFoundError(f"generation handoff does not exist: {path}")
        raw = json.loads(path.read_text(encoding="utf-8"))
        supplied = raw.get("payload_sha256")
        if supplied != job.payload_sha256:
            raise ValueError("job payload_sha256 does not match handoff payload_sha256")
        request = LocalGenerationHandoff.read(str(path))
        if request.request_id != job.request_id:
            raise ValueError("job request_id does not match locked handoff")
        if request.provider_id != job.provider_id or request.model_id != job.model_id:
            raise ValueError("job provider/model does not match locked handoff")

    @staticmethod
    def _failure(job: GenerationJob, code: str, detail: str, *, retryable: bool) -> WorkerExecutionResult:
        return WorkerExecutionResult(
            request_id=job.request_id,
            payload_sha256=job.payload_sha256,
            provider_id=job.provider_id,
            model_id=job.model_id,
            result_path=None,
            retryable=retryable,
            failure_code=code,
            failure_detail=detail,
        )

    @staticmethod
    def _looks_transient(detail: str) -> bool:
        lowered = detail.lower()
        return any(marker in lowered for marker in _TRANSIENT_MARKERS)

    @staticmethod
    def _bounded_detail(detail: str, limit: int = 4000) -> str:
        text = (detail or "").strip()
        return text[-limit:]
