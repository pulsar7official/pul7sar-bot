#!/usr/bin/env python3
"""Execute the locked Qwen Image 2512 runtime-envelope plan on a compatible $0-local host.

The parent process verifies Change Sets 228/229 evidence, then launches each
planned engineering probe in an isolated subprocess. It stops after the first
failure. Generated PNGs are measurement artifacts only and can never be reused
as canonical/Golden pixels by this tool.
"""
from __future__ import annotations

import argparse
import hashlib
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
    PROBE_PROMPT,
    PROBE_SEED,
    sha256_file,
    validate_probe_prompt,
)
from engine.intelligence.qwen_image_runtime_envelope_admission import verify_runtime_envelope_admission
from engine.intelligence.qwen_image_runtime_envelope_executor import (
    build_runtime_envelope_execution_receipt,
    verify_runtime_envelope_execution_receipt,
)
from engine.intelligence.qwen_image_runtime_envelope_plan import (
    DTYPE,
    OFFLOAD_MODE,
    PROBES,
    verify_runtime_envelope_plan,
)


def _repo_path(path: str) -> Path:
    value = Path(path)
    if not value.is_absolute():
        value = ROOT / value
    value = value.resolve()
    if not value.is_relative_to(ROOT.resolve()):
        raise RuntimeError(f"QWEN_RUNTIME_ENVELOPE_EXECUTOR_PATH_ESCAPE: {value}")
    return value


def _gib(value: int | float) -> float:
    return round(float(value) / (1024 ** 3), 4)


def _max_rss_gib() -> float:
    return round(float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / (1024 ** 2), 4)


def _probe_by_id(probe_id: str) -> dict[str, Any]:
    for probe in PROBES:
        if probe["probe_id"] == probe_id:
            return dict(probe)
    raise RuntimeError("QWEN_RUNTIME_ENVELOPE_EXECUTOR_UNKNOWN_PROBE")


