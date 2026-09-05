#!/usr/bin/env python3
"""Route one CS304/CS305 canonical candidate without bypassing identity review.

Change Set 317 closes the manual routing gap immediately after the admitted
candidate semantic checkpoint. A candidate that requires human pixel-identity
review is converted only into the existing byte-bound CS266 review request and
stops. A candidate that does not require pixel-identity review may continue to
the existing CS268 Generated-Layer QA. No identity approval is manufactured and
no semantic, Human Review, Golden, materialization, or publication authority is
granted here.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_canonical_candidate_generated_layer_qa import (
    SCHEMA as GENERATED_LAYER_QA_SCHEMA,
    run_canonical_candidate_generated_layer_qa,
    verify_canonical_candidate_generated_layer_qa,
)
from engine.intelligence.qwen_image_canonical_candidate_identity_requirement import (
    SCHEMA as IDENTITY_REQUIREMENT_SCHEMA,
    verify_identity_requirement,
)
from engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_request import (
    SCHEMA as PIXEL_IDENTITY_REQUEST_SCHEMA,
    build_pixel_identity_review_request,
    verify_pixel_identity_review_request,
)
from engine.intelligence.qwen_image_canonical_candidate_semantic_base_qa import (
    CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_SCHEMA,
    verify_canonical_candidate_semantic_base_qa,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-post-semantic-identity-aware-routing-v1"
_DOWNSTREAM_FALSE = (
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


def _inside_repo_output(repo_root: Path, output_root: Path) -> Path:
    if output_root.is_symlink():
        raise ValueError("QWEN_IDENTITY_ROUTE_OUTPUT_SYMLINK_FORBIDDEN")
    root = repo_root.resolve()
    resolved = output_root.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("QWEN_IDENTITY_ROUTE_OUTPUT_OUTSIDE_REPOSITORY") from exc
    if resolved.exists():
        raise ValueError("QWEN_IDENTITY_ROUTE_OUTPUT_ALREADY_EXISTS")
    if not resolved.parent.is_dir():
        raise ValueError("QWEN_IDENTITY_ROUTE_OUTPUT_PARENT_INVALID")
    return resolved


def _relative(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _assert_closed(receipt: Mapping[str, Any], prefix: str) -> None:
    for field in _DOWNSTREAM_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"{prefix}_PREMATURE_AUTHORITY:{field}")


def _write_summary(path: Path, payload: dict[str, Any]) -> None:
    unsigned = dict(payload)
    unsigned["receipt_sha256"] = sha256_json(unsigned)
    tmp = path.parent / f".{path.name}.tmp"
    with tmp.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(unsigned, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def route_after_identity_requirement(
    cs304_receipt_path: Path,
    cs305_receipt_path: Path,
    output_root: Path,
    *,
    repo_root: Path,
) -> tuple[Path, bool]:
    """Route exact CS304/CS305 lineage to CS266 or CS268, fail-closed."""
    root = _inside_repo_output(repo_root, output_root)
    root.mkdir(mode=0o700)

    cs304 = verify_canonical_candidate_semantic_base_qa(
        cs304_receipt_path, repo_root=repo_root
    )
    cs305 = verify_identity_requirement(cs305_receipt_path, repo_root=repo_root)
    if (
        cs304.get("schema") != CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_SCHEMA
        or cs304.get("semantic_base_scene_approved") is not True
    ):
        raise ValueError("QWEN_IDENTITY_ROUTE_CS304_NOT_APPROVED")
    if (
        cs305.get("schema") != IDENTITY_REQUIREMENT_SCHEMA
        or cs305.get("identity_requirement_classified") is not True
    ):
        raise ValueError("QWEN_IDENTITY_ROUTE_CS305_NOT_CLASSIFIED")
    _assert_closed(cs304, "QWEN_IDENTITY_ROUTE_CS304")
    _assert_closed(cs305, "QWEN_IDENTITY_ROUTE_CS305")

    story_sha = cs304.get("story_snapshot_sha256")
    candidate = cs304.get("candidate_png")
    if story_sha != cs305.get("story_snapshot_sha256") or candidate != cs305.get("candidate_png"):
        raise ValueError("QWEN_IDENTITY_ROUTE_UPSTREAM_LINEAGE_DRIFT")
    review_required = cs305.get("pixel_identity_review_required")
    if not isinstance(review_required, bool):
        raise ValueError("QWEN_IDENTITY_ROUTE_REVIEW_REQUIREMENT_INVALID")

    summary_path = root / "post_semantic_identity_route_receipt.json"
    base: dict[str, Any] = {
        "schema": SCHEMA,
        "story_snapshot_sha256": story_sha,
        "candidate_png": candidate,
        "source_cs304_receipt": _relative(repo_root, cs304_receipt_path),
        "source_cs305_receipt": _relative(repo_root, cs305_receipt_path),
        "pixel_identity_review_required": review_required,
        "identity_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }

    if review_required:
        request_dir = root / "cs266-pixel-identity-review-request"
        request_run = build_pixel_identity_review_request(
            cs305_receipt_path,
            request_dir,
            repo_root=repo_root,
        )
        request = verify_pixel_identity_review_request(
            request_run.receipt_path,
            repo_root=repo_root,
        )
        if request.get("schema") != PIXEL_IDENTITY_REQUEST_SCHEMA:
            raise ValueError("QWEN_IDENTITY_ROUTE_CS266_SCHEMA_DRIFT")
        _assert_closed(request, "QWEN_IDENTITY_ROUTE_CS266")
        if (
            request.get("story_snapshot_sha256") != story_sha
            or request.get("candidate_png") != candidate
            or request.get("pixel_identity_review_required") is not True
            or request.get("pixel_identity_review_request_created") is not True
            or request.get("pixel_identity_review_executed") is not False
            or request.get("identity_approved") is not False
        ):
            raise ValueError("QWEN_IDENTITY_ROUTE_CS266_STATE_INVALID")
        base.update(
            {
                "status": "QWEN_IMAGE_CANONICAL_CANDIDATE_AWAITING_PIXEL_IDENTITY_REVIEW",
                "route": "CS266_PIXEL_IDENTITY_REVIEW_REQUIRED",
                "cs266_receipt": _relative(repo_root, request_run.receipt_path),
                "pixel_identity_review_request_created": True,
                "generated_layer_qa_executed": False,
                "generated_layer_qa_approved": False,
            }
        )
        _write_summary(summary_path, base)
        return summary_path, True

    generated_dir = root / "cs268-generated-layer-qa"
    generated_run = run_canonical_candidate_generated_layer_qa(
        cs304_receipt_path,
        cs305_receipt_path,
        generated_dir,
        repo_root=repo_root,
        cs267_receipt_path=None,
    )
    generated = verify_canonical_candidate_generated_layer_qa(
        generated_run.receipt_path,
        repo_root=repo_root,
    )
    if generated.get("schema") != GENERATED_LAYER_QA_SCHEMA:
        raise ValueError("QWEN_IDENTITY_ROUTE_CS268_SCHEMA_DRIFT")
    _assert_closed(generated, "QWEN_IDENTITY_ROUTE_CS268")
    if (
        generated.get("story_snapshot_sha256") != story_sha
        or generated.get("candidate_png") != candidate
        or generated.get("pixel_identity_review_required") is not False
        or generated.get("identity_approved") is not False
        or generated.get("composition_executed") is not False
        or generated.get("composed_visual_approved") is not False
    ):
        raise ValueError("QWEN_IDENTITY_ROUTE_CS268_STATE_INVALID")
    approved = generated.get("generated_layer_qa_approved") is True
    base.update(
        {
            "status": (
                "QWEN_IMAGE_CANONICAL_CANDIDATE_GENERATED_LAYER_QA_PASSED"
                if approved
                else "QWEN_IMAGE_CANONICAL_CANDIDATE_GENERATED_LAYER_QA_REJECTED"
            ),
            "route": "CS268_GENERATED_LAYER_QA_NO_PIXEL_IDENTITY_REVIEW_REQUIRED",
            "cs268_receipt": _relative(repo_root, generated_run.receipt_path),
            "pixel_identity_review_request_created": False,
            "generated_layer_qa_executed": True,
            "generated_layer_qa_approved": approved,
        }
    )
    _write_summary(summary_path, base)
    return summary_path, approved


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Route an exact approved CS304/CS305 candidate: create CS266 and stop when "
            "human pixel identity review is required, otherwise run CS268 Generated-Layer QA."
        )
    )
    parser.add_argument("--cs304-receipt", type=Path, required=True)
    parser.add_argument("--cs305-receipt", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    summary, accepted = route_after_identity_requirement(
        args.cs304_receipt,
        args.cs305_receipt,
        args.output_root,
        repo_root=args.repo_root,
    )
    payload = json.loads(summary.read_text(encoding="utf-8"))
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
