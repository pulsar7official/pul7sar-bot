#!/usr/bin/env python3
"""CPU-only system-memory preflight for the first Golden Candidate.

The command runs before Qwen/FLUX model work and proves enough *currently
available* host RAM exists for the constrained first-Golden path. It performs no
network access, model loading, queue mutation, generation, or publication work.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
DEFAULT_OUTPUT = ROOT / "output" / "phase18_gpu_smoke" / "host-memory-preflight.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.host_memory_qualification import (
    DEFAULT_MINIMUM_AVAILABLE_SYSTEM_RAM_GB,
    HostMemoryQualificationProbe,
)


def _branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if completed.returncode != 0:
        raise RuntimeError("HOST_MEMORY_PREFLIGHT_BRANCH_RESOLUTION_FAILED")
    return completed.stdout.strip()


def _inside_root(path: Path) -> Path:
    target = path if path.is_absolute() else ROOT / path
    target = target.resolve()
    root = ROOT.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("HOST_MEMORY_PREFLIGHT_OUTPUT_ESCAPES_REPOSITORY")
    return target


def run(*, minimum_available_ram_gb: float, output: Path) -> dict[str, object]:
    if _branch() != EXPECTED_BRANCH:
        raise RuntimeError("HOST_MEMORY_PREFLIGHT_BRANCH_BLOCKED")
    report = HostMemoryQualificationProbe(
        minimum_available_ram_gb=minimum_available_ram_gb
    ).inspect()
    payload: dict[str, object] = {
        "schema": "pul7sar-first-golden-host-memory-preflight-v1",
        "branch": EXPECTED_BRANCH,
        **asdict(report),
    }
    target = _inside_root(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Qualify available system RAM before first-Golden model work")
    parser.add_argument(
        "--minimum-available-ram-gb",
        type=float,
        default=DEFAULT_MINIMUM_AVAILABLE_SYSTEM_RAM_GB,
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(minimum_available_ram_gb=args.minimum_available_ram_gb, output=args.output)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("ready") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
