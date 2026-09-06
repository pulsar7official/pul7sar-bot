#!/usr/bin/env python3
"""Build a byte-bound admission receipt for a future Qwen runtime-envelope experiment.

CPU-only. This tool replays a successful engineering single-inference receipt
against the exact PNG bytes it names. It does not load Qwen Image, run CUDA,
mutate the generation queue, establish a runtime floor, or authorize Golden
or publication use.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.qwen_image_inference_measurement import sha256_file
from engine.intelligence.qwen_image_runtime_envelope_admission import (
    build_runtime_envelope_admission,
    verify_runtime_envelope_admission,
)


def _repo_path(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise RuntimeError(f"QWEN_RUNTIME_ENVELOPE_ADMISSION_PATH_ESCAPE: {path}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build byte-bound Qwen runtime-envelope measurement admission")
    parser.add_argument("--inference-receipt", required=True)
    parser.add_argument("--output", default="output/phase18_gpu_smoke/qwen-image-2512-runtime-envelope-admission.json")
    args = parser.parse_args()

    source = _repo_path(args.inference_receipt)
    receipt = json.loads(source.read_text(encoding="utf-8"))
    admission = build_runtime_envelope_admission(
        receipt,
        inference_receipt_file_sha256=sha256_file(source),
        repo_root=ROOT,
    )
    verify_runtime_envelope_admission(admission)
    output = _repo_path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(admission, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(admission, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
