#!/usr/bin/env python3
"""Run one isolated, identity-neutral Qwen Image 2512 inference probe.

This is a measurement tool, not canonical generation. It requires a successful
Change Set 225 pipeline-load receipt, reuses the exact pinned local snapshot,
forces sequential CPU offload, emits one 512x512 engineering PNG, and preserves
all Golden/semantic/publication authority as closed.
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
from engine.intelligence.qwen_image_inference_measurement import (
    PROBE_GUIDANCE_SCALE,
    PROBE_HEIGHT,
    PROBE_OFFLOAD_MODE,
    PROBE_PROMPT,
    PROBE_SEED,
    PROBE_STEPS,
    PROBE_WIDTH,
    QwenImageInferenceMeasurement,
    QwenImageInferenceObservation,
    sha256_file,
    verify_load_measurement_for_inference,
)


def _repo_path(path: str) -> Path:
    value = Path(path)
    if not value.is_absolute():
        value = ROOT / value
    value = value.resolve()
    if not value.is_relative_to(ROOT.resolve()):
        raise RuntimeError(f"QWEN_IMAGE_INFERENCE_MEASUREMENT_PATH_ESCAPE: {value}")
    return value


def _gib(value: int | float) -> float:
    return round(float(value) / (1024 ** 3), 4)


def _max_rss_gib() -> float:
    return round(float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / (1024 ** 2), 4)


def _cuda_snapshot(torch: Any) -> dict[str, Any]:
    if not torch.cuda.is_available():
        raise RuntimeError("QWEN_IMAGE_INFERENCE_MEASUREMENT_CUDA_UNAVAILABLE")
    if not bool(torch.cuda.is_bf16_supported()):
        raise RuntimeError("QWEN_IMAGE_INFERENCE_MEASUREMENT_NATIVE_BF16_UNPROVEN")
    free_bytes, total_bytes = torch.cuda.mem_get_info()
    return {
        "gpu_name": str(torch.cuda.get_device_name(0)),
        "gpu_total_vram_gb": _gib(total_bytes),
        "gpu_free_vram_gb": _gib(free_bytes),
        "native_bf16": True,
    }


def _child(snapshot: Path, result_path: Path, png_path: Path) -> int:
    started = time.monotonic()
    payload: dict[str, Any] = {
        "inference_succeeded": False,
        "pipeline_class": None,
        "offload_mode": None,
        "torch_version": None,
        "cuda_version": None,
        "diffusers_version": None,
        "gpu_name": None,
        "native_bf16": None,
        "gpu_total_vram_gb": None,
        "gpu_free_vram_gb_before": None,
        "gpu_free_vram_gb_after": None,
        "max_cuda_allocated_gb": None,
        "max_cuda_reserved_gb": None,
        "process_max_rss_gb": None,
        "elapsed_seconds": None,
        "output_png_path": None,
        "output_png_sha256": None,
        "output_png_size_bytes": None,
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
            "gpu_name": before["gpu_name"],
            "native_bf16": before["native_bf16"],
            "gpu_total_vram_gb": before["gpu_total_vram_gb"],
            "gpu_free_vram_gb_before": before["gpu_free_vram_gb"],
        })
        pipeline_cls = getattr(diffusers, "QwenImagePipeline", None)
        if pipeline_cls is None:
            raise RuntimeError("QWEN_IMAGE_INFERENCE_MEASUREMENT_PIPELINE_CLASS_UNAVAILABLE")
        torch.cuda.reset_peak_memory_stats()
        pipe = pipeline_cls.from_pretrained(
            str(snapshot),
            torch_dtype=torch.bfloat16,
            local_files_only=True,
            low_cpu_mem_usage=True,
        )
        payload["pipeline_class"] = type(pipe).__name__
        sequential = getattr(pipe, "enable_sequential_cpu_offload", None)
        if not callable(sequential):
            raise RuntimeError("QWEN_IMAGE_INFERENCE_MEASUREMENT_SEQUENTIAL_OFFLOAD_UNAVAILABLE")
        sequential()
        payload["offload_mode"] = PROBE_OFFLOAD_MODE
        generator = torch.Generator(device="cpu").manual_seed(PROBE_SEED)
        result = pipe(
            prompt=PROBE_PROMPT,
            width=PROBE_WIDTH,
            height=PROBE_HEIGHT,
            num_inference_steps=PROBE_STEPS,
            guidance_scale=PROBE_GUIDANCE_SCALE,
            generator=generator,
        )
        images = getattr(result, "images", None)
        if not images or len(images) != 1:
            raise RuntimeError("QWEN_IMAGE_INFERENCE_MEASUREMENT_SINGLE_IMAGE_REQUIRED")
        png_path.parent.mkdir(parents=True, exist_ok=True)
        images[0].save(png_path, format="PNG")
        signature = png_path.read_bytes()[:8]
        if signature != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError("QWEN_IMAGE_INFERENCE_MEASUREMENT_OUTPUT_NOT_PNG")
        payload["output_png_path"] = str(png_path)
        payload["output_png_sha256"] = sha256_file(png_path)
        payload["output_png_size_bytes"] = png_path.stat().st_size
        payload["inference_succeeded"] = True
        free_after, _ = torch.cuda.mem_get_info()
        payload["gpu_free_vram_gb_after"] = _gib(free_after)
        payload["max_cuda_allocated_gb"] = _gib(torch.cuda.max_memory_allocated())
        payload["max_cuda_reserved_gb"] = _gib(torch.cuda.max_memory_reserved())
        del result
        del pipe
        torch.cuda.empty_cache()
    except BaseException as exc:
        payload["failure_type"] = type(exc).__name__
        payload["failure_message"] = str(exc)[:2000]
    finally:
        payload["elapsed_seconds"] = round(time.monotonic() - started, 3)
        payload["process_max_rss_gb"] = _max_rss_gib()
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if payload["inference_succeeded"] else 2


def _observation(*, exit_code: int, child: dict[str, Any]) -> QwenImageInferenceObservation:
    return QwenImageInferenceObservation(
        child_exit_code=int(exit_code),
        inference_succeeded=bool(child.get("inference_succeeded")) and exit_code == 0,
        pipeline_class=child.get("pipeline_class"),
        offload_mode=child.get("offload_mode"),
        torch_version=child.get("torch_version"),
        cuda_version=child.get("cuda_version"),
        diffusers_version=child.get("diffusers_version"),
        gpu_name=child.get("gpu_name"),
        native_bf16=child.get("native_bf16") if isinstance(child.get("native_bf16"), bool) else None,
        gpu_total_vram_gb=child.get("gpu_total_vram_gb"),
        gpu_free_vram_gb_before=child.get("gpu_free_vram_gb_before"),
        gpu_free_vram_gb_after=child.get("gpu_free_vram_gb_after"),
        max_cuda_allocated_gb=child.get("max_cuda_allocated_gb"),
        max_cuda_reserved_gb=child.get("max_cuda_reserved_gb"),
        process_max_rss_gb=child.get("process_max_rss_gb"),
        elapsed_seconds=child.get("elapsed_seconds"),
        output_png_path=child.get("output_png_path"),
        output_png_sha256=child.get("output_png_sha256"),
        output_png_size_bytes=child.get("output_png_size_bytes"),
        failure_type=child.get("failure_type"),
        failure_message=child.get("failure_message"),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure one isolated Qwen Image 2512 inference without canonical authority")
    parser.add_argument("--load-receipt", help="Successful Change Set 225 runtime-load receipt")
    parser.add_argument("--receipt", default="output/phase18_gpu_smoke/qwen-image-2512-single-inference-measurement.json")
    parser.add_argument("--child-result", default="output/phase18_gpu_smoke/qwen-image-2512-single-inference-child.json")
    parser.add_argument("--png", default="output/phase18_gpu_smoke/qwen-image-2512-single-inference-engineering.png")
    parser.add_argument("--timeout-seconds", type=int, default=5400)
    parser.add_argument("--child-snapshot")
    parser.add_argument("--child-output")
    parser.add_argument("--child-png")
    args = parser.parse_args()

    if args.child_snapshot or args.child_output or args.child_png:
        if not args.child_snapshot or not args.child_output or not args.child_png:
            raise RuntimeError("QWEN_IMAGE_INFERENCE_MEASUREMENT_CHILD_ARGUMENTS_INCOMPLETE")
        snapshot = Path(args.child_snapshot).expanduser().resolve()
        if snapshot.name != QWEN_IMAGE_2512_REVISION:
            raise RuntimeError("QWEN_IMAGE_INFERENCE_MEASUREMENT_CHILD_REVISION_MISMATCH")
        return _child(snapshot, Path(args.child_output).expanduser().resolve(), Path(args.child_png).expanduser().resolve())

    if not args.load_receipt:
        raise RuntimeError("QWEN_IMAGE_INFERENCE_MEASUREMENT_LOAD_RECEIPT_REQUIRED")
    load_path = _repo_path(args.load_receipt)
    load_receipt = json.loads(load_path.read_text(encoding="utf-8"))
    load_sha = verify_load_measurement_for_inference(load_receipt)
    snapshot = Path(str(load_receipt["exact_snapshot_path"])).expanduser().resolve()

    child_result_path = _repo_path(args.child_result)
    output_png_path = _repo_path(args.png)
    child_result_path.parent.mkdir(parents=True, exist_ok=True)
    child_result_path.unlink(missing_ok=True)
    output_png_path.unlink(missing_ok=True)
    cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--child-snapshot",
        str(snapshot),
        "--child-output",
        str(child_result_path),
        "--child-png",
        str(output_png_path),
    ]
    try:
        completed = subprocess.run(cmd, cwd=str(ROOT), check=False, timeout=max(1, args.timeout_seconds))
        exit_code = int(completed.returncode)
    except subprocess.TimeoutExpired:
        exit_code = 124

    if child_result_path.is_file():
        child = json.loads(child_result_path.read_text(encoding="utf-8"))
    else:
        child = {
            "inference_succeeded": False,
            "failure_type": "ChildProcessTerminated",
            "failure_message": f"isolated inference child exited without a receipt (exit_code={exit_code})",
        }
    observation = _observation(exit_code=exit_code, child=child)
    measurement = QwenImageInferenceMeasurement(
        load_receipt_sha256=load_sha,
        load_receipt_file_sha256=sha256_file(load_path),
        exact_snapshot_path=str(snapshot),
        observation=observation,
    )
    receipt = measurement.as_receipt()
    receipt_path = _repo_path(args.receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if receipt["single_inference_proven"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
