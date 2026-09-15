#!/usr/bin/env python3
"""4-bit FLUX.2 klein 4B engineering preview for Colab T4-class GPUs.

The unquantized direct-CUDA path can fill a 14.56-GiB T4 before inference starts.
This optional preview quantizes the two largest pipeline components (transformer
and Qwen3 text encoder) with bitsandbytes NF4, then loads the remaining Klein
pipeline pieces normally. It is intentionally isolated from Golden-reference
execution and can never imply publication readiness.

This path trades some fidelity and speed characteristics for memory headroom so
PUL7SAR can inspect real story-conditioned pixels on zero-cost constrained GPUs.
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
    return _aligned(round(request_width * scale)), _aligned(round(request_height * scale))


def main() -> int:
    parser = argparse.ArgumentParser(description="PUL7SAR 4-bit T4 FLUX.2 engineering preview")
    parser.add_argument("--request", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--result", required=True)
    parser.add_argument("--max-long-edge", type=int, default=768)
    args = parser.parse_args()

    request = LocalGenerationHandoff.read(args.request)
    if request.model_id != FLUX2_KLEIN_4B_MODEL_ID:
        raise RuntimeError("quantized T4 preview only accepts the approved FLUX.2 klein 4B model")
    if request.reference_asset_ids:
        raise RuntimeError("quantized T4 preview does not enable reference-image execution")

    import torch
    from diffusers import (
        BitsAndBytesConfig as DiffusersBitsAndBytesConfig,
        Flux2KleinPipeline,
        Flux2Transformer2DModel,
    )
    from transformers import BitsAndBytesConfig as TransformersBitsAndBytesConfig, Qwen3ForCausalLM

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required")

    props = torch.cuda.get_device_properties(0)
    total_vram_gb = float(props.total_memory) / (1024 ** 3)
    if total_vram_gb < 13.0:
        raise RuntimeError(f"quantized T4 preview requires at least 13 GB VRAM; found {total_vram_gb:.2f}")

    width, height = _preview_canvas(request.width, request.height, args.max_long_edge)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats(0)
    started = time.monotonic()

    print("=== PUL7SAR T4 4-BIT ENGINEERING PREVIEW ===", flush=True)
    print(f"gpu={props.name} vram={total_vram_gb:.2f}GB", flush=True)
    print(f"request_canvas={request.width}x{request.height} preview_canvas={width}x{height}", flush=True)
    print("quantizing transformer + Qwen3 text encoder to bitsandbytes NF4", flush=True)

    transformer_quant = DiffusersBitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )
    text_quant = TransformersBitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )

    transformer = Flux2Transformer2DModel.from_pretrained(
        request.model_id,
        subfolder="transformer",
        revision=FLUX2_KLEIN_4B_REVISION,
        quantization_config=transformer_quant,
        torch_dtype=torch.float16,
        device_map="auto",
        low_cpu_mem_usage=True,
    )
    print("transformer loaded", flush=True)

    text_encoder = Qwen3ForCausalLM.from_pretrained(
        request.model_id,
        subfolder="text_encoder",
        revision=FLUX2_KLEIN_4B_REVISION,
        quantization_config=text_quant,
        torch_dtype=torch.float16,
        device_map="auto",
        low_cpu_mem_usage=True,
    )
    print("text encoder loaded", flush=True)

    pipe = Flux2KleinPipeline.from_pretrained(
        request.model_id,
        revision=FLUX2_KLEIN_4B_REVISION,
        transformer=transformer,
        text_encoder=text_encoder,
        torch_dtype=torch.float16,
        device_map="cuda",
        low_cpu_mem_usage=True,
    )
    print("pipeline ready", flush=True)

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

    payload = {
        "status": "T4_4BIT_ENGINEERING_PREVIEW_GENERATED",
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
        "quantization": "bitsandbytes_nf4_4bit_transformer_and_text_encoder",
        "num_inference_steps": 4,
        "execution_seconds": elapsed,
        "cuda_peak_allocated_gb": round(torch.cuda.max_memory_allocated(0) / (1024 ** 3), 3),
        "cuda_peak_reserved_gb": round(torch.cuda.max_memory_reserved(0) / (1024 ** 3), 3),
        "quality_tier": "t4_4bit_engineering_preview_not_golden",
        "publication_ready": False,
    }
    result = Path(args.result)
    result.parent.mkdir(parents=True, exist_ok=True)
    result.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
