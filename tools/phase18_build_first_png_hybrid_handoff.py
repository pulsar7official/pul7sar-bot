#!/usr/bin/env python3
"""Build the canonical Hybrid v5 base summary from proven Candidate 1 bytes.

This tool does not generate pixels or run semantic inspection. It binds the
first-PNG provenance postflight to the exact Golden v5 manifest and writes a
summary that the existing Hybrid v5 semantic/composition path can consume.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.first_png_hybrid_handoff import FirstPngHybridHandoffBuilder
from engine.intelligence.golden_smoke import load_first_candidate

EXPECTED_BRANCH = "phase18/story-intelligence"
DEFAULT_MANIFEST = "output/phase18_handoffs/golden-batch/manifest.json"
DEFAULT_POSTFLIGHT = "output/phase18_gpu_smoke/first-png-provenance-postflight.json"
DEFAULT_OUTPUT = "output/phase18_colab/latest.json"


def _branch(root: Path) -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("FIRST_PNG_HYBRID_HANDOFF_BRANCH_UNAVAILABLE")
    return completed.stdout.strip()


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description="Bridge proven Candidate 1 into the Hybrid v5 review path")
    parser.add_argument("--repository-root", default=str(ROOT))
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--postflight", default=DEFAULT_POSTFLIGHT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    root = Path(args.repository_root).resolve()
    if not (root / "engine" / "intelligence").is_dir():
        raise RuntimeError("repository-root is not a Phase 18 checkout")
    branch = _branch(root)
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"FIRST_PNG_HYBRID_HANDOFF_BRANCH_BLOCKED: {branch}")

    manifest_path = _resolve(root, args.manifest)
    postflight_path = _resolve(root, args.postflight)
    output_path = _resolve(root, args.output)
    if output_path != root and root not in output_path.parents:
        raise RuntimeError("FIRST_PNG_HYBRID_HANDOFF_OUTPUT_ESCAPES_REPOSITORY")
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    if not postflight_path.is_file():
        raise FileNotFoundError(postflight_path)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    postflight = json.loads(postflight_path.read_text(encoding="utf-8"))
    candidate = load_first_candidate(manifest_path)
    payload = FirstPngHybridHandoffBuilder().build(
        repository_root=root,
        candidate=candidate,
        manifest=manifest,
        postflight=postflight,
        branch=branch,
    )
    FirstPngHybridHandoffBuilder.write(output_path, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
