#!/usr/bin/env python3
"""Capture and bind authoritative first-Golden pre-generation evidence.

Fail-closed, $0-local/offline-only preparatory orchestrator. It captures the four
pieces consumed by the canonical-fresh launcher, then semantically and
cryptographically binds them to the exact Phase 18 source SHA. It never starts
generation and never grants publication, Golden-quality, or Seeds 2-4 authority.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.phase18_bind_authoritative_first_golden_pre_generation_evidence import bind

BRANCH = "phase18/story-intelligence"
_SHA40 = re.compile(r"^[0-9a-f]{40}$")


def _inside(path: Path) -> Path:
    target = path if path.is_absolute() else ROOT / path
    target = target.resolve()
    root = ROOT.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("AUTHORITATIVE_PRE_GENERATION_EVIDENCE_PATH_ESCAPES_REPOSITORY")
    return target


def _run(tool: str, output: Path) -> None:
    subprocess.run(
        [sys.executable, str(ROOT / tool), "--output", str(output)],
        cwd=ROOT,
        check=True,
        env={**os.environ, "PUL7SAR_PHASE18_COST_MODE": "$0-local", "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"},
    )


def capture(*, source_sha: str, output_dir: Path) -> dict[str, object]:
    if _SHA40.fullmatch(source_sha) is None:
        raise RuntimeError("AUTHORITATIVE_PRE_GENERATION_SOURCE_SHA_INVALID")
    if os.environ.get("PUL7SAR_PHASE18_COST_MODE") != "$0-local":
        raise RuntimeError("AUTHORITATIVE_PRE_GENERATION_REQUIRES_ZERO_COST_MODE")
    if os.environ.get("HF_HUB_OFFLINE") != "1" or os.environ.get("TRANSFORMERS_OFFLINE") != "1":
        raise RuntimeError("AUTHORITATIVE_PRE_GENERATION_REQUIRES_OFFLINE_MODEL_RESOLUTION")

    directory = _inside(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    network = directory / "first-genuine-golden-v6-zero-cost-network-guard.json"
    runner = directory / "first-genuine-golden-v6-runner-identity.json"
    snapshots = directory / "first-genuine-golden-v6-approved-snapshot-inventory.json"
    blocker = directory / "first-genuine-golden-v6-execution-blocker-probe.json"
    binding_path = directory / "first-genuine-golden-v6-authoritative-pre-generation-binding.json"

    _run("tools/phase18_capture_zero_cost_network_guard_evidence.py", network)
    _run("tools/phase18_capture_first_golden_runner_identity.py", runner)
    _run("tools/phase18_capture_approved_snapshot_inventory.py", snapshots)
    _run("tools/phase18_probe_first_golden_execution_blocker.py", blocker)

    binding = bind(
        source_sha=source_sha,
        branch=BRANCH,
        network=network,
        runner=runner,
        snapshots=snapshots,
        blocker=blocker,
    )
    binding_path.write_text(json.dumps(binding, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "schema": "pul7sar-phase18-authoritative-pre-generation-evidence-capture-v1",
        "branch": BRANCH,
        "source_sha": source_sha,
        "binding": str(binding_path),
        "ready": True,
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "human_review_authorized": False,
        "golden_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture and bind authoritative first-Golden pre-generation evidence without generation")
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("output/phase18_gpu_smoke"))
    args = parser.parse_args()
    payload = capture(source_sha=args.source_sha, output_dir=args.output_dir)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
