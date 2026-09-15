#!/usr/bin/env python3
"""Run and attest the unified first-Golden pre-GPU proof atomically.

This helper performs no model download, model loading, image generation, queue
mutation, publication, or seed expansion. It writes the unified pre-GPU receipt,
attests the exact bytes against the immutable expected source commit, and returns
success only when both stages remain fail-closed and ready.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.phase18_probe_first_golden_pre_gpu import inspect as inspect_pre_gpu
from tools.phase18_attest_first_golden_pre_gpu_receipt import attest

_SHA40 = re.compile(r"^[0-9a-f]{40}$")


def _inside_repository(path: Path) -> Path:
    resolved = path if path.is_absolute() else ROOT / path
    resolved = resolved.resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise RuntimeError("FIRST_GOLDEN_ATTESTED_PRE_GPU_OUTPUT_ESCAPES_REPOSITORY")
    return resolved


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(*, expected_commit: str, receipt_path: Path, attestation_path: Path) -> dict[str, object]:
    if _SHA40.fullmatch(expected_commit) is None:
        return {
            "schema": "pul7sar-phase18-first-golden-attested-pre-gpu-run-v1",
            "expected_commit": expected_commit,
            "ready_for_authoritative_golden_preflight": False,
            "blockers": ["EXPECTED_COMMIT_INVALID"],
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }

    receipt_target = _inside_repository(receipt_path)
    attestation_target = _inside_repository(attestation_path)
    if receipt_target == attestation_target:
        raise RuntimeError("FIRST_GOLDEN_PRE_GPU_RECEIPT_AND_ATTESTATION_MUST_DIFFER")

    receipt = inspect_pre_gpu(expected_commit=expected_commit)
    _write_json(receipt_target, receipt)

    attestation = attest(receipt_path=receipt_target, expected_commit=expected_commit)
    _write_json(attestation_target, attestation)

    blockers: list[str] = []
    if receipt.get("ready_for_authoritative_golden_preflight") is not True:
        blockers.append("PRE_GPU_RECEIPT_NOT_READY")
    if attestation.get("receipt_attested") is not True:
        blockers.append("PRE_GPU_RECEIPT_NOT_ATTESTED")
    for label, report in (("receipt", receipt), ("attestation", attestation)):
        if report.get("network_download_authorized") is not False:
            blockers.append(f"{label.upper()}_NETWORK_AUTHORITY_DRIFT")
        if report.get("generation_authorized") is not False:
            blockers.append(f"{label.upper()}_GENERATION_AUTHORITY_DRIFT")
        if report.get("publication_ready") is not False:
            blockers.append(f"{label.upper()}_PUBLICATION_AUTHORITY_DRIFT")
        if report.get("seeds_2_to_4_authorized") is not False:
            blockers.append(f"{label.upper()}_SEED_AUTHORITY_DRIFT")

    ready = not blockers
    return {
        "schema": "pul7sar-phase18-first-golden-attested-pre-gpu-run-v1",
        "expected_commit": expected_commit,
        "receipt_path": str(receipt_target),
        "attestation_path": str(attestation_target),
        "receipt_schema": receipt.get("schema"),
        "attestation_schema": attestation.get("schema"),
        "receipt_attested": attestation.get("receipt_attested") is True,
        "ready_for_authoritative_golden_preflight": ready,
        "blockers": blockers,
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run and attest the first-Golden unified pre-GPU proof")
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--attestation", type=Path, required=True)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()

    payload = run(
        expected_commit=args.expected_commit,
        receipt_path=args.receipt,
        attestation_path=args.attestation,
    )
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.summary:
        _write_json(_inside_repository(args.summary), payload)
    print(rendered, end="")
    return 0 if payload["ready_for_authoritative_golden_preflight"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
