#!/usr/bin/env python3
"""Package the first genuine Golden v6 Candidate 1 into a review-only evidence bundle.

CPU-safe, zero-cost and fail-closed. This tool performs no generation, no model
loading, no network access, no Human Review, no Golden approval and no
publication. It accepts only the already-verified fresh/source-bound and
snapshot-bound manifests, replays every referenced evidence digest plus the PNG
bytes, and copies that exact evidence set into a new empty run-scoped bundle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_COST_MODE = "$0-local"
FRESH_SCHEMA = "pul7sar-phase18-first-genuine-golden-v6-fresh-source-bound-manifest-v3"
SNAPSHOT_SCHEMA = "pul7sar-phase18-first-genuine-golden-v6-snapshot-bound-manifest-v1"
BUNDLE_SCHEMA = "pul7sar-phase18-first-genuine-golden-v6-review-bundle-v1"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_INVALID_JSON:{path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_INVALID_OBJECT:{path}")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_false(payload: dict[str, Any], fields: tuple[str, ...], *, label: str) -> None:
    for field in fields:
        if payload.get(field) is not False:
            raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_AUTHORITY_DRIFT:{label}:{field}")


def _inside_repo(path_value: str, repo_root: Path) -> Path:
    candidate = (repo_root / path_value).resolve() if not Path(path_value).is_absolute() else Path(path_value).resolve()
    root = repo_root.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_PATH_OUTSIDE_REPO") from exc
    if not candidate.is_file():
        raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_FILE_MISSING:{candidate}")
    return candidate


def _verify_ref(record: object, *, repo_root: Path, label: str) -> Path:
    if not isinstance(record, dict):
        raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_REF_INVALID:{label}")
    path_value = record.get("path")
    expected_sha = record.get("sha256")
    if not isinstance(path_value, str) or not path_value:
        raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_REF_PATH_INVALID:{label}")
    if not re.fullmatch(r"[0-9a-f]{64}", str(expected_sha or "")):
        raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_REF_SHA_INVALID:{label}")
    path = _inside_repo(path_value, repo_root)
    if _sha256(path) != expected_sha:
        raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_REF_SHA_DRIFT:{label}")
    return path


def _copy_entry(src: Path, dst: Path, *, bundle_path: str, expected_sha: str | None = None) -> dict[str, Any]:
    if expected_sha is not None and _sha256(src) != expected_sha:
        raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_COPY_SOURCE_SHA_DRIFT:{src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    actual_sha = _sha256(dst)
    if expected_sha is not None and actual_sha != expected_sha:
        raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_COPY_SHA_DRIFT:{dst}")
    return {"path": bundle_path, "sha256": actual_sha, "bytes": dst.stat().st_size}


def build_bundle(*, fresh_manifest_path: Path, snapshot_manifest_path: Path, repo_root: Path,
                 bundle_dir: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    fresh_path = fresh_manifest_path.resolve()
    snapshot_path = snapshot_manifest_path.resolve()
    for path in (fresh_path, snapshot_path):
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise RuntimeError("GOLDEN_REVIEW_BUNDLE_MANIFEST_OUTSIDE_REPO") from exc

    fresh = _load(fresh_path)
    snapshot = _load(snapshot_path)
    if fresh.get("schema") != FRESH_SCHEMA or snapshot.get("schema") != SNAPSHOT_SCHEMA:
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_SCHEMA_DRIFT")
    for payload, label in ((fresh, "fresh"), (snapshot, "snapshot")):
        if payload.get("branch") != EXPECTED_BRANCH or payload.get("candidate") != 1:
            raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_IDENTITY_DRIFT:{label}")
        if payload.get("cost_mode") != EXPECTED_COST_MODE or payload.get("offline_only") is not True:
            raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_POLICY_DRIFT:{label}")
        if payload.get("eligible_for_human_visual_review") is not True:
            raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_NOT_REVIEW_ELIGIBLE:{label}")
        _require_false(payload, (
            "authoritative_gate", "network_download_authorized", "generation_authorized",
            "human_visual_review_approved", "golden_quality_approved", "publication_ready",
            "seeds_2_to_4_authorized",
        ), label=label)

    source_sha = fresh.get("source_commit_sha")
    png_sha = fresh.get("png_sha256")
    if snapshot.get("source_commit_sha") != source_sha or snapshot.get("png_sha256") != png_sha:
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_UPSTREAM_IDENTITY_DRIFT")
    if not re.fullmatch(r"[0-9a-f]{40}", str(source_sha or "")) or not re.fullmatch(r"[0-9a-f]{64}", str(png_sha or "")):
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_DIGEST_INVALID")

    upstream_ref = snapshot.get("upstream_manifest")
    upstream_path = _verify_ref(upstream_ref, repo_root=root, label="snapshot-upstream")
    if upstream_path != fresh_path or upstream_ref.get("sha256") != _sha256(fresh_path):
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_FRESH_MANIFEST_LINK_DRIFT")
    inventory_path = _verify_ref(snapshot.get("recorded_snapshot_inventory"), repo_root=root, label="snapshot-inventory")

    evidence = fresh.get("evidence")
    if not isinstance(evidence, dict) or not evidence:
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_EVIDENCE_INVALID")
    png_record = evidence.get("png")
    png_path = _verify_ref(png_record, repo_root=root, label="png")
    if png_record.get("sha256") != png_sha or png_record.get("bytes") != png_path.stat().st_size:
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_PNG_RECORD_DRIFT")
    with png_path.open("rb") as handle:
        if handle.read(len(PNG_SIGNATURE)) != PNG_SIGNATURE:
            raise RuntimeError("GOLDEN_REVIEW_BUNDLE_PNG_SIGNATURE_INVALID")

    exact_evidence: dict[str, Path] = {}
    for key, record in evidence.items():
        if key == "png":
            continue
        if not re.fullmatch(r"[a-z0-9_]+", str(key)):
            raise RuntimeError("GOLDEN_REVIEW_BUNDLE_EVIDENCE_KEY_INVALID")
        exact_evidence[key] = _verify_ref(record, repo_root=root, label=f"evidence:{key}")

    target = bundle_dir.resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_TARGET_OUTSIDE_REPO") from exc
    if target.exists():
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_TARGET_ALREADY_EXISTS")
    temporary = target.with_name(target.name + ".tmp")
    if temporary.exists():
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_TEMP_TARGET_ALREADY_EXISTS")

    entries: dict[str, dict[str, Any]] = {}
    try:
        temporary.mkdir(parents=True, exist_ok=False)
        entries["candidate_png"] = _copy_entry(
            png_path, temporary / "candidate-1.png", bundle_path="candidate-1.png", expected_sha=png_sha
        )
        entries["fresh_source_bound_manifest"] = _copy_entry(
            fresh_path, temporary / "fresh-source-bound-manifest.json", bundle_path="fresh-source-bound-manifest.json"
        )
        entries["snapshot_bound_manifest"] = _copy_entry(
            snapshot_path, temporary / "snapshot-bound-manifest.json", bundle_path="snapshot-bound-manifest.json"
        )
        entries["approved_snapshot_inventory"] = _copy_entry(
            inventory_path, temporary / "approved-snapshot-inventory.json", bundle_path="approved-snapshot-inventory.json"
        )
        for key, src in sorted(exact_evidence.items()):
            suffix = src.suffix or ".bin"
            relative = f"evidence/{key}{suffix}"
            entries[f"evidence_{key}"] = _copy_entry(
                src, temporary / relative, bundle_path=relative
            )

        manifest = {
            "schema": BUNDLE_SCHEMA,
            "status": "FIRST_GENUINE_GOLDEN_V6_REVIEW_BUNDLE_CRYPTOGRAPHICALLY_BOUND",
            "branch": EXPECTED_BRANCH,
            "candidate": 1,
            "cost_mode": EXPECTED_COST_MODE,
            "offline_only": True,
            "source_commit_sha": source_sha,
            "png_sha256": png_sha,
            "exact_evidence_only": True,
            "eligible_for_human_visual_review": True,
            "entries": entries,
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        (temporary / "review-bundle-manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        temporary.replace(target)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary, ignore_errors=True)
        raise
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fresh-manifest", type=Path, required=True)
    parser.add_argument("--snapshot-manifest", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--bundle-dir", type=Path, required=True)
    args = parser.parse_args()
    manifest = build_bundle(
        fresh_manifest_path=args.fresh_manifest,
        snapshot_manifest_path=args.snapshot_manifest,
        repo_root=args.repo_root,
        bundle_dir=args.bundle_dir,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
