"""Durable worker heartbeat and capacity telemetry for Phase 18 generation.

The first real Golden Visual must teach PUL7SAR how the selected GPU actually
behaves.  This module records observed worker state and measured generation
cycle durations without inventing throughput numbers before a real successful
GPU execution exists.

Telemetry is deliberately provider-neutral and publication-neutral: a generated
PNG is not counted as a publishable image unless later semantic and Golden
quality gates say so.  Capacity estimates here therefore describe raw generation
capacity only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable, Mapping


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _require_aware(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")


def _safe_component(value: str, name: str) -> str:
    safe = value.strip()
    if not safe or safe in {".", ".."} or "/" in safe or "\\" in safe:
        raise ValueError(f"{name} is unsafe for filesystem persistence")
    return safe


@dataclass(frozen=True)
class WorkerHeartbeat:
    worker_id: str
    observed_at: datetime
    status: str
    gpu_name: str | None
    vram_gb: float | None
    bf16_supported: bool
    queue_counts: Mapping[str, int] = field(default_factory=dict)
    current_job_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _safe_component(self.worker_id, "worker_id")
        _require_aware(self.observed_at, "observed_at")
        if not isinstance(self.status, str) or not self.status.strip():
            raise ValueError("status must be non-empty")
        if self.vram_gb is not None and self.vram_gb < 0:
            raise ValueError("vram_gb must be non-negative")
        counts = dict(self.queue_counts)
        if any(not isinstance(value, int) or value < 0 for value in counts.values()):
            raise ValueError("queue_counts values must be non-negative integers")
        object.__setattr__(self, "queue_counts", MappingProxyType(counts))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class GenerationPerformanceSample:
    worker_id: str
    job_id: str
    request_id: str | None
    started_at: datetime
    finished_at: datetime
    duration_seconds: float
    outcome: str
    result_path: str | None = None
    gpu_name: str | None = None
    vram_gb: float | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _safe_component(self.worker_id, "worker_id")
        _safe_component(self.job_id, "job_id")
        _require_aware(self.started_at, "started_at")
        _require_aware(self.finished_at, "finished_at")
        if self.finished_at < self.started_at:
            raise ValueError("finished_at cannot precede started_at")
        if not math.isfinite(self.duration_seconds) or self.duration_seconds < 0:
            raise ValueError("duration_seconds must be a finite non-negative number")
        if not isinstance(self.outcome, str) or not self.outcome.strip():
            raise ValueError("outcome must be non-empty")
        if self.vram_gb is not None and self.vram_gb < 0:
            raise ValueError("vram_gb must be non-negative")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def succeeded(self) -> bool:
        return self.outcome == "succeeded" and bool(self.result_path)


@dataclass(frozen=True)
class RawGenerationCapacityReport:
    successful_samples: int
    failed_samples: int
    worker_count: int
    utilization: float
    median_seconds_per_success: float | None
    p95_seconds_per_success: float | None
    estimated_images_per_hour: float | None
    estimated_images_per_day: float | None
    confidence: str
    blocker: str | None = None


class GenerationCapacityEstimator:
    """Estimate raw generation throughput only from real successful samples."""

    def estimate(
        self,
        samples: Iterable[GenerationPerformanceSample],
        *,
        worker_count: int = 1,
        utilization: float = 0.70,
    ) -> RawGenerationCapacityReport:
        if worker_count <= 0:
            raise ValueError("worker_count must be positive")
        if not 0 < utilization <= 1:
            raise ValueError("utilization must be in (0, 1]")
        all_samples = tuple(samples)
        successes = [sample.duration_seconds for sample in all_samples if sample.succeeded and sample.duration_seconds > 0]
        failures = len(all_samples) - len(successes)
        if not successes:
            return RawGenerationCapacityReport(
                successful_samples=0,
                failed_samples=failures,
                worker_count=worker_count,
                utilization=utilization,
                median_seconds_per_success=None,
                p95_seconds_per_success=None,
                estimated_images_per_hour=None,
                estimated_images_per_day=None,
                confidence="unproven",
                blocker="no real successful GPU generation sample has been recorded",
            )

        ordered = sorted(successes)
        median = self._percentile(ordered, 0.50)
        p95 = self._percentile(ordered, 0.95)
        per_hour = worker_count * utilization * 3600.0 / median
        per_day = per_hour * 24.0
        if len(successes) >= 20:
            confidence = "measured-high"
        elif len(successes) >= 5:
            confidence = "measured-medium"
        else:
            confidence = "measured-low"
        return RawGenerationCapacityReport(
            successful_samples=len(successes),
            failed_samples=failures,
            worker_count=worker_count,
            utilization=utilization,
            median_seconds_per_success=median,
            p95_seconds_per_success=p95,
            estimated_images_per_hour=per_hour,
            estimated_images_per_day=per_day,
            confidence=confidence,
        )

    @staticmethod
    def _percentile(ordered: list[float], quantile: float) -> float:
        if len(ordered) == 1:
            return ordered[0]
        position = (len(ordered) - 1) * quantile
        lower = math.floor(position)
        upper = math.ceil(position)
        if lower == upper:
            return ordered[lower]
        fraction = position - lower
        return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


class FilesystemWorkerTelemetryStore:
    """Dependency-free telemetry persistence for one or more filesystem workers."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.heartbeats_dir = self.root / "heartbeats"
        self.samples_dir = self.root / "samples"
        self.heartbeats_dir.mkdir(parents=True, exist_ok=True)
        self.samples_dir.mkdir(parents=True, exist_ok=True)

    def write_heartbeat(self, heartbeat: WorkerHeartbeat) -> Path:
        worker_id = _safe_component(heartbeat.worker_id, "worker_id")
        target = self.heartbeats_dir / f"{worker_id}.json"
        self._atomic_json(target, self._heartbeat_payload(heartbeat))
        return target

    def read_heartbeat(self, worker_id: str) -> WorkerHeartbeat | None:
        safe = _safe_component(worker_id, "worker_id")
        path = self.heartbeats_dir / f"{safe}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return WorkerHeartbeat(
            worker_id=str(data["worker_id"]),
            observed_at=datetime.fromisoformat(str(data["observed_at"])),
            status=str(data["status"]),
            gpu_name=data.get("gpu_name"),
            vram_gb=float(data["vram_gb"]) if data.get("vram_gb") is not None else None,
            bf16_supported=bool(data["bf16_supported"]),
            queue_counts=dict(data.get("queue_counts") or {}),
            current_job_id=data.get("current_job_id"),
            metadata=dict(data.get("metadata") or {}),
        )

    def record_sample(self, sample: GenerationPerformanceSample) -> Path:
        worker = _safe_component(sample.worker_id, "worker_id")
        job = _safe_component(sample.job_id, "job_id")
        stamp = sample.finished_at.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        target = self.samples_dir / f"{stamp}__{worker}__{job}.json"
        self._write_exclusive_json(target, self._sample_payload(sample))
        return target

    def iter_samples(self) -> Iterable[GenerationPerformanceSample]:
        for path in sorted(self.samples_dir.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            yield GenerationPerformanceSample(
                worker_id=str(data["worker_id"]),
                job_id=str(data["job_id"]),
                request_id=data.get("request_id"),
                started_at=datetime.fromisoformat(str(data["started_at"])),
                finished_at=datetime.fromisoformat(str(data["finished_at"])),
                duration_seconds=float(data["duration_seconds"]),
                outcome=str(data["outcome"]),
                result_path=data.get("result_path"),
                gpu_name=data.get("gpu_name"),
                vram_gb=float(data["vram_gb"]) if data.get("vram_gb") is not None else None,
                metadata=dict(data.get("metadata") or {}),
            )

    @staticmethod
    def _heartbeat_payload(value: WorkerHeartbeat) -> dict[str, object]:
        return {
            "worker_id": value.worker_id,
            "observed_at": value.observed_at.isoformat(),
            "status": value.status,
            "gpu_name": value.gpu_name,
            "vram_gb": value.vram_gb,
            "bf16_supported": value.bf16_supported,
            "queue_counts": dict(value.queue_counts),
            "current_job_id": value.current_job_id,
            "metadata": dict(value.metadata),
        }

    @staticmethod
    def _sample_payload(value: GenerationPerformanceSample) -> dict[str, object]:
        return {
            "worker_id": value.worker_id,
            "job_id": value.job_id,
            "request_id": value.request_id,
            "started_at": value.started_at.isoformat(),
            "finished_at": value.finished_at.isoformat(),
            "duration_seconds": value.duration_seconds,
            "outcome": value.outcome,
            "result_path": value.result_path,
            "gpu_name": value.gpu_name,
            "vram_gb": value.vram_gb,
            "metadata": dict(value.metadata),
        }

    @staticmethod
    def _write_exclusive_json(path: Path, payload: dict[str, object]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
        except Exception:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
            raise

    @staticmethod
    def _atomic_json(path: Path, payload: dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(tmp, path)
