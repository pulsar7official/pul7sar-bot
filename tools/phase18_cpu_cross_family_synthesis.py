"""Generate one original synthesis benchmark scene per generative editorial family.

The model is loaded once on CPU, then reused across families to keep the GitHub
benchmark zero-cost and practical. Tactical remains deterministic and is omitted.
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

MODEL = os.environ.get("PUL7SAR_CPU_T2I_MODEL", "stabilityai/sd-turbo")
FAMILIES = (
    EditorialSceneFamily.TRANSFER_SIGNATURE,
    EditorialSceneFamily.RESULT_STATEMENT,
    EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
    EditorialSceneFamily.DATA_MONUMENT,
    EditorialSceneFamily.EVENT_EDITORIAL,
)
SEEDS = {
    EditorialSceneFamily.TRANSFER_SIGNATURE: 18101,
    EditorialSceneFamily.RESULT_STATEMENT: 18201,
    EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: 18301,
    EditorialSceneFamily.DATA_MONUMENT: 18501,
    EditorialSceneFamily.EVENT_EDITORIAL: 18601,
}


def parse():
    p=argparse.ArgumentParser(); p.add_argument('--out-dir',required=True); p.add_argument('--width',type=int,default=512); p.add_argument('--height',type=int,default=640); p.add_argument('--steps',type=int,default=1); p.add_argument('--model',default=MODEL); return p.parse_args()


def main():
    q=parse(); out=Path(q.out_dir); out.mkdir(parents=True,exist_ok=True)
    pipe=AutoPipelineForText2Image.from_pretrained(q.model,torch_dtype=torch.float32).to('cpu'); pipe.set_progress_bar_config(disable=False)
    manifest=[]
    for family in FAMILIES:
        profile=OriginalScenePromptProfileRegistry.get(family); seed=SEEDS[family]; gen=torch.Generator(device='cpu').manual_seed(seed)
        image=pipe(prompt=profile.prompt,width=q.width,height=q.height,num_inference_steps=q.steps,guidance_scale=0.0,generator=gen).images[0]
        path=out/f'{family.value}.png'; image.save(path)
        manifest.append({'family':family.value,'seed':seed,'file':path.name,'generated_subject_policy':profile.generated_subject_policy,'exact_layers_reserved':list(profile.exact_layers_reserved)})
    (out/'manifest.json').write_text(json.dumps({'contract':'pul7sar-cpu-cross-family-synthesis-v1','model':q.model,'device':'cpu','cost_mode':'$0-github-public-runner','publication_ready':False,'scenes':manifest},indent=2),encoding='utf-8')

if __name__=='__main__': main()
