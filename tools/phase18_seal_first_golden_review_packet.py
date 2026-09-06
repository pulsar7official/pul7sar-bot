#!/usr/bin/env python3
"""Seal and replay-verify the Candidate 1 Golden human-review packet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from engine.intelligence.first_golden_review_packet_integrity import (
    FirstGoldenReviewPacketIntegrity,
    verification_payload,
)

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
DEFAULT_PACKET = ROOT / "output" / "phase18_gpu_smoke" / "first-golden-human-review-packet.json"
DEFAULT_MANIFEST = ROOT / "output" / "phase18_gpu_smoke" / "first-golden-human-review-integrity.json"
DEFAULT_VERIFICATION = ROOT / "output" / "phase18_gpu_smoke" / "first-golden-human-review-integrity-verification.json"


def _branch() -> str:
    completed = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_SEAL_BRANCH_RESOLUTION_FAILED")
    return completed.stdout.strip()


def _inside_root(path: Path) -> Path:
    resolved = path if path.is_absolute() else ROOT / path
    resolved = resolved.resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_SEAL_OUTPUT_ESCAPES_REPOSITORY")
    return resolved


def run(*, packet_path: Path, manifest_path: Path, verification_path: Path) -> dict[str, object]:
    if _branch() != EXPECTED_BRANCH:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_SEAL_BRANCH_BLOCKED")
    manifest_path = _inside_root(manifest_path)
    verification_path = _inside_root(verification_path)
    integrity = FirstGoldenReviewPacketIntegrity(root=ROOT)
    manifest = integrity.build_manifest(packet_path=packet_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    decision = integrity.verify_manifest(manifest=manifest)
    receipt = verification_payload(decision)
    verification_path.parent.mkdir(parents=True, exist_ok=True)
    verification_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    if not decision.verified:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_PACKET_INTEGRITY_REPLAY_FAILED: " + ", ".join(decision.failures))

    return {
        "schema": "pul7sar-first-golden-review-seal-v1",
        "status": "FIRST_GOLDEN_REVIEW_PACKET_SEALED_AND_VERIFIED",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "cost_mode": "$0-local",
        "packet": str(_inside_root(packet_path)),
        "manifest": str(manifest_path),
        "verification": str(verification_path),
        "manifest_sha256": decision.manifest_sha256,
        "human_visual_review_required": True,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Seal and replay-verify the exact Candidate 1 human-review packet")
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--verification", type=Path, default=DEFAULT_VERIFICATION)
    args = parser.parse_args()
    payload = run(packet_path=args.packet, manifest_path=args.manifest, verification_path=args.verification)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
