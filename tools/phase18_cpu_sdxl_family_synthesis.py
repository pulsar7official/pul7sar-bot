"""Generate one higher-quality original scene for a selected editorial family.

This benchmark-only path uses SDXL Turbo on a public GitHub CPU runner. A selected
CrossFamilyVisualSystem archetype may alter the camera/environment grammar so
anti-repetition decisions become visible in generated pixels, while all exact
identity/data/branding layers remain outside generation.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import torch
from diffusers import AutoPipelineForText2Image

from engine.intelligence.generation_prompt_budget import GenerationPromptBudget
from engine.intelligence.original_scene_archetype_profiles import OriginalSceneArchetypeProfileRegistry
from engine.intelligence.original_scene_prompt_profiles import OriginalScenePromptProfileRegistry
from engine.intelligence.pre_generation_scene_lock import PreGenerationSceneLockRegistry
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily

MODEL = os.environ.get("PUL7SAR_SDXL_T2I_MODEL", "stabilityai/sdxl-turbo")
SEEDS = {
    EditorialSceneFamily.TRANSFER_SIGNATURE: 28101,
    EditorialSceneFamily.RESULT_STATEMENT: 28201,
    EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: 28301,
    EditorialSceneFamily.DATA_MONUMENT: 28501,
    EditorialSceneFamily.EVENT_EDITORIAL: 28601,
}


def parse() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--family", required=True, choices=[f.value for f in SEEDS])
    p.add_argument("--archetype", default="")
    p.add_argument("--out-dir", required=True)
    p.add_argument("--width", type=int, default=512)
    p.add_argument("--height", type=int, default=640)
    p.add_argument("--steps", type=int, default=4)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--model", default=MODEL)
    return p.parse_args()


def main() -> None:
    q = parse()
    family = EditorialSceneFamily(q.family)
    out = Path(q.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    profile = OriginalScenePromptProfileRegistry.get(family)
    lock = PreGenerationSceneLockRegistry.get(family)
    archetype_id = q.archetype.strip()
    archetype_prompt = ""
    if archetype_id:
        archetype = OriginalSceneArchetypeProfileRegistry.get(family, archetype_id)
        archetype_prompt = " " + archetype.atmosphere_prompt
    prompt = PreGenerationSceneLockRegistry.locked_prompt(family, profile.prompt + archetype_prompt)

    pipe = AutoPipelineForText2Image.from_pretrained(
        q.model,
        torch_dtype=torch.float32,
        use_safetensors=True,
    ).to("cpu")
    pipe.set_progress_bar_config(disable=False)

    budgets = []
    for name in ("tokenizer", "tokenizer_2"):
        tokenizer = getattr(pipe, name, None)
        if tokenizer is not None:
            e = GenerationPromptBudget.require_fit(tokenizer, prompt, reserve_tokens=2)
            budgets.append({
                "tokenizer": name,
                "token_count": e.token_count,
                "model_max_length": e.model_max_length,
                "usable_limit": e.usable_limit,
            })
    if not budgets:
        raise RuntimeError("NO_USABLE_TEXT_TOKENIZER")

    seed = q.seed if q.seed is not None else SEEDS[family]
    if seed < 0:
        raise ValueError("seed must be non-negative")
    gen = torch.Generator(device="cpu").manual_seed(seed)
    image = pipe(
        prompt=prompt,
        width=q.width,
        height=q.height,
        num_inference_steps=q.steps,
        guidance_scale=0.0,
        generator=gen,
    ).images[0]

    image_path = out / f"{family.value}.png"
    image.save(image_path)
    manifest = {
        "contract": "pul7sar-sdxl-family-synthesis-v2-archetype-aware",
        "family": family.value,
        "archetype_id": archetype_id or None,
        "model": q.model,
        "device": "cpu",
        "cost_mode": "$0-github-public-runner",
        "sport_lock": lock.sport,
        "semantic_anchor": lock.semantic_anchor,
        "generated_subject_policy": profile.generated_subject_policy,
        "exact_layers_reserved": list(profile.exact_layers_reserved),
        "prompt_budgets": budgets,
        "seed": seed,
        "steps": q.steps,
        "width": q.width,
        "height": q.height,
        "file": image_path.name,
        "publication_ready": False,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
