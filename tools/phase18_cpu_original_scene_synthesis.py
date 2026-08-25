"""Zero-cost CPU original-scene synthesis runtime for Phase 18 benchmarks.

It creates only unbranded atmosphere/base-scene pixels. Exact PUL7SAR branding,
club crests, readable copy, scores, statistics and verified real-person identity
remain deterministic post-composition responsibilities.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import torch
from diffusers import AutoPipelineForText2Image

from engine.intelligence.original_scene_prompt_profiles import OriginalScenePromptProfileRegistry
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


DEFAULT_MODEL = os.environ.get("PUL7SAR_CPU_T2I_MODEL", "stabilityai/sd-turbo")
FAMILIES = {f.value: f for f in EditorialSceneFamily}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    p.add_argument("--seed", type=int, default=1801)
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--width", type=int, default=512)
    p.add_argument("--height", type=int, default=640)
    p.add_argument("--steps", type=int, default=1)
    p.add_argument("--family", choices=tuple(FAMILIES), default=EditorialSceneFamily.EVENT_EDITORIAL.value)
    p.add_argument("--prompt", default=None)
    return p.parse_args()


def main() -> None:
    q = parse_args()
    if q.width % 8 or q.height % 8:
        raise ValueError("width and height must be divisible by 8")
    family = FAMILIES[q.family]
    if family is EditorialSceneFamily.TACTICAL_BOARD:
        raise ValueError("TACTICAL_BOARD_REMAINS_DETERMINISTIC_FIRST")
    profile = OriginalScenePromptProfileRegistry.get(family)
    prompt = q.prompt or profile.prompt
    out = Path(q.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    pipe = AutoPipelineForText2Image.from_pretrained(q.model, torch_dtype=torch.float32)
    pipe = pipe.to("cpu")
    pipe.set_progress_bar_config(disable=False)
    generator = torch.Generator(device="cpu").manual_seed(q.seed)
    result = pipe(
        prompt=prompt,
        width=q.width,
        height=q.height,
        num_inference_steps=q.steps,
        guidance_scale=0.0,
        generator=generator,
    ).images[0]
    result.save(out)
    meta = {
        "contract": "pul7sar-cpu-original-scene-synthesis-v2",
        "family": family.value,
        "profile_contract": profile.contract,
        "generated_subject_policy": profile.generated_subject_policy,
        "model": q.model,
        "seed": q.seed,
        "width": q.width,
        "height": q.height,
        "steps": q.steps,
        "device": "cpu",
        "cost_mode": "$0-github-public-runner",
        "publication_ready": False,
        "exact_layers_reserved": list(profile.exact_layers_reserved),
    }
    out.with_suffix(".json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
