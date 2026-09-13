#!/usr/bin/env python3
"""Repair/qualify Colab, prefetch semantic weights, then launch Golden Hybrid v5.

Semantic QA is desirable but is not allowed to trap development in a retry loop.
The bootstrap repairs the verified runtime and probes it in a fresh interpreter.
When that semantic runtime is coherent it also proves/downloads the exact local
Qwen snapshot *before* FLUX spends GPU time. If semantic preparation fails and
strict mode is not requested, the protected runner is launched in explicit
engineering-proof mode; publication remains fail-closed inside that runner.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "requirements-phase18-gpu.txt"
VERIFIED_PILLOW = "11.3.0"
VERIFIED_TRANSFORMERS = "4.56.2"


def _run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print("$", " ".join(command), flush=True)
    return subprocess.run(command, cwd=ROOT, env=os.environ.copy(), text=True, check=check)


def _repair_runtime() -> None:
    if not REQUIREMENTS.is_file():
        raise RuntimeError("PHASE18_GPU_REQUIREMENTS_MISSING")
    _run([
        sys.executable, "-m", "pip", "install", "--no-cache-dir", "--force-reinstall", "--upgrade",
        f"Pillow=={VERIFIED_PILLOW}", f"transformers=={VERIFIED_TRANSFORMERS}",
    ])
    _run([
        sys.executable, "-m", "pip", "install", "--no-cache-dir",
        "--upgrade-strategy", "only-if-needed", "-r", str(REQUIREMENTS),
    ])


def _fresh_process_probe() -> bool:
    probe = r'''
import json
import torch
payload = {
    "status": "PHASE18_COLAB_RUNTIME_PROBE",
    "torch": torch.__version__,
    "cuda_available": bool(torch.cuda.is_available()),
    "semantic_ready": False,
    "semantic_error": None,
}
try:
    import transformers
    import PIL
    from PIL import Image, ImageDraw, ImageFont
    from transformers import Qwen2_5_VLConfig, pipeline
    payload.update({
        "transformers": transformers.__version__,
        "pillow": PIL.__version__,
        "qwen_public_api": bool(Qwen2_5_VLConfig is not None and pipeline is not None),
        "pillow_modules_coherent": bool(Image and ImageDraw and ImageFont),
    })
    payload["semantic_ready"] = bool(
        payload["transformers"] == "4.56.2"
        and payload["pillow"] == "11.3.0"
        and payload["qwen_public_api"]
        and payload["pillow_modules_coherent"]
    )
except Exception as exc:
    payload["semantic_error"] = f"{exc.__class__.__name__}:{exc}"
print(json.dumps(payload, indent=2, sort_keys=True))
if not payload["cuda_available"]:
    raise SystemExit(2)
if not payload["semantic_ready"]:
    raise SystemExit(1)
'''
    completed = _run([sys.executable, "-c", probe], check=False)
    if completed.returncode == 2:
        raise RuntimeError("CUDA_NOT_AVAILABLE")
    return completed.returncode == 0


def _prefetch_semantic_model() -> bool:
    """Prepare exact Qwen weights before FLUX generation; never performs inference."""
    completed = _run([
        sys.executable,
        str(ROOT / "tools" / "phase18_prefetch_qwen.py"),
        "--receipt",
        "output/phase18_gpu_smoke/qwen-model-cache.json",
    ], check=False)
    return completed.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="PUL7SAR Phase 18 Colab self-repair + Golden Hybrid v5 bootstrap")
    parser.add_argument("--candidate", type=int, default=1)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--semantic-inspection", choices=("qwen",), default="qwen")
    parser.add_argument("--skip-repair", action="store_true", help="Only for a runtime already proven by this bootstrap")
    parser.add_argument("--strict-semantic", action="store_true", help="Require semantic QA instead of allowing engineering proof fallback")
    args = parser.parse_args()

    print("=== PUL7SAR PHASE 18 — COLAB BOOTSTRAP ===", flush=True)
    if not args.skip_repair:
        print("1/4 Repairing the exact verified semantic runtime...", flush=True)
        _repair_runtime()
    else:
        print("1/4 Runtime repair skipped by explicit request.", flush=True)

    print("2/4 Probing Pillow/Qwen/CUDA in a fresh interpreter...", flush=True)
    semantic_ready = _fresh_process_probe()
    if semantic_ready:
        print("PHASE18_COLAB_RUNTIME_READY", flush=True)
    else:
        print("PHASE18_SEMANTIC_RUNTIME_DEGRADED: publication semantic QA is unavailable.", flush=True)
        if args.strict_semantic:
            raise RuntimeError("SEMANTIC_RUNTIME_REQUIRED_BY_STRICT_MODE")

    semantic_mode = args.semantic_inspection if semantic_ready else "none"
    if semantic_ready:
        print("3/4 Proving/caching exact Qwen semantic weights before FLUX GPU generation...", flush=True)
        semantic_model_ready = _prefetch_semantic_model()
        if not semantic_model_ready:
            print(
                "PHASE18_QWEN_MODEL_CACHE_DEGRADED: continuing in engineering-proof mode; "
                "publication remains blocked.",
                flush=True,
            )
            if args.strict_semantic:
                raise RuntimeError("SEMANTIC_MODEL_CACHE_REQUIRED_BY_STRICT_MODE")
            semantic_mode = "none"
    else:
        print("3/4 Qwen model prefetch skipped because semantic runtime is degraded.", flush=True)

    print("4/4 Launching protected Golden Hybrid v5 runner in a fresh interpreter...", flush=True)
    command = [
        sys.executable,
        str(ROOT / "tools" / "phase18_colab_one_command.py"),
        "--candidate", str(args.candidate),
        "--semantic-inspection", semantic_mode,
    ]
    if args.force:
        command.append("--force")
    if args.strict_semantic:
        command.append("--strict-semantic")
    completed = _run(command, check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
