#!/usr/bin/env python3
"""Measure pinned Qwen Image 2512 pipeline loadability in an isolated process.

The measurement intentionally performs no image inference.  Its only purpose is
to turn a successful Change Set 224 measurement admission into durable evidence
that the exact pinned local snapshot can be instantiated by the current
software/host stack without risking the parent orchestration process if the
child is OOM-killed.  Generation, Golden, semantic, and publication authority
remain closed regardless of the result.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import resource
import subprocess
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_REVISION
from engine.intelligence.qwen_image_runtime_measurement import (
    QwenImagePipelineLoadObservation,
    QwenImageRuntimeLoadMeasurement,
    sha256_file,
    verify_measurement_admission,
)


def _repo_path(path: str) -> Path:
    value = Path(path)
    if not value.is_absolute():
        value = ROOT / value
    value = value.resolve()
    if not value.is_relative_to(ROOT.resolve()):
        raise RuntimeError(f"QWEN_IMAGE_RUNTIME_MEASUREMENT_PATH_ESCAPE: {value}")
    return value


def _gib(value: int | float) -> float:
    return round(float(value) / (1024 ** 3), 4)


def _max_rss_gib() -> float:
    # Linux reports ru_maxrss in KiB. Phase 18 GPU hosts are Linux-only.
    return round(float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / (1024 ** 2), 4)


def _cuda_snapshot(torch: Any) -> dict[str, Any]:
    if not torch.cuda.is_available():
        raise RuntimeError("QWEN_IMAGE_RUNTIME_MEASUREMENT_CUDA_UNAVAILABLE")
    if not bool(torch.cuda.is_bf16_supported()):
        raise RuntimeError("QWEN_IMAGE_RUNTIME_MEASUREMENT_NATIVE_BF16_UNPROVEN")
    free_bytes, total_bytes = torch.cuda.mem_get_info()
    return {
        "gpu_name": str(torch.cuda.get_device_name(0)),
        "gpu_total_vram_gb": _gib(total_bytes),
        "gpu_free_vram_gb": _gib(free_bytes),
        "native_bf16": True,
    }


def _child(snapshot: Path, result_path: Path) -> int:
    started = time.monotonic()
    payload: dict[str, Any] = {
        "pipeline_load_succeeded": False,
        "pipeline_class": None,
        "torch_version": None,
        "cuda_version": None,
        "diffusers_version": None,
        "native_bf16": None,
        "gpu_name": None,
        "gpu_total_vram_gb": None,
        "gpu_free_vram_gb_before": None,
        "gpu_free_vram_gb_after": None,
        "max_cuda_allocated_gb": None,
        "max_cuda_reserved_gb": None,
        "process_max_rss_gb": None,
        "elapsed_seconds": None,
        "failure_type": None,
        "failure_message": None,
    }
    try:
        import torch
        import diffusers

        payload["torch_version"] = str(getattr(torch, "__version__", "") or "") or None
        payload["cuda_version"] = str(getattr(torch.version, "cuda", "") or "") or None
        payload["diffusers_version"] = str(getattr(diffusers, "__version__", "") or "") or None
        before = _cuda_snapshot(torch)
        payload.update({
            "native_bf16": before["native_bf16"],
            "gpu_name": before["gpu_name"],
            "gpu_total_vram_gb": before["gpu_total_vram_gb"],
            "gpu_free_vram_gb_before": before["gpu_free_vram_gb"],
        })
        pipeline_cls = getattr(diffusers, "QwenImagePipeline", None)
        if pipeline_cls is None:
            raise RuntimeError("QWEN_IMAGE_RUNTIME_MEASUREMENT_PIPELINE_CLASS_UNAVAILABLE")
        torch.cuda.reset_peak_memory_stats()
        pipe = pipeline_cls.from_pretrained(
            str(snapshot),
            torch_dtype=torch.bfloat16,
            local_files_only=True,
            low_cpu_mem_usage=True,
        )
        payload["pipeline_class"] = type(pipe).__name__
        payload["pipeline_load_succeeded"] = True
        free_after, _ = torch.cuda.mem_get_info()
        payload["gpu_free_vram_gb_after"] = _gib(free_after)
        payload["max_cuda_allocated_gb"] = _gib(torch.cuda.max_memory_allocated())
        payload["max_cuda_reserved_gb"] = _gib(torch.cuda.max_memory_reserved())
        del pipe
        torch.cuda.empty_cache()
    except BaseException as exc:  # child must preserve measurement failure evidence
        payload["failure_type"] = type(exc).__name__
        payload["failure_message"] = str(exc)[:2000]
    finally:
        payload["elapsed_seconds"] = round(time.monotonic() - started, 3)
        payload["process_max_rss_gb"] = _max_rss_gib()
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if payload["pipeline_load_succeeded"] else 2


def _observation_from_child(*, exit_code: int, child_result: dict[str, Any]) -> QwenImagePipelineLoadObservation:
    return QwenImagePipelineLoadObservation(
        child_exit_code=int(exit_code),
        pipeline_load_succeeded=bool(child_result.get("pipeline_load_succeeded")) and exit_code == 0,
        pipeline_class=child_result.get("pipeline_class"),
        torch_version=child_result.get("torch_version"),
        cuda_version=child_result.get("cuda_version"),
        diffusers_version=child_result.get("diffusers_version"),
        native_bf16=child_result.get("native_bf16") if isinstance(child_result.get("native_bf16"), bool) else None,
        gpu_name=child_result.get("gpu_name"),
        gpu_total_vram_gb=child_result.get("gpu_total_vram_gb"),
        gpu_free_vram_gb_before=child_result.get("gpu_free_vram_gb_before"),
        gpu_free_vram_gb_after=child_result.get("gpu_free_vram_gb_after"),
        max_cuda_allocated_gb=child_result.get("max_cuda_allocated_gb"),
        max_cuda_reserved_gb=child_result.get("max_cuda_reserved_gb"),
        process_max_rss_gb=child_result.get("process_max_rss_gb"),
        elapsed_seconds=child_result.get("elapsed_seconds"),
        failure_type=child_result.get("failure_type"),
        failure_message=child_result.get("failure_message"),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure isolated Qwen Image 2512 pipeline loadability without inference")
    parser.add_argument("--admission", help="Change Set 224 measurement-admission receipt")
    parser.add_argument("--receipt", default="output/phase18_gpu_smoke/qwen-image-2512-runtime-load-measurement.json")
    parser.add_argument("--child-result", default="output/phase18_gpu_smoke/qwen-image-2512-runtime-load-child.json")
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    parser.add_argument("--child-snapshot")
    parser.add_argument("--child-output")
    args = parser.parse_args()

    if args.child_snapshot or args.child_output:
        if not args.child_snapshot or not args.child_output:
            raise RuntimeError("QWEN_IMAGE_RUNTIME_MEASUREMENT_CHILD_ARGUMENTS_INCOMPLETE")
        snapshot = Path(args.child_snapshot).expanduser().resolve()
        if snapshot.name != QWEN_IMAGE_2512_REVISION:
            raise RuntimeError("QWEN_IMAGE_RUNTIME_MEASUREMENT_CHILD_REVISION_MISMATCH")
        return _child(snapshot, Path(args.child_output).expanduser().resolve())

    if not args.admission:
        raise RuntimeError("QWEN_IMAGE_RUNTIME_MEASUREMENT_ADMISSION_REQUIRED")
    admission_path = _repo_path(args.admission)
    admission = json.loads(admission_path.read_text(encoding="utf-8"))
    admission_sha = verify_measurement_admission(admission)
    snapshot = Path(str(admission["exact_snapshot_path"])).expanduser().resolve()

    child_result_path = _repo_path(args.child_result)
    child_result_path.parent.mkdir(parents=True, exist_ok=True)
    child_result_path.unlink(missing_ok=True)
    cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--child-snapshot",
        str(snapshot),
        "--child-output",
        str(child_result_path),
    ]
    try:
        completed = subprocess.run(cmd, cwd=str(ROOT), check=False, timeout=max(1, args.timeout_seconds))
        exit_code = int(completed.returncode)
    except subprocess.TimeoutExpired:
        exit_code = 124

    if child_result_path.is_file():
        child_result = json.loads(child_result_path.read_text(encoding="utf-8"))
    else:
        child_result = {
            "pipeline_load_succeeded": False,
            "failure_type": "ChildProcessTerminated",
            "failure_message": f"isolated measurement child exited without a receipt (exit_code={exit_code})",
        }
    observation = _observation_from_child(exit_code=exit_code, child_result=child_result)
    measurement = QwenImageRuntimeLoadMeasurement(
        admission_sha256=admission_sha,
        admission_file_sha256=sha256_file(admission_path),
        exact_snapshot_path=str(snapshot),
        observation=observation,
    )
    receipt = measurement.as_receipt()
    receipt_path = _repo_path(args.receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if receipt["pipeline_load_proven"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
