#!/usr/bin/env python3
"""Run Change Set 234's non-inference live Qwen host identity recheck.

This command imports the live Torch/Diffusers runtime and inspects the current CUDA
host. It never loads Qwen weights, runs inference, generates pixels, mutates queues,
or grants canonical/Golden/publication authority.
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

from engine.intelligence.qwen_image_live_host_recheck import (  # noqa: E402
    build_live_host_recheck_receipt,
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
        raise ValueError("QWEN_LIVE_HOST_RECHECK_PATH_ESCAPE")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-contract", required=True)
    parser.add_argument("--host-qualification", required=True)
    parser.add_argument("--candidate-receipt", required=True)
    parser.add_argument("--execution-receipt", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    contract_path = _repo_bound(Path(args.preflight_contract))
    qualification_path = _repo_bound(Path(args.host_qualification))
    candidate_path = _repo_bound(Path(args.candidate_receipt))
    execution_path = _repo_bound(Path(args.execution_receipt))
    output_path = _repo_bound(Path(args.output))
    for path in (contract_path, qualification_path, candidate_path, execution_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    qualification = json.loads(qualification_path.read_text(encoding="utf-8"))
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    execution = json.loads(execution_path.read_text(encoding="utf-8"))

    receipt = build_live_host_recheck_receipt(
        contract,
        qualification,
        candidate,
        execution,
        qualification_file_sha256=_sha256_file(qualification_path),
        candidate_file_sha256=_sha256_file(candidate_path),
        execution_file_sha256=_sha256_file(execution_path),
        repo_root=REPO_ROOT,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output_path)
    print(receipt["live_host_recheck_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