def _base_child_payload(probe: dict[str, Any]) -> dict[str, Any]:
    normalized_prompt = validate_probe_prompt(PROBE_PROMPT)
    return {
        **probe,
        "seed": PROBE_SEED,
        "guidance_scale": PROBE_GUIDANCE_SCALE,
        "dtype": DTYPE,
        "offload_mode": None,
        "prompt_sha256": hashlib.sha256(normalized_prompt.encode("utf-8")).hexdigest(),
        "child_exit_code": 2,
        "inference_succeeded": False,
        "pipeline_class": None,
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


def _cuda_snapshot(torch: Any) -> dict[str, Any]:
    if not torch.cuda.is_available():
        raise RuntimeError("QWEN_RUNTIME_ENVELOPE_EXECUTOR_CUDA_UNAVAILABLE")
    if not bool(torch.cuda.is_bf16_supported()):
        raise RuntimeError("QWEN_RUNTIME_ENVELOPE_EXECUTOR_NATIVE_BF16_UNPROVEN")
    free_bytes, total_bytes = torch.cuda.mem_get_info()
    return {
        "gpu_name": str(torch.cuda.get_device_name(0)),
        "gpu_total_vram_gb": _gib(total_bytes),
        "gpu_free_vram_gb": _gib(free_bytes),
        "native_bf16": True,
    }


def _child(snapshot: Path, result_path: Path, png_path: Path, probe_id: str) -> int:
    probe = _probe_by_id(probe_id)
    payload = _base_child_payload(probe)
    started = time.monotonic()
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
            raise RuntimeError("QWEN_RUNTIME_ENVELOPE_EXECUTOR_PIPELINE_CLASS_UNAVAILABLE")
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
            raise RuntimeError("QWEN_RUNTIME_ENVELOPE_EXECUTOR_SEQUENTIAL_OFFLOAD_UNAVAILABLE")
        sequential()
        payload["offload_mode"] = OFFLOAD_MODE
        generator = torch.Generator(device="cpu").manual_seed(PROBE_SEED)
        result = pipe(
            prompt=validate_probe_prompt(PROBE_PROMPT),
            width=probe["width"],
            height=probe["height"],
            num_inference_steps=probe["steps"],
            guidance_scale=PROBE_GUIDANCE_SCALE,
            generator=generator,
        )
        images = getattr(result, "images", None)
        if not images or len(images) != 1:
            raise RuntimeError("QWEN_RUNTIME_ENVELOPE_EXECUTOR_SINGLE_IMAGE_REQUIRED")
        png_path.parent.mkdir(parents=True, exist_ok=True)
        images[0].save(png_path, format="PNG")
        if png_path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError("QWEN_RUNTIME_ENVELOPE_EXECUTOR_OUTPUT_NOT_PNG")
        resolved_png = png_path.resolve()
        payload["output_png_path"] = str(resolved_png.relative_to(ROOT.resolve()))
        payload["output_png_sha256"] = sha256_file(resolved_png)
        payload["output_png_size_bytes"] = resolved_png.stat().st_size
        free_after, _ = torch.cuda.mem_get_info()
        payload["gpu_free_vram_gb_after"] = _gib(free_after)
        payload["max_cuda_allocated_gb"] = _gib(torch.cuda.max_memory_allocated())
        payload["max_cuda_reserved_gb"] = _gib(torch.cuda.max_memory_reserved())
        payload["inference_succeeded"] = True
        payload["child_exit_code"] = 0
        del result
        del pipe
        torch.cuda.empty_cache()
    except BaseException as exc:
        payload["failure_type"] = type(exc).__name__
        payload["failure_message"] = str(exc)[:2000]
        payload["child_exit_code"] = 2
        png_path.unlink(missing_ok=True)
    finally:
        payload["elapsed_seconds"] = round(time.monotonic() - started, 3)
        payload["process_max_rss_gb"] = _max_rss_gib()
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return int(payload["child_exit_code"])


def _synthetic_failure(probe: dict[str, Any], *, exit_code: int, failure_type: str, message: str) -> dict[str, Any]:
    payload = _base_child_payload(probe)
    payload["child_exit_code"] = int(exit_code)
    payload["failure_type"] = failure_type
    payload["failure_message"] = message[:2000]
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute the locked Qwen Image 2512 runtime-envelope engineering plan")
    parser.add_argument("--plan", help="Change Set 229 locked plan JSON")
    parser.add_argument("--admission", help="Change Set 228 admission JSON bound by the plan")
    parser.add_argument("--snapshot", help="Exact local Qwen Image 2512 snapshot directory")
    parser.add_argument("--receipt", default="output/phase18_gpu_smoke/qwen-image-2512-runtime-envelope-execution.json")
    parser.add_argument("--output-dir", default="output/phase18_gpu_smoke/qwen-image-2512-runtime-envelope")
    parser.add_argument("--timeout-seconds-per-probe", type=int, default=7200)
    parser.add_argument("--child-snapshot")
    parser.add_argument("--child-result")
    parser.add_argument("--child-png")
    parser.add_argument("--child-probe-id")
    args = parser.parse_args()

    child_values = (args.child_snapshot, args.child_result, args.child_png, args.child_probe_id)
    if any(child_values):
        if not all(child_values):
            raise RuntimeError("QWEN_RUNTIME_ENVELOPE_EXECUTOR_CHILD_ARGUMENTS_INCOMPLETE")
        snapshot = Path(args.child_snapshot).expanduser().resolve()
        if snapshot.name != QWEN_IMAGE_2512_REVISION:
            raise RuntimeError("QWEN_RUNTIME_ENVELOPE_EXECUTOR_CHILD_REVISION_MISMATCH")
        return _child(snapshot, Path(args.child_result).expanduser().resolve(), Path(args.child_png).expanduser().resolve(), str(args.child_probe_id))

    if not args.plan or not args.admission or not args.snapshot:
        raise RuntimeError("QWEN_RUNTIME_ENVELOPE_EXECUTOR_PLAN_ADMISSION_SNAPSHOT_REQUIRED")
    plan_path = _repo_path(args.plan)
    admission_path = _repo_path(args.admission)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    admission = json.loads(admission_path.read_text(encoding="utf-8"))
    plan_sha = verify_runtime_envelope_plan(plan)
    admission_sha = verify_runtime_envelope_admission(admission)
    admission_file_sha = sha256_file(admission_path)
    if plan.get("source_admission_sha256") != admission_sha or plan.get("source_admission_file_sha256") != admission_file_sha:
        raise RuntimeError("QWEN_RUNTIME_ENVELOPE_EXECUTOR_ADMISSION_BINDING_MISMATCH")

    snapshot = Path(args.snapshot).expanduser().resolve()
    if snapshot.name != QWEN_IMAGE_2512_REVISION or not snapshot.is_dir():
        raise RuntimeError("QWEN_RUNTIME_ENVELOPE_EXECUTOR_EXACT_SNAPSHOT_REQUIRED")
    output_dir = _repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    observations: list[dict[str, Any]] = []

    for probe in plan["probe_order"]:
        probe_id = str(probe["probe_id"])
        child_result = output_dir / f"{probe_id}.child.json"
        png_path = output_dir / f"{probe_id}.engineering.png"
        child_result.unlink(missing_ok=True)
        png_path.unlink(missing_ok=True)
        cmd = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--child-snapshot", str(snapshot),
            "--child-result", str(child_result),
            "--child-png", str(png_path),
            "--child-probe-id", probe_id,
        ]
        try:
            completed = subprocess.run(cmd, cwd=str(ROOT), check=False, timeout=max(1, args.timeout_seconds_per_probe))
            exit_code = int(completed.returncode)
            if child_result.is_file():
                observation = json.loads(child_result.read_text(encoding="utf-8"))
                observation["child_exit_code"] = exit_code
            else:
                observation = _synthetic_failure(probe, exit_code=exit_code, failure_type="ChildProcessTerminated", message=f"probe child exited without receipt (exit_code={exit_code})")
        except subprocess.TimeoutExpired:
            png_path.unlink(missing_ok=True)
            observation = _synthetic_failure(probe, exit_code=124, failure_type="TimeoutExpired", message="isolated runtime-envelope probe exceeded timeout")
        observations.append(observation)
        if not observation.get("inference_succeeded") or observation.get("child_exit_code") != 0:
            break

    receipt = build_runtime_envelope_execution_receipt(
        plan,
        plan_file_sha256=sha256_file(plan_path),
        exact_snapshot_path=str(snapshot),
        observations=observations,
        repo_root=ROOT,
    )
    verify_runtime_envelope_execution_receipt(receipt, repo_root=ROOT)
    if receipt["source_plan_sha256"] != plan_sha:
        raise RuntimeError("QWEN_RUNTIME_ENVELOPE_EXECUTOR_PLAN_BINDING_MISMATCH")
    receipt_path = _repo_path(args.receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if receipt["all_planned_probes_completed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
