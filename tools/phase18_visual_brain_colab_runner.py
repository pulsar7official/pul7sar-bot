#!/usr/bin/env python3
"""Colab runner for concept-diverse Visual Brain benchmark candidates."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.phase18_build_visual_brain_batch import build_batch


def _env(root: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return env


def _run(command: list[str], root: Path, *, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=root, text=True, capture_output=capture, env=_env(root))


def _json_command(command: list[str], root: Path, label: str) -> dict[str, object]:
    result = _run(command, root)
    if result.returncode != 0:
        raise RuntimeError(f"{label} failed\n{result.stdout[-2500:]}\n{result.stderr[-2500:]}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label} did not emit JSON") from exc


def _display(path: Path) -> bool:
    try:
        from IPython import get_ipython
        if get_ipython() is None:
            return False
        from IPython.display import Image, display
        display(Image(filename=str(path)))
        return True
    except Exception:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="PUL7SAR Visual Brain Colab runner")
    parser.add_argument("--repository-root", default=str(ROOT))
    parser.add_argument("--candidate", type=int, default=1)
    parser.add_argument("--dtype", choices=("auto", "bfloat16", "float16-preview"), default="auto")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--batch-dir", default="output/phase18_handoffs/visual-brain-preview-v1")
    parser.add_argument("--generation-dir", default="output/phase18_generated/visual-brain-preview-v1")
    parser.add_argument("--proof-dir", default="output/phase18_visual_proof/visual-brain-preview-v1")
    args = parser.parse_args()
    root = Path(args.repository_root).resolve()

    branch = _run(["git", "branch", "--show-current"], root).stdout.strip()
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"VISUAL_BRAIN_BRANCH_BLOCKED: expected {EXPECTED_BRANCH!r}, found {branch!r}")
    cpu = _run([sys.executable, str(root / "tools" / "phase18_cpu_validate.py")], root)
    if cpu.returncode != 0:
        raise RuntimeError("VISUAL_BRAIN_CPU_PREFLIGHT_FAILED\n" + cpu.stdout[-2500:] + cpu.stderr[-2500:])

    manifest = build_batch(str(root / args.batch_dir))
    candidates = list(manifest["candidates"])
    if args.candidate < 1 or args.candidate > len(candidates):
        raise ValueError(f"candidate must be between 1 and {len(candidates)}")
    selected = dict(candidates[args.candidate - 1])
    readiness = _json_command(
        [sys.executable, str(root / "tools" / "phase18_local_readiness.py"), "--dtype", args.dtype],
        root,
        "Visual Brain GPU readiness",
    )
    if readiness.get("requested_generation_ready") is not True:
        raise RuntimeError("VISUAL_BRAIN_GPU_NOT_READY\n" + json.dumps(readiness, indent=2))

    proof_dir = root / args.proof_dir
    proof_dir.mkdir(parents=True, exist_ok=True)
    result_path = proof_dir / f"candidate-{args.candidate:02d}-result.json"
    handoff = root / args.batch_dir / str(selected["handoff"])
    command = [
        sys.executable,
        str(root / "tools" / "phase18_flux2_execute.py"),
        "--request", str(handoff),
        "--generation-dir", str(root / args.generation_dir),
        "--proof-dir", str(proof_dir),
        "--dtype", args.dtype,
        "--result", str(result_path),
    ]
    if args.force and result_path.exists():
        result_path.unlink()
    print("=== PUL7SAR VISUAL BRAIN GPU ===")
    print(f"candidate={args.candidate} concept={selected['concept_id']} seed={selected['seed']} dtype={args.dtype}")
    result = _run(command, root, capture=False)
    if result.returncode != 0:
        raise RuntimeError(f"VISUAL_BRAIN_GENERATION_FAILED exit={result.returncode}")
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    png_value = payload.get("png")
    if not isinstance(png_value, str) or not png_value:
        raise RuntimeError("Visual Brain executor did not report PNG")
    png = Path(png_value)
    if not png.is_absolute():
        png = root / png
    summary = {
        "status": "VISUAL_BRAIN_CANDIDATE_GENERATED_AWAITING_CRITIC",
        "candidate": args.candidate,
        "concept_id": selected["concept_id"],
        "concept_title": selected["concept_title"],
        "editorial_metaphor": selected["editorial_metaphor"],
        "seed": selected["seed"],
        "png": str(png.resolve()),
        "visual_critic_required": True,
        "publication_ready": False,
        "displayed_inline": _display(png),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
