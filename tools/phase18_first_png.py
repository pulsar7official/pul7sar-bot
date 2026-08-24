#!/usr/bin/env python3
"""Prepare and execute the first genuine Phase 18 Golden Visual PNG in one command.

This command is intentionally an orchestration wrapper around existing trusted
boundaries. It does not add a new image-generation implementation and does not
weaken any gate. On a compatible GPU host it:

1. builds the deterministic Golden batch if needed,
2. verifies the complete batch SHA-256/canvas/cost contract,
3. qualifies the physical CUDA/BF16 host before downloads or queue mutation,
4. proves the exact local Qwen runtime/model are ready before FLUX preparation,
5. verifies/prefetches the exact approved FLUX.2 Klein snapshot,
6. proves CUDA + FLUX.2 Klein + native BF16 readiness,
7. prepares/reuses exactly one candidate-1 durable smoke job,
8. executes one normal GPU-worker cycle,
9. verifies that the durable job ended in `succeeded` and points to a real PNG.

On a CPU/incompatible host it fails before model download and before enqueueing
work. No placeholder PNG is ever created.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.generation_job_store import FilesystemGenerationJobStore
from engine.intelligence.generation_jobs import GenerationJobState
from engine.intelligence.golden_smoke import (
    DEFAULT_SMOKE_JOB_ID,
    load_first_candidate,
    prepare_smoke_job,
    smoke_status_payload,
)
from tools.phase18_build_golden_batch import build_batch
from tools.phase18_verify_golden_batch import verify_batch


EXPECTED_SEMANTIC_PREFLIGHT_SCHEMA = "pul7sar-phase18-semantic-gpu-preflight-v1"
EXPECTED_QWEN_MODEL_ID = "Qwen/Qwen2.5-VL-3B-Instruct"
EXPECTED_COST_MODE = "$0-local"


def _run_json_command(command: list[str], *, repository_root: Path, label: str) -> dict[str, object]:
    completed = subprocess.run(
        command,
        cwd=repository_root,
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"{label} did not emit valid JSON: " + (completed.stderr or completed.stdout)[-2000:]
        ) from exc
    if completed.returncode != 0:
        raise RuntimeError(
            f"{label} failed\n" + json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
        )
    return payload


def _run_host_qualification(repository_root: Path, receipt_path: Path) -> dict[str, object]:
    payload = _run_json_command(
        [
            sys.executable,
            str(repository_root / "tools" / "phase18_qualify_gpu_host.py"),
            "--output",
            str(receipt_path),
        ],
        repository_root=repository_root,
        label="GPU host qualification",
    )
    if payload.get("eligible") is not True:
        raise RuntimeError("GPU host qualification returned without eligible=true")
    return payload


def _run_semantic_preflight(
    repository_root: Path,
    receipt_path: Path,
    qwen_cache_receipt_path: Path,
    *,
    minimum_free_gib: float,
) -> dict[str, object]:
    payload = _run_json_command(
        [
            sys.executable,
            str(repository_root / "tools" / "phase18_preflight_semantic_gpu.py"),
            "--repository-root",
            str(repository_root),
            "--minimum-free-gib",
            str(minimum_free_gib),
            "--qwen-cache-receipt",
            str(qwen_cache_receipt_path),
            "--output",
            str(receipt_path),
        ],
        repository_root=repository_root,
        label="Semantic GPU preflight",
    )
    failures: list[str] = []
    if payload.get("schema") != EXPECTED_SEMANTIC_PREFLIGHT_SCHEMA:
        failures.append("semantic_preflight_schema_drift")
    if payload.get("model_id") != EXPECTED_QWEN_MODEL_ID:
        failures.append("semantic_preflight_qwen_model_drift")
    if payload.get("cost_mode") != EXPECTED_COST_MODE:
        failures.append("semantic_preflight_escaped_zero_cost_policy")
    if payload.get("semantic_runtime_ready") is not True:
        failures.append("semantic_runtime_not_ready")
    if payload.get("semantic_model_ready") is not True:
        failures.append("semantic_model_not_ready")
    if payload.get("cuda_available") is not True:
        failures.append("semantic_cuda_not_available")
    if payload.get("generation_authorized") is not False:
        failures.append("semantic_preflight_generation_authority_drift")
    if payload.get("queue_mutated") is not False:
        failures.append("semantic_preflight_queue_mutation_detected")
    if payload.get("png_created") is not False:
        failures.append("semantic_preflight_png_creation_detected")
    if payload.get("publication_ready") is not False:
        failures.append("semantic_preflight_publication_authority_drift")
    if failures:
        raise RuntimeError("SEMANTIC_GPU_PREFLIGHT_CONTRACT_FAILED: " + ", ".join(failures))
    return payload


def _run_model_prefetch(
    repository_root: Path,
    receipt_path: Path,
    *,
    minimum_free_gib: float,
) -> dict[str, object]:
    payload = _run_json_command(
        [
            sys.executable,
            str(repository_root / "tools" / "phase18_prefetch_flux2.py"),
            "--receipt",
            str(receipt_path),
            "--minimum-free-gib",
            str(minimum_free_gib),
        ],
        repository_root=repository_root,
        label="FLUX.2 model cache preflight",
    )
    if payload.get("ready") is not True:
        raise RuntimeError("FLUX.2 model cache preflight returned without ready=true")
    if payload.get("cost_mode") != EXPECTED_COST_MODE:
        raise RuntimeError("FLUX.2 model cache preflight escaped the $0-local policy")
    return payload


def _run_readiness(repository_root: Path) -> dict[str, object]:
    payload = _run_json_command(
        [sys.executable, str(repository_root / "tools" / "phase18_local_readiness.py")],
        repository_root=repository_root,
        label="Golden GPU readiness",
    )
    if payload.get("golden_generation_ready") is not True:
        raise RuntimeError("GOLDEN_GPU_NOT_READY\n" + json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return payload


def _run_worker_once(
    *,
    repository_root: Path,
    worker_id: str,
    queue_root: str,
    telemetry_root: str,
    generation_dir: str,
    proof_dir: str,
    timeout_seconds: int,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(repository_root / "tools" / "phase18_gpu_worker.py"),
        "--worker-id", worker_id,
        "--queue-root", queue_root,
        "--telemetry-root", telemetry_root,
        "--repository-root", str(repository_root),
        "--generation-dir", generation_dir,
        "--proof-dir", proof_dir,
        "--timeout-seconds", str(timeout_seconds),
        "--once",
    ]
    return subprocess.run(
        command,
        cwd=repository_root,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout_seconds + 120,
    )


def _resolve_output_path(repository_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repository_root / path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the first genuine PUL7SAR Phase 18 Golden PNG")
    parser.add_argument("--repository-root", default=str(ROOT))
    parser.add_argument("--batch-dir", default="output/phase18_handoffs/golden-batch")
    parser.add_argument("--queue-root", default="output/phase18_generation_queue")
    parser.add_argument("--telemetry-root", default="output/phase18_worker_telemetry")
    parser.add_argument("--generation-dir", default="output/phase18_generated")
    parser.add_argument("--proof-dir", default="output/phase18_visual_proof")
    parser.add_argument("--host-qualification-receipt", default="output/phase18_gpu_host/qualification.json")
    parser.add_argument("--semantic-preflight-receipt", default="output/phase18_gpu_smoke/semantic-preflight.json")
    parser.add_argument("--qwen-cache-receipt", default="output/phase18_gpu_smoke/qwen-model-cache.json")
    parser.add_argument("--model-cache-receipt", default="output/phase18_gpu_smoke/model-cache.json")
    parser.add_argument("--qwen-minimum-free-gib", type=float, default=12.0)
    parser.add_argument("--minimum-free-gib", type=float, default=30.0)
    parser.add_argument("--job-id", default=DEFAULT_SMOKE_JOB_ID)
    parser.add_argument("--worker-id", default="golden-smoke-worker-01")
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    args = parser.parse_args()

    repository_root = Path(args.repository_root).resolve()
    if not (repository_root / "engine" / "intelligence").is_dir():
        raise RuntimeError("repository-root does not contain the Phase 18 intelligence engine")
    if args.max_attempts <= 0:
        raise ValueError("max-attempts must be positive")
    if args.timeout_seconds <= 0:
        raise ValueError("timeout-seconds must be positive")
    if args.minimum_free_gib <= 0:
        raise ValueError("minimum-free-gib must be positive")
    if args.qwen_minimum_free_gib <= 0:
        raise ValueError("qwen-minimum-free-gib must be positive")

    batch_dir = _resolve_output_path(repository_root, args.batch_dir)
    manifest_path = batch_dir / "manifest.json"
    if not manifest_path.is_file():
        build_batch(str(batch_dir))
    integrity = verify_batch(str(manifest_path))
    candidate = load_first_candidate(manifest_path)

    # Fail closed in strict order. Hardware must be proven before any large model
    # download, semantic readiness must be proven before FLUX preparation, and
    # every generation prerequisite must pass before the durable queue is mutated.
    host_receipt_path = _resolve_output_path(repository_root, args.host_qualification_receipt)
    semantic_receipt_path = _resolve_output_path(repository_root, args.semantic_preflight_receipt)
    qwen_cache_receipt_path = _resolve_output_path(repository_root, args.qwen_cache_receipt)
    cache_receipt_path = _resolve_output_path(repository_root, args.model_cache_receipt)
    host_qualification = _run_host_qualification(repository_root, host_receipt_path)
    semantic_preflight = _run_semantic_preflight(
        repository_root,
        semantic_receipt_path,
        qwen_cache_receipt_path,
        minimum_free_gib=args.qwen_minimum_free_gib,
    )
    model_cache = _run_model_prefetch(
        repository_root,
        cache_receipt_path,
        minimum_free_gib=args.minimum_free_gib,
    )
    readiness = _run_readiness(repository_root)

    queue_root = _resolve_output_path(repository_root, args.queue_root)
    store = FilesystemGenerationJobStore(queue_root)
    preparation = prepare_smoke_job(
        store=store,
        candidate=candidate,
        job_id=args.job_id,
        max_attempts=args.max_attempts,
    )

    evidence = {
        "host_qualification_receipt": str(host_receipt_path),
        "semantic_preflight_receipt": str(semantic_receipt_path),
        "qwen_model_cache_receipt": str(qwen_cache_receipt_path),
        "model_cache_receipt": str(cache_receipt_path),
        "host_eligible": host_qualification.get("eligible"),
        "semantic_runtime_ready": semantic_preflight.get("semantic_runtime_ready"),
        "semantic_model_ready": semantic_preflight.get("semantic_model_ready"),
        "semantic_model_id": semantic_preflight.get("model_id"),
        "semantic_cost_mode": semantic_preflight.get("cost_mode"),
        "model_cache_ready": model_cache.get("ready"),
        "golden_generation_ready": readiness.get("golden_generation_ready"),
    }

    if preparation.job.state is GenerationJobState.SUCCEEDED:
        png = Path(preparation.job.result_path or "")
        if not png.is_absolute():
            png = repository_root / png
        if not png.is_file() or png.suffix.lower() != ".png":
            raise RuntimeError("existing succeeded smoke job does not point to a real PNG")
        print(json.dumps({
            "status": "FIRST_REAL_GOLDEN_PNG_ALREADY_EXISTS",
            "png": str(png),
            "integrity": integrity,
            "evidence": evidence,
            "readiness": readiness,
            "job": smoke_status_payload(preparation),
            "publication_ready": False,
        }, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    if preparation.job.state in {GenerationJobState.LEASED, GenerationJobState.RUNNING}:
        raise RuntimeError("candidate 1 smoke job is already active on a worker; refusing competing execution")

    completed = _run_worker_once(
        repository_root=repository_root,
        worker_id=args.worker_id,
        queue_root=str(queue_root),
        telemetry_root=args.telemetry_root,
        generation_dir=args.generation_dir,
        proof_dir=args.proof_dir,
        timeout_seconds=args.timeout_seconds,
    )
    final_job = store.get(args.job_id)
    if completed.returncode != 0:
        raise RuntimeError(
            "GPU worker smoke cycle failed\nstdout:\n"
            + completed.stdout[-4000:]
            + "\nstderr:\n"
            + completed.stderr[-4000:]
        )
    if final_job is None or final_job.state is not GenerationJobState.SUCCEEDED or not final_job.result_path:
        detail = {
            "worker_stdout_tail": completed.stdout[-4000:],
            "worker_stderr_tail": completed.stderr[-4000:],
            "final_job_state": final_job.state.value if final_job else None,
            "failure_code": final_job.failure_code if final_job else None,
            "failure_detail": final_job.failure_detail if final_job else None,
        }
        raise RuntimeError("worker returned without a successful real PNG job:\n" + json.dumps(detail, ensure_ascii=False, indent=2))

    png = Path(final_job.result_path)
    if not png.is_absolute():
        png = repository_root / png
    if not png.is_file() or png.suffix.lower() != ".png":
        raise RuntimeError("successful smoke job result is not an existing PNG")

    print(json.dumps({
        "status": "FIRST_REAL_GOLDEN_PNG_GENERATED",
        "png": str(png),
        "job_id": final_job.job_id,
        "request_id": final_job.request_id,
        "attempt": final_job.attempt,
        "payload_sha256": final_job.payload_sha256,
        "integrity": integrity,
        "evidence": evidence,
        "readiness": {
            "golden_generation_ready": readiness.get("golden_generation_ready"),
            "recommended_dtype": readiness.get("recommended_dtype"),
            "runtime": readiness.get("runtime"),
        },
        "worker_stdout_tail": completed.stdout[-4000:],
        "publication_ready": False,
        "publication_note": "Real generation success still requires semantic verification and Golden quality review.",
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
