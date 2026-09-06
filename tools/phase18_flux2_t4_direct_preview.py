#!/usr/bin/env python3
"""Direct-CUDA engineering preview for FLUX.2 klein 4B on ~16 GB GPUs.

This path exists only to prove pixels on constrained Colab T4-class hardware.
It deliberately bypasses CPU offload because a 12-13 GB system-RAM host can be
killed while staging the full pipeline on CPU. The upstream FLUX.2 klein 4B
model is documented as a ~13 GB consumer-GPU model, so this preview loads the
approved immutable revision directly onto CUDA with low_cpu_mem_usage enabled.

The output is NEVER publication-ready and NEVER Golden-reference evidence. It
uses a reduced native preview canvas to leave activation headroom, then writes a
plain PNG plus a JSON diagnostic result. The normal Golden executor and its
provenance gates remain unchanged.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
)
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff


def _aligned(value: int) -> int:
    value = max(256, int(value))
    return value - (value % 16)


def _preview_canvas(request_width: int, request_height: int, max_long_edge: int) -> tuple[int, int]:
    if request_width <= 0 or request_height <= 0:
        raise ValueError("request canvas must be positive")
    long_edge = max(request_width, request_height)
    scale = min(1.0, float(max_long_edge) / float(long_edge))
    width = _aligned(round(request_width * scale))
    height = _aligned(round(request_height * scale))
    return width, height


def main() -> int:
    parser = argparse.ArgumentParser(description="PUL7SAR T4 direct-CUDA FLUX.2 engineering preview")
    parser.add_argument("--request", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--result", required=True)
    parser.add_argument("--max-long-edge", type=int, default=960)
    args = parser.parse_args()

    request = LocalGenerationHandoff.read(args.request)
    if request.model_id != FLUX2_KLEIN_4B_MODEL_ID:
        raise RuntimeError("T4 preview only accepts the approved FLUX.2 klein 4B model")
    if request.reference_asset_ids:
        raise RuntimeError("T4 preview does not enable reference-image execution")

    import torch
    from diffusers import Flux2KleinPipeline

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required")
    props = torch.cuda.get_device_properties(0)
    total_vram_gb = float(props.total_memory) / (1024 ** 3)
    if total_vram_gb < 13.0:
        raise RuntimeError(f"T4 direct preview requires at least 13 GB VRAM; found {total_vram_gb:.2f}")

    width, height = _preview_canvas(request.width, request.height, args.max_long_edge)
    started = time.monotonic()
    torch.cuda.empty_cache()

    print("=== PUL7SAR T4 DIRECT-CUDA ENGINEERING PREVIEW ===")
    print(f"gpu={props.name} vram={total_vram_gb:.2f}GB")
    print(f"request_canvas={request.width}x{request.height} preview_canvas={width}x{height}")
    print("loading approved FLUX.2 klein 4B directly to CUDA; no CPU offload")

    pipe = Flux2KleinPipeline.from_pretrained(
        request.model_id,
        revision=FLUX2_KLEIN_4B_REVISION,
        torch_dtype=torch.float16,
        device_map="cuda",
        low_cpu_mem_usage=True,
    )

    generator = torch.Generator(device="cuda").manual_seed(request.seed)
    image = pipe(
        prompt=request.prompt,
        height=height,
        width=width,
        guidance_scale=1.0,
        num_inference_steps=4,
        generator=generator,
    ).images[0]

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    elapsed = time.monotonic() - started

    peak_allocated = torch.cuda.max_memory_allocated(0) / (1024 ** 3)
    peak_reserved = torch.cuda.max_memory_reserved(0) / (1024 ** 3)
    payload = {
        "status": "T4_DIRECT_ENGINEERING_PREVIEW_GENERATED",
        "png": str(output.resolve()),
        "request_id": request.request_id,
        "model_id": request.model_id,
        "model_revision": FLUX2_KLEIN_4B_REVISION,
        "seed": request.seed,
        "gpu_name": str(props.name),
        "gpu_vram_gb": round(total_vram_gb, 3),
        "requested_width": request.width,
        "requested_height": request.height,
        "preview_width": width,
        "preview_height": height,
        "dtype": "float16",
        "device_map": "cuda",
        "cpu_offload": False,
        "low_cpu_mem_usage": True,
        "num_inference_steps": 4,
        "execution_seconds": elapsed,
        "cuda_peak_allocated_gb": round(peak_allocated, 3),
        "cuda_peak_reserved_gb": round(peak_reserved, 3),
        "quality_tier": "t4_direct_engineering_preview_not_golden",
        "publication_ready": False,
    }
    result = Path(args.result)
    result.parent.mkdir(parents=True, exist_ok=True)
    result.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
