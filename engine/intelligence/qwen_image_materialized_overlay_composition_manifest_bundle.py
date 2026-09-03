"""Build exact CS269/CS270 manifests from CS332/CS333 materialized overlays.

CS334 is control-plane only. It verifies same-story/same-candidate lineage and
repository byte bindings, then writes the two manifests consumed by the already
authoritative CS269 and CS270 gates. It never renders or approves pixels.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_canonical_candidate_generated_layer_qa import (
    verify_canonical_candidate_generated_layer_qa,
)
from engine.intelligence.qwen_image_canonical_candidate_deterministic_composition_request import (
    MANIFEST_SCHEMA as CS269_MANIFEST_SCHEMA,
)
from engine.intelligence.qwen_image_canonical_candidate_composition_execution_preflight import (
    PAYLOAD_MANIFEST_SCHEMA as CS270_MANIFEST_SCHEMA,
)
from engine.intelligence.qwen_image_explicit_overlay_materializer import (
    verify_explicit_overlay_materialization,
)
from engine.intelligence.qwen_image_explicit_verified_brand_overlay_materializer import (
    CONTRACT as BRAND_CONTRACT,
    OUTPUT_RENDERER_CONTRACT,
)

SCHEMA = "pul7sar-phase18-materialized-overlay-composition-manifest-bundle-v1"


def _json(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError("CS334_JSON_INVALID")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("CS334_JSON_INVALID")
    return value


def _file(repo_root: Path, raw: object) -> tuple[Path, dict[str, Any]]:
    root = repo_root.resolve()
    path = Path(str(raw or ""))
    path = path if path.is_absolute() else root / path
    path = path.resolve()
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ValueError("CS334_FILE_OUTSIDE_REPOSITORY") from exc
    if path.is_symlink() or not path.is_file():
        raise ValueError("CS334_FILE_INVALID")
    data = path.read_bytes()
    return path, {
        "repository_relative_path": relative.as_posix(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "byte_size": len(data),
    }


def _bound(repo_root: Path, meta: Mapping[str, Any], path_key: str, size_key: str) -> dict[str, Any]:
    _, binding = _file(repo_root, meta.get(path_key))
    if binding["sha256"] != meta.get("sha256") or binding["byte_size"] != meta.get(size_key):
        raise ValueError("CS334_BYTE_DRIFT")
    return binding


def build_materialized_overlay_composition_manifest_bundle(
    cs268_receipt_path: Path,
    typography_receipt_path: Path,
    brand_manifest_path: Path,
    brand_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> Path:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("CS334_OUTPUT_INVALID")

    cs268 = verify_canonical_candidate_generated_layer_qa(cs268_receipt_path, repo_root=repo_root)
    if cs268.get("generated_layer_qa_approved") is not True:
        raise ValueError("CS334_CS268_NOT_APPROVED")
    story_sha = cs268.get("story_snapshot_sha256")
    candidate = cs268.get("candidate_png")
    plan = cs268.get("hybrid_layer_plan")
    if not isinstance(story_sha, str) or len(story_sha) != 64 or not isinstance(candidate, Mapping) or not isinstance(plan, list):
        raise ValueError("CS334_CS268_LINEAGE_INVALID")

    typography = verify_explicit_overlay_materialization(typography_receipt_path, repo_root=repo_root)
    if (
        typography.get("story_snapshot_sha256") != story_sha
        or typography.get("candidate_png") != candidate
        or typography.get("layer_name") != "editorial_typography"
        or typography.get("layer_source") != "deterministic"
        or typography.get("renderer_contract") != OUTPUT_RENDERER_CONTRACT
        or typography.get("overlay_materialized") is not True
    ):
        raise ValueError("CS334_TYPOGRAPHY_LINEAGE_DRIFT")
    typography_binding = typography.get("overlay_file")
    if not isinstance(typography_binding, Mapping):
        raise ValueError("CS334_TYPOGRAPHY_BINDING_INVALID")
    _, actual_typography = _file(repo_root, typography_binding.get("repository_relative_path"))
    if actual_typography != dict(typography_binding):
        raise ValueError("CS334_TYPOGRAPHY_BYTE_DRIFT")

    brand_manifest = _json(brand_manifest_path)
    brand_receipt = _json(brand_receipt_path)
    if (
        brand_manifest.get("contract") != BRAND_CONTRACT
        or brand_manifest.get("story_sha256") != story_sha
        or brand_manifest.get("layer_name") != "pul7sar_brand"
        or brand_manifest.get("layer_source") != "verified_asset"
        or brand_manifest.get("owner_brand_approval_required") is not True
    ):
        raise ValueError("CS334_BRAND_MANIFEST_INVALID")
    brand_candidate = brand_manifest.get("candidate")
    brand_tile = brand_manifest.get("brand_tile")
    if not isinstance(brand_candidate, Mapping) or not isinstance(brand_tile, Mapping):
        raise ValueError("CS334_BRAND_MANIFEST_INVALID")
    candidate_binding = _bound(repo_root, brand_candidate, "path", "size_bytes")
    _bound(repo_root, brand_tile, "path", "size_bytes")
    if candidate_binding["sha256"] != candidate.get("sha256") or candidate_binding["byte_size"] != candidate.get("byte_size"):
        raise ValueError("CS334_BRAND_CANDIDATE_DRIFT")

    forbidden_true = (
        "brand_publication_approved", "composition_executed", "semantic_approved",
        "human_visual_review_approved", "golden_quality_approved",
        "genuine_golden_png_created", "publication_ready", "authoritative",
    )
    if any(brand_receipt.get(field) is not False for field in forbidden_true):
        raise ValueError("CS334_BRAND_PREMATURE_AUTHORITY")
    if brand_receipt.get("overlay_materialized") is not True or brand_receipt.get("owner_brand_approval_required") is not True:
        raise ValueError("CS334_BRAND_RECEIPT_INVALID")
    if (
        brand_receipt.get("story_sha256") != story_sha
        or brand_receipt.get("candidate_sha256") != candidate.get("sha256")
        or brand_receipt.get("candidate_size_bytes") != candidate.get("byte_size")
        or brand_receipt.get("renderer_contract") != OUTPUT_RENDERER_CONTRACT
    ):
        raise ValueError("CS334_BRAND_RECEIPT_DRIFT")
    _, brand_binding = _file(repo_root, brand_receipt.get("output_path"))
    if brand_binding["sha256"] != brand_receipt.get("output_sha256") or brand_binding["byte_size"] != brand_receipt.get("output_size_bytes"):
        raise ValueError("CS334_BRAND_OUTPUT_BYTE_DRIFT")

    required = {
        item.get("name")
        for item in plan
        if isinstance(item, Mapping)
        and item.get("required") is True
        and item.get("source") not in {"generative", "optional"}
    }
    supported = {"editorial_typography", "pul7sar_brand"}
    unsupported = sorted(str(name) for name in required - supported)
    if unsupported:
        raise ValueError("CS334_UNSUPPORTED_REQUIRED_LAYER:" + ",".join(unsupported))
    ownership = {item.get("name"): item.get("source") for item in plan if isinstance(item, Mapping)}
    if ownership.get("editorial_typography") != "deterministic" or ownership.get("pul7sar_brand") != "verified_asset":
        raise ValueError("CS334_LAYER_OWNERSHIP_DRIFT")

    output_dir.mkdir(mode=0o700)
    composition_path = output_dir / "composition_input_manifest.json"
    payload_path = output_dir / "deterministic_payload_manifest.json"
    composition = {
        "schema": CS269_MANIFEST_SCHEMA,
        "story_snapshot_sha256": story_sha,
        "candidate_png": dict(candidate),
        "layers": [
            {
                "name": "editorial_typography",
                "source": "deterministic",
                "renderer_contract": OUTPUT_RENDERER_CONTRACT,
                "payload_sha256": actual_typography["sha256"],
            },
            {
                "name": "pul7sar_brand",
                "source": "verified_asset",
                "asset_file": brand_binding,
            },
        ],
    }
    payload = {
        "schema": CS270_MANIFEST_SCHEMA,
        "story_snapshot_sha256": story_sha,
        "candidate_png_sha256": candidate.get("sha256"),
        "deterministic_payloads": [
            {
                "name": "editorial_typography",
                "renderer_contract": OUTPUT_RENDERER_CONTRACT,
                "payload_file": actual_typography,
            }
        ],
    }
    composition_path.write_text(json.dumps(composition, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    payload_path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    bundle = {
        "schema": SCHEMA,
        "status": "MATERIALIZED_OVERLAY_COMPOSITION_MANIFESTS_READY",
        "story_snapshot_sha256": story_sha,
        "candidate_png": dict(candidate),
        "composition_manifest": _file(repo_root, composition_path)[1],
        "payload_manifest": _file(repo_root, payload_path)[1],
        "composition_input_binding_ready": True,
        "composition_executed": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "policy": {
            "cs269_must_verify_composition_manifest": True,
            "cs270_must_verify_payload_manifest": True,
            "brand_owner_approval_remains_pending": True,
            "no_rendering_or_generation": True,
        },
    }
    bundle_path = output_dir / "materialized_overlay_composition_manifest_bundle.json"
    bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return bundle_path
