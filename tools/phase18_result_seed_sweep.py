from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from diffusers import AutoPipelineForText2Image
from PIL import Image, ImageDraw, ImageFont

from engine.intelligence.generation_prompt_budget import GenerationPromptBudget
from engine.intelligence.original_scene_prompt_profiles import OriginalScenePromptProfileRegistry
from engine.intelligence.pre_generation_scene_lock import PreGenerationSceneLockRegistry
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


def parse():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", required=True)
    p.add_argument("--model", default="stabilityai/sd-turbo")
    p.add_argument("--width", type=int, default=512)
    p.add_argument("--height", type=int, default=640)
    p.add_argument("--steps", type=int, default=4)
    p.add_argument("--seeds", default="18201,18217,18231,18247")
    return p.parse_args()


def main():
    q = parse()
    out = Path(q.out_dir); out.mkdir(parents=True, exist_ok=True)
    family = EditorialSceneFamily.RESULT_STATEMENT
    profile = OriginalScenePromptProfileRegistry.get(family)
    lock = PreGenerationSceneLockRegistry.get(family)

    pipe = AutoPipelineForText2Image.from_pretrained(q.model, torch_dtype=torch.float32).to("cpu")
    prompt = PreGenerationSceneLockRegistry.locked_prompt(family, profile.prompt)
    budget = GenerationPromptBudget.require_fit(pipe.tokenizer, prompt, reserve_tokens=2)

    seeds = tuple(int(s.strip()) for s in q.seeds.split(",") if s.strip())
    files = []
    thumbs = []
    font = ImageFont.load_default()
    for seed in seeds:
        gen = torch.Generator(device="cpu").manual_seed(seed)
        image = pipe(
            prompt=prompt,
            width=q.width,
            height=q.height,
            num_inference_steps=q.steps,
            guidance_scale=0.0,
            generator=gen,
        ).images[0]
        p = out / f"result_seed_{seed}.png"
        image.save(p)
        files.append({"seed": seed, "file": p.name})

        t = image.copy().convert("RGB")
        draw = ImageDraw.Draw(t)
        draw.rectangle((0, 0, 124, 22), fill=(0, 0, 0))
        draw.text((6, 5), f"seed {seed}", font=font, fill=(255, 255, 255))
        thumbs.append(t)

    cols = 2
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (q.width * cols, q.height * rows), (12, 12, 12))
    for i, t in enumerate(thumbs):
        x = (i % cols) * q.width
        y = (i // cols) * q.height
        sheet.paste(t, (x, y))
    sheet_path = out / "result_seed_contact_sheet.jpg"
    sheet.save(sheet_path, quality=94)

    manifest = {
        "contract": "pul7sar-result-seed-sweep-v1",
        "family": family.value,
        "model": q.model,
        "sport_lock": lock.sport,
        "prompt_policy": "compact_positive_scene_ownership_fail_closed_token_budget",
        "prompt_token_count": budget.token_count,
        "prompt_usable_limit": budget.usable_limit,
        "seeds": list(seeds),
        "candidates": files,
        "contact_sheet": sheet_path.name,
        "publication_ready": False,
        "human_visual_review_required": True,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
