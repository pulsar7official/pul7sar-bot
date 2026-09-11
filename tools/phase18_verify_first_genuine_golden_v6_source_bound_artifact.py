#!/usr/bin/env python3
"""Fail-closed source-bound replay verifier for First Genuine Golden v6 artifacts.

This CPU-safe wrapper composes the existing byte/semantic artifact replay with the
exact source-commit envelope produced by the Golden v6 workflow. It performs no
model loading, generation, network access, Human Review, Golden approval, or
publication action.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase18_bind_first_genuine_golden_source_commit import verify as verify_source_binding
from phase18_verify_first_genuine_golden_v6_artifact import verify as verify_artifact

SOURCE_BINDING_RECORDED_PATH = "output/phase18_gpu_smoke/first-genuine-golden-v6-source-binding.json"


def _resolve_source_binding(root: Path) -> Path:
    root = root.resolve()
    relative = Path("phase18_gpu_smoke/first-genuine-golden-v6-source-binding.json")
    candidates = (root / relative, root / "output" / relative)
    existing = [candidate.resolve() for candidate in candidates if candidate.is_file()]
    if not existing:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_BINDING_ARTIFACT_MISSING")
    if len(existing) > 1 and existing[0] != existing[1]:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_BINDING_ARTIFACT_AMBIGUOUS")
    binding = existing[0]
    if binding != root and root not in binding.parents:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_BINDING_ESCAPES_ARTIFACT_ROOT")
    return binding


def verify(
    receipt_path: Path,
    *,
    artifact_root: Path | None = None,
    expected_source_sha: str,
) -> dict[str, object]:
    receipt_path = receipt_path.resolve()
    root = (artifact_root or receipt_path.parent).resolve()

    replay = verify_artifact(receipt_path, artifact_root=root)
    binding_path = _resolve_source_binding(root)
    source = verify_source_binding(
        binding_path,
        receipt_path,
        expected_source_sha=expected_source_sha,
    )

    if replay.get("branch") != source.get("branch") or replay.get("candidate") != source.get("candidate"):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_BOUND_ARTIFACT_IDENTITY_DRIFT")
    for field in (
        "human_visual_review_approved",
        "golden_quality_approved",
        "publication_ready",
        "seeds_2_to_4_authorized",
    ):
        if replay.get(field) is not False or source.get(field) is not False:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_SOURCE_BOUND_ILLEGAL_AUTHORITY:{field}")

    result = dict(replay)
    result.update(
        {
            "status": "FIRST_GENUINE_GOLDEN_V6_SOURCE_BOUND_ARTIFACT_REPLAY_VERIFIED",
            "source_commit_sha": expected_source_sha,
            "source_commit_verified": True,
            "source_binding": str(binding_path),
            "resource_lock_sha256": source.get("resource_lock_sha256"),
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--artifact-root", type=Path, default=None)
    parser.add_argument("--expected-source-sha", required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            verify(
                args.receipt,
                artifact_root=args.artifact_root,
                expected_source_sha=args.expected_source_sha,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
