#!/usr/bin/env python3
"""Repair/qualify the Colab semantic stack, then launch Golden Hybrid v5.

This wrapper intentionally uses only the Python standard library before it repairs
Pillow/Transformers. That matters in Colab: if a previous notebook cell upgraded
Pillow in-place, importing PIL in the notebook kernel can observe a mixed package
tree. We repair the exact verified builds on disk, validate them in a fresh child
interpreter, then launch the real Phase 18 runner in another fresh child process.
"""
from __future__ import annotations

import argparse
import json
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
    return subprocess.run(
        command,
        cwd=ROOT,
        env=os.environ.copy(),
        text=True,
        check=check,
    )


def _repair_runtime() -> None:
    if not REQUIREMENTS.is_file():
        raise RuntimeError("PHASE18_GPU_REQUIREMENTS_MISSING")

    # Repair the two packages known to become incoherent in a live Colab kernel.
    # Force-reinstall makes the package tree internally consistent even when the
    # metadata already reports the desired version.
    _run([
        sys.executable,
        "-m",
        "pip",
        "install",
        "--no-cache-dir",
        "--force-reinstall",
        "--upgrade",
        f"Pillow=={VERIFIED_PILLOW}",
        f"transformers=={VERIFIED_TRANSFORMERS}",
    ])

    # Install/bound the rest of the Phase 18 stack without replacing torch.
    _run([
        sys.executable,
        "-m",
        "pip",
        "install",
        "--no-cache-dir",
        "--upgrade-strategy",
        "only-if-needed",
        "-r",
        str(REQUIREMENTS),
    ])


def _fresh_process_probe() -> None:
    probe = r'''
import json
import torch
import transformers
import PIL
from PIL import Image, ImageDraw, ImageFont, ImageText
from transformers import Qwen2_5_VLConfig, pipeline

payload = {
    "status": "PHASE18_COLAB_RUNTIME_READY",
    "torch": torch.__version__,
    "cuda_available": bool(torch.cuda.is_available()),
    "transformers": transformers.__version__,
    "pillow": PIL.__version__,
    "qwen_public_api": bool(Qwen2_5_VLConfig is not None and pipeline is not None),
    "pillow_modules_coherent": bool(Image and ImageDraw and ImageFont and ImageText),
}
print(json.dumps(payload, indent=2, sort_keys=True))
if payload["transformers"] != "4.56.2":
    raise SystemExit("TRANSFORMERS_VERSION_DRIFT")
if payload["pillow"] != "11.3.0":
    raise SystemExit("PILLOW_VERSION_DRIFT")
if not payload["cuda_available"]:
    raise SystemExit("CUDA_NOT_AVAILABLE")
'''
    _run([sys.executable, "-c", probe])


def main() -> int:
    parser = argparse.ArgumentParser(description="PUL7SAR Phase 18 Colab self-repair + Golden Hybrid v5 bootstrap")
    parser.add_argument("--candidate", type=int, default=1)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--semantic-inspection", choices=("qwen",), default="qwen")
    parser.add_argument("--skip-repair", action="store_true", help="Only for a runtime already proven by this bootstrap")
    args = parser.parse_args()

    print("=== PUL7SAR PHASE 18 — COLAB BOOTSTRAP ===", flush=True)
    if not args.skip_repair:
        print("1/3 Repairing the exact verified semantic runtime...", flush=True)
        _repair_runtime()
    else:
        print("1/3 Runtime repair skipped by explicit request.", flush=True)

    print("2/3 Proving Pillow/Qwen/CUDA coherence in a fresh interpreter...", flush=True)
    _fresh_process_probe()

    print("3/3 Launching the protected Golden Hybrid v5 runner in a fresh interpreter...", flush=True)
    command = [
        sys.executable,
        str(ROOT / "tools" / "phase18_colab_one_command.py"),
        "--candidate",
        str(args.candidate),
        "--semantic-inspection",
        args.semantic_inspection,
    ]
    if args.force:
        command.append("--force")
    completed = _run(command, check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
