#!/usr/bin/env python3
"""Build the CPU-only Change Set 233 controlled Golden-trial preflight contract.

This command does not perform a live host recheck, invoke CUDA, load Qwen Image,
generate pixels, mutate a queue, or authorize canonical/Golden/publication output.
It only replays the existing host-bound qualification chain and locks the evidence
that a later live generation gate must require.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (  # noqa: E402
    build_controlled_golden_trial_preflight_contract,
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_bound(path: Path) -> Path:
    resolved = path.expanduser()
    if not resolved.is_absolute():
        resolved = REPO_ROOT / resolved
    resolved = resolved.resolve()
    if not resolved.is_relative_to(REPO_ROOT):
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_PATH_ESCAPE")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host-qualification", required=True)
    parser.add_argument("--candidate-receipt", required=True)
    parser.add_argument("--execution-receipt", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    qualification_path = _repo_bound(Path(args.host_qualification))
    candidate_path = _repo_bound(Path(args.candidate_receipt))
    execution_path = _repo_bound(Path(args.execution_receipt))
    output_path = _repo_bound(Path(args.output))
    for path in (qualification_path, candidate_path, execution_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    qualification = json.loads(qualification_path.read_text(encoding="utf-8"))
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    execution = json.loads(execution_path.read_text(encoding="utf-8"))
    contract = build_controlled_golden_trial_preflight_contract(
        qualification,
        candidate,
        execution,
        qualification_file_sha256=_sha256_file(qualification_path),
        candidate_file_sha256=_sha256_file(candidate_path),
        execution_file_sha256=_sha256_file(execution_path),
        repo_root=REPO_ROOT,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(contract, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output_path)
    print(contract["preflight_contract_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
