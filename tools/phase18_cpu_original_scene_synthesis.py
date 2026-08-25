"""Zero-cost CPU original-scene synthesis smoke runtime for Phase 18.

This is a benchmark adapter, not a publication renderer. It intentionally creates
only an unbranded atmospheric base scene. Exact PUL7SAR branding, club crests,
readable copy, scores, statistics and real-person identities stay outside this
runtime and are added deterministically after synthesis.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import torch
from diffusers import AutoPipelineForText2Image


DEFAULT_MODEL = os.environ.get("PUL7SAR_CPU_T2I_MODEL", "stabilityai/sd-turbo")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    p.add_argument("--seed", type=int, default=1801)
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--width", type=int, default=512)
    p.add_argument("--height", type=int, default=640)
    p.add_argument("--steps", type=int, default=1)
    p.add_argument("--prompt", default=(
        "premium cinematic football editorial atmosphere at night, one coherent physical scene, "
        "deep stadium-scale spatial feeling without identifying any real stadium, dramatic practical floodlights, "
        "subtle crowd depth, dark textured sporting environment, realistic lens depth, natural shadows, "
        "restrained red and electric blue light accents integrated into the environment, sophisticated sports photography mood, "
        "large clean negative space for later editorial composition, completely unbranded scene, blank neutral advertising surfaces, "
        "no readable writing, no numbers, no logos, no club crest, no watermark, no celebrity, no identifiable real person"
    ))
    return p.parse_args()


def main() -> None:
    q = parse_args()
    if q.width % 8 or q.height % 8:
        raise ValueError("width and height must be divisible by 8")
    out = Path(q.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    pipe = AutoPipelineForText2Image.from_pretrained(q.model, torch_dtype=torch.float32)
    pipe = pipe.to("cpu")
    pipe.set_progress_bar_config(disable=False)
    generator = torch.Generator(device="cpu").manual_seed(q.seed)
    result = pipe(
        prompt=q.prompt,
        width=q.width,
        height=q.height,
        num_inference_steps=q.steps,
        guidance_scale=0.0,
        generator=generator,
    ).images[0]
    result.save(out)
    meta = {
        "contract": "pul7sar-cpu-original-scene-synthesis-smoke-v1",
        "model": q.model,
        "seed": q.seed,
        "width": q.width,
        "height": q.height,
        "steps": q.steps,
        "device": "cpu",
        "cost_mode": "$0-github-public-runner",
        "publication_ready": False,
        "exact_fact_roles_reserved_for_compositor": ["readable_text", "pul7sar_brand", "exact_score", "club_crest"],
    }
    out.with_suffix(".json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
