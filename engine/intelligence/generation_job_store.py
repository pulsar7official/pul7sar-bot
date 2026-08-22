"""Durable filesystem queue adapter for Phase 18 generation jobs.

This adapter is intentionally dependency-free so the first production-shaped GPU
worker can run on a single host before Redis/SQS is introduced.  State is encoded
by directory and every claim uses an atomic rename, preventing two workers on the
same filesystem from leasing the same queued job.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import json
import os
from pathlib import Path
from typing import Iterable

from engine.intelligence.generation_jobs import (
    GenerationJob,
    GenerationJobState,
    GenerationWorkerCapabilities,
)


_STATE_DIRS = {
    GenerationJobState.QUEUED: "queued",
    GenerationJobState.LEASED: "leased",
    GenerationJobState.RUNNING: "running",
    GenerationJobState.SUCCEEDED: "succeeded",
    GenerationJobState.RETRYABLE_FAILED: "retryable_failed",
    GenerationJobState.TERMINAL_FAILED: "terminal_failed",
}


class FilesystemGenerationJobStore:
    """Single-filesystem durable queue with atomic leasing.

    It is suitable for one machine or multiple worker processes sharing the same
    mounted filesystem.  It is not presented as a distributed-database substitute;
    the GenerationJobStore protocol remains backend-neutral for a later Redis/SQS
    adapter.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        for dirname in _STATE_DIRS.values():
            (self.root / dirname).mkdir(parents=True, exist_ok=True)

    def enqueue(self, job: GenerationJob) -> None:
        if job.state is not GenerationJobState.QUEUED:
            raise ValueError("only queued jobs can be enqueued")
        target = self._path(job.state, job.job_id)
        if self._find_existing(job.job_id) is not None:
            raise FileExistsError(f"generation job already exists: {job.job_id}")
        self._write_exclusive(target, job)

    def lease_next(
        self,
        *,
        worker: GenerationWorkerCapabilities,
        lease_until: datetime,
    ) -> GenerationJob | None:
        queued_dir = self.root / _STATE_DIRS[GenerationJobState.QUEUED]
        for source in sorted(queued_dir.glob("*.json")):
            try:
                job = self._read(source)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if job.state is not GenerationJobState.QUEUED:
                continue
            if not worker.supports(job, require_bf16=True):
                continue

            claim = self._path(GenerationJobState.LEASED, job.job_id)
            try:
                os.replace(source, claim)
            except FileNotFoundError:
                # Another worker claimed it first.
                continue

            leased = job.transition(
                GenerationJobState.LEASED,
                lease_owner=worker.worker_id,
                lease_expires_at=lease_until,
            )
            self._atomic_write(claim, leased)
            return leased
        return None

    def save(self, job: GenerationJob) -> None:
        target = self._path(job.state, job.job_id)
        existing = self._find_existing(job.job_id)
        self._atomic_write(target, job)
        if existing is not None and existing != target:
            try:
                existing.unlink()
            except FileNotFoundError:
                pass

    def get(self, job_id: str) -> GenerationJob | None:
        existing = self._find_existing(job_id)
        return self._read(existing) if existing is not None else None

    def iter_state(self, state: GenerationJobState) -> Iterable[GenerationJob]:
        directory = self.root / _STATE_DIRS[state]
        for path in sorted(directory.glob("*.json")):
            yield self._read(path)

    def _find_existing(self, job_id: str) -> Path | None:
        matches = [self._path(state, job_id) for state in GenerationJobState]
        existing = [path for path in matches if path.exists()]
        if len(existing) > 1:
            raise RuntimeError(f"generation job exists in multiple states: {job_id}")
        return existing[0] if existing else None

    def _path(self, state: GenerationJobState, job_id: str) -> Path:
        safe = job_id.strip()
        if not safe or safe in {".", ".."} or "/" in safe or "\\" in safe:
            raise ValueError("job_id is unsafe for filesystem persistence")
        return self.root / _STATE_DIRS[state] / f"{safe}.json"

    @staticmethod
    def _serialize(job: GenerationJob) -> dict[str, object]:
        data = asdict(job)
        data["state"] = job.state.value
        for field in ("created_at", "updated_at", "lease_expires_at"):
            value = getattr(job, field)
            data[field] = value.isoformat() if value is not None else None
        data["metadata"] = dict(job.metadata)
        return data

    @staticmethod
    def _deserialize(data: dict[str, object]) -> GenerationJob:
        values = dict(data)
        values["state"] = GenerationJobState(str(values["state"]))
        for field in ("created_at", "updated_at", "lease_expires_at"):
            value = values.get(field)
            values[field] = datetime.fromisoformat(str(value)) if value is not None else None
        return GenerationJob(**values)

    def _read(self, path: Path) -> GenerationJob:
        return self._deserialize(json.loads(path.read_text(encoding="utf-8")))

    def _write_exclusive(self, path: Path, job: GenerationJob) -> None:
        payload = json.dumps(self._serialize(job), ensure_ascii=False, indent=2, sort_keys=True)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        except Exception:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
            raise

    def _atomic_write(self, path: Path, job: GenerationJob) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
        tmp.write_text(
            json.dumps(self._serialize(job), ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        os.replace(tmp, path)
