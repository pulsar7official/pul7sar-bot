#!/usr/bin/env python3
"""Admit the locked Golden Candidate 1 to the measured local original-scene runtime.

This command performs no generation and no queue mutation. It is intended to run
on the same compatible GPU host immediately before the canonical first-PNG path.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.flux2_klein_diffusers import Flux2KleinDiffusersProbe
from engine.intelligence.golden_original_scene_admission import GoldenOriginalSceneAdmissionGate
from engine.intelligence.golden_smoke import load_first_candidate
from engine.intelligence.local_dtype import LocalDTypeSelector
from engine.intelligence.local_readiness_service import LocalReadinessService
from engine.intelligence.local_runtime import LocalRuntimeProbe
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_DTYPE = "bfloat16"


def _current_branch(repository_root: Path) -> str:
    import subprocess

    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repository_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("unable to resolve current branch")
    return completed.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Admit Golden Candidate 1 to the provider-neutral original-scene runtime")
    parser.add_argument("--repository-root", default=str(ROOT))
    parser.add_argument("--manifest", default="output/phase18_handoffs/golden-batch/manifest.json")
    parser.add_argument("--output", default="output/phase18_gpu_smoke/original-scene-runtime-admission.json")
    args = parser.parse_args()

    repository_root = Path(args.repository_root).resolve()
    if _current_branch(repository_root) != EXPECTED_BRANCH:
        raise RuntimeError("ORIGINAL_SCENE_ADMISSION_REQUIRES_PHASE18_BRANCH")

    manifest = Path(args.manifest)
    if not manifest.is_absolute():
        manifest = repository_root / manifest
    output = Path(args.output)
    if not output.is_absolute():
        output = repository_root / output
    try:
        output.relative_to(repository_root)
    except ValueError as exc:
        raise RuntimeError("ORIGINAL_SCENE_ADMISSION_OUTPUT_MUST_STAY_INSIDE_REPOSITORY") from exc

    candidate = load_first_candidate(manifest)
    backend = Flux2KleinDiffusersProbe().probe()
    runtime = LocalRuntimeProbe().detect()
    readiness = LocalReadinessService().evaluate(
        model=FLUX2_KLEIN_4B_LOCAL,
        backend=backend,
        runtime=runtime,
    ).generation
    dtype = LocalDTypeSelector().select(runtime, "auto")
    if dtype.resolved != EXPECTED_DTYPE:
        raise RuntimeError("GOLDEN_ORIGINAL_SCENE_ADMISSION_REQUIRES_NATIVE_BF16")

    receipt = GoldenOriginalSceneAdmissionGate().admit(candidate=candidate, readiness=readiness)
    payload = receipt.as_dict()
    payload.update({
        "resolved_dtype": dtype.resolved,
        "runtime_ready": readiness.ready,
        "generation_authorized": False,
        "queue_mutated": False,
        "png_created": False,
        "semantic_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    })
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
