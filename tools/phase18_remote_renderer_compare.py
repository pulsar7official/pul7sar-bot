#!/usr/bin/env python3
"""Compare stronger remote ZeroGPU renderers for one PUL7SAR editorial prompt.

This is a Phase 18 development benchmark. It intentionally bypasses local T4
inference and calls public Hugging Face Spaces through gradio_client so PUL7SAR
can compare current open-weight renderers without rebuilding its editorial brain.

Renderers:
- Qwen/Qwen-Image-2512 (official ZeroGPU Space)
- black-forest-labs/FLUX.2-dev (official ZeroGPU Space)

The tool saves raw base visuals only. PUL7SAR branding/typography remain separate,
deterministic post-composition layers.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import time
from typing import Any


def _client(space: str):
    from gradio_client import Client
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    kwargs = {"hf_token": token} if token else {}
    return Client(space, **kwargs)


def _copy_result(result: Any, target: Path) -> None:
    """Accept common gradio_client image return shapes and persist one PNG."""
    candidate = result
    if isinstance(candidate, (tuple, list)) and candidate:
        candidate = candidate[0]
    if isinstance(candidate, dict):
        candidate = candidate.get("path") or candidate.get("name") or candidate.get("url")
    if hasattr(candidate, "name"):
        candidate = candidate.name
    if not isinstance(candidate, str):
        raise RuntimeError(f"unsupported Gradio image result type: {type(candidate)!r}")
    source = Path(candidate)
    if not source.is_file():
        raise FileNotFoundError(f"Gradio result file not found: {candidate}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def render_qwen(*, prompt: str, output: Path, seed: int) -> dict[str, Any]:
    client = _client("Qwen/Qwen-Image-2512")
    started = time.monotonic()
    # Official Space inputs: prompt, seed, randomize_seed, aspect_ratio,
    # guidance_scale, num_inference_steps, prompt_enhance.
    result = client.predict(
        prompt,
        seed,
        False,
        "3:4",
        4.0,
        40,
        True,
        api_name="/infer",
    )
    _copy_result(result, output)
    return {
        "renderer": "qwen-image-2512",
        "space": "Qwen/Qwen-Image-2512",
        "output": str(output.resolve()),
        "seed": seed,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "publication_ready": False,
    }


def render_flux2_dev(*, prompt: str, output: Path, seed: int) -> dict[str, Any]:
    client = _client("black-forest-labs/FLUX.2-dev")
    started = time.monotonic()
    # Official Space inputs: prompt, input_images, seed, randomize_seed, width,
    # height, num_inference_steps, guidance_scale, prompt_upsampling.
    result = client.predict(
        prompt,
        None,
        seed,
        False,
        768,
        1024,
        30,
        4.0,
        True,
        api_name="/infer",
    )
    _copy_result(result, output)
    return {
        "renderer": "flux2-dev",
        "space": "black-forest-labs/FLUX.2-dev",
        "output": str(output.resolve()),
        "seed": seed,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "publication_ready": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Qwen Image 2512 vs FLUX.2 dev ZeroGPU")
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--result", required=True)
    parser.add_argument("--seed", type=int, default=1902001)
    args = parser.parse_args()

    prompt_path = Path(args.prompt_file)
    prompt = prompt_path.read_text(encoding="utf-8").strip()
    if not prompt:
        raise ValueError("prompt file is empty")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    reports: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    jobs = (
        ("qwen-image-2512", render_qwen, output_dir / "qwen-image-2512.png"),
        ("flux2-dev", render_flux2_dev, output_dir / "flux2-dev.png"),
    )
    for name, fn, output in jobs:
        print(f"\n=== {name} ===", flush=True)
        try:
            report = fn(prompt=prompt, output=output, seed=args.seed)
            reports.append(report)
            print(json.dumps(report, indent=2), flush=True)
        except Exception as exc:
            failure = {"renderer": name, "error": f"{type(exc).__name__}: {exc}"}
            failures.append(failure)
            print(json.dumps(failure, indent=2), flush=True)

    payload = {
        "status": "REMOTE_RENDERER_COMPARISON_COMPLETE" if reports else "REMOTE_RENDERER_COMPARISON_FAILED",
        "prompt_file": str(prompt_path.resolve()),
        "successful": reports,
        "failures": failures,
        "publication_ready": False,
        "human_visual_review_required": True,
    }
    result_path = Path(args.result)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n" + json.dumps(payload, indent=2, ensure_ascii=False), flush=True)
    return 0 if reports else 1


if __name__ == "__main__":
    raise SystemExit(main())
