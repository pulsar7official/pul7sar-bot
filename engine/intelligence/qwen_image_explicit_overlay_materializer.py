"""Explicit, fail-closed full-canvas overlay materialization for Phase 18.

This module closes a narrow execution gap between project-native deterministic
layer generation and the CS330 full-canvas overlay composer.  It never chooses
layout.  Every source tile, integer placement, z-order, canvas dimension, story
binding, and candidate binding must already exist in a repository-bound manifest.

The materializer performs only deterministic RGBA alpha placement with no resize,
font selection, text shaping, logo movement, inference, network access, semantic
approval, visual approval, or publication authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from PIL import Image

from engine.intelligence.qwen_image_inference_measurement import sha256_json
from engine.intelligence.qwen_image_production_overlay_composition_runner import (
    FULL_CANVAS_OVERLAY_CONTRACT,
)

SCHEMA = "pul7sar-phase18-explicit-overlay-materialization-v1"
MANIFEST_SCHEMA = "pul7sar-phase18-explicit-overlay-materialization-manifest-v1"
MATERIALIZER_ID = "pul7sar-phase18-explicit-rgba-tile-materializer-v1"
_ALLOWED_LAYER = "editorial_typography"
_DOWNSTREAM_FALSE = (
    "composition_executed",
    "composed_visual_approved",
    "semantic_approved",
    "human_visual_review_approved",
    "genuine_golden_png_created",
    "golden_quality_approved",
    "publication_ready",
)


@dataclass(frozen=True)
class ExplicitOverlayMaterializationRun:
    receipt_path: Path
    overlay_path: Path


def _read_json(path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(code) from exc
    if not isinstance(value, dict):
        raise ValueError(code)
    return value


def _inside_repo_file(repo_root: Path, path: Path, code: str) -> str:
    if path.is_symlink():
        raise ValueError(code)
    root = repo_root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    if not resolved.is_file():
        raise ValueError(code)
    return relative


def _bind_file(repo_root: Path, path: Path, code: str) -> dict[str, Any]:
    relative = _inside_repo_file(repo_root, path, code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    return {
        "repository_relative_path": relative,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


def _reopen_binding(repo_root: Path, binding: Any, code: str) -> Path:
    if not isinstance(binding, Mapping):
        raise ValueError(code)
    relative = binding.get("repository_relative_path")
    if (
        not isinstance(relative, str)
        or not relative
        or Path(relative).is_absolute()
        or ".." in Path(relative).parts
    ):
        raise ValueError(code)
    path = repo_root.resolve() / relative
    canonical = _inside_repo_file(repo_root, path, code)
    if canonical != Path(relative).as_posix():
        raise ValueError(code)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != binding.get("sha256") or len(raw) != binding.get("byte_size"):
        raise ValueError(f"{code}_BYTE_DRIFT")
    return path


def _open_rgba_png(path: Path, code: str) -> Image.Image:
    try:
        with Image.open(path) as image:
            if image.format != "PNG":
                raise ValueError(f"{code}_NOT_PNG")
            if image.mode != "RGBA":
                raise ValueError(f"{code}_NOT_RGBA")
            rgba = image.copy()
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"{code}_DECODE_FAILED") from exc
    if rgba.getchannel("A").getextrema()[1] == 0:
        raise ValueError(f"{code}_FULLY_TRANSPARENT")
    return rgba


def _validate_binding_shape(binding: Any, code: str) -> None:
    if not isinstance(binding, Mapping):
        raise ValueError(code)
    if (
        not isinstance(binding.get("repository_relative_path"), str)
        or not isinstance(binding.get("sha256"), str)
        or len(binding.get("sha256", "")) != 64
        or not isinstance(binding.get("byte_size"), int)
        or binding.get("byte_size", 0) <= 0
    ):
        raise ValueError(code)


def _normalize_tiles(
    manifest: Mapping[str, Any],
    *,
    repo_root: Path,
    width: int,
    height: int,
) -> list[dict[str, Any]]:
    raw_tiles = manifest.get("tiles")
    if not isinstance(raw_tiles, list) or not raw_tiles:
        raise ValueError("QWEN_OVERLAY_MATERIALIZER_TILES_INVALID")
    normalized: list[dict[str, Any]] = []
    seen_z: set[int] = set()
    for raw in raw_tiles:
        if not isinstance(raw, Mapping):
            raise ValueError("QWEN_OVERLAY_MATERIALIZER_TILE_INVALID")
        source = raw.get("source_file")
        x = raw.get("x")
        y = raw.get("y")
        z_index = raw.get("z_index")
        if (
            not isinstance(x, int)
            or isinstance(x, bool)
            or not isinstance(y, int)
            or isinstance(y, bool)
            or not isinstance(z_index, int)
            or isinstance(z_index, bool)
            or z_index in seen_z
        ):
            raise ValueError("QWEN_OVERLAY_MATERIALIZER_TILE_GEOMETRY_INVALID")
        seen_z.add(z_index)
        _validate_binding_shape(source, "QWEN_OVERLAY_MATERIALIZER_TILE_BINDING_INVALID")
        path = _reopen_binding(repo_root, source, "QWEN_OVERLAY_MATERIALIZER_TILE_INVALID")
        tile = _open_rgba_png(path, "QWEN_OVERLAY_MATERIALIZER_TILE_INVALID")
        tile_width, tile_height = tile.size
        if x < 0 or y < 0 or x + tile_width > width or y + tile_height > height:
            raise ValueError("QWEN_OVERLAY_MATERIALIZER_TILE_OUT_OF_BOUNDS")
        normalized.append({
            "source_file": dict(source),
            "x": x,
            "y": y,
            "z_index": z_index,
            "width": tile_width,
            "height": tile_height,
        })
    return sorted(normalized, key=lambda item: item["z_index"])


def _validate_manifest(
    manifest: Mapping[str, Any],
    *,
    repo_root: Path,
) -> tuple[str, dict[str, Any], int, int, list[dict[str, Any]]]:
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ValueError("QWEN_OVERLAY_MATERIALIZER_MANIFEST_SCHEMA_DRIFT")
    if manifest.get("layer_name") != _ALLOWED_LAYER or manifest.get("layer_source") != "deterministic":
        raise ValueError("QWEN_OVERLAY_MATERIALIZER_LAYER_OWNERSHIP_INVALID")
    if manifest.get("renderer_contract") != FULL_CANVAS_OVERLAY_CONTRACT:
        raise ValueError("QWEN_OVERLAY_MATERIALIZER_RENDERER_CONTRACT_DRIFT")
    story_sha = manifest.get("story_snapshot_sha256")
    candidate = manifest.get("candidate_png")
    canvas = manifest.get("canvas")
    if not isinstance(story_sha, str) or len(story_sha) != 64:
        raise ValueError("QWEN_OVERLAY_MATERIALIZER_STORY_BINDING_INVALID")
    _validate_binding_shape(candidate, "QWEN_OVERLAY_MATERIALIZER_CANDIDATE_BINDING_INVALID")
    candidate_path = _reopen_binding(repo_root, candidate, "QWEN_OVERLAY_MATERIALIZER_CANDIDATE_INVALID")
    if not isinstance(canvas, Mapping):
        raise ValueError("QWEN_OVERLAY_MATERIALIZER_CANVAS_INVALID")
    width = canvas.get("width")
    height = canvas.get("height")
    if (
        not isinstance(width, int)
        or isinstance(width, bool)
        or not isinstance(height, int)
        or isinstance(height, bool)
        or width <= 0
        or height <= 0
    ):
        raise ValueError("QWEN_OVERLAY_MATERIALIZER_CANVAS_INVALID")
    try:
        with Image.open(candidate_path) as image:
            if image.format != "PNG" or image.size != (width, height):
                raise ValueError("QWEN_OVERLAY_MATERIALIZER_CANDIDATE_CANVAS_DRIFT")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("QWEN_OVERLAY_MATERIALIZER_CANDIDATE_DECODE_FAILED") from exc
    tiles = _normalize_tiles(manifest, repo_root=repo_root, width=width, height=height)
    return story_sha, dict(candidate), width, height, tiles


def build_explicit_overlay_materialization(
    manifest_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> ExplicitOverlayMaterializationRun:
    """Materialize an explicitly positioned deterministic overlay.

    The manifest is authoritative for geometry.  This function never derives,
    adjusts, centers, wraps, resizes, or otherwise chooses placement.
    """
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_OVERLAY_MATERIALIZER_OUTPUT_INVALID")
    manifest_binding = _bind_file(repo_root, manifest_path, "QWEN_OVERLAY_MATERIALIZER_MANIFEST_INVALID")
    manifest = _read_json(manifest_path, "QWEN_OVERLAY_MATERIALIZER_MANIFEST_INVALID")
    story_sha, candidate, width, height, tiles = _validate_manifest(manifest, repo_root=repo_root)

    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for tile_spec in tiles:
        tile_path = _reopen_binding(
            repo_root,
            tile_spec["source_file"],
            "QWEN_OVERLAY_MATERIALIZER_TILE_INVALID",
        )
        tile = _open_rgba_png(tile_path, "QWEN_OVERLAY_MATERIALIZER_TILE_INVALID")
        canvas.alpha_composite(tile, dest=(tile_spec["x"], tile_spec["y"]))

    alpha_min, alpha_max = canvas.getchannel("A").getextrema()
    if alpha_max == 0:
        raise ValueError("QWEN_OVERLAY_MATERIALIZER_OUTPUT_FULLY_TRANSPARENT")
    if alpha_min == 255:
        raise ValueError("QWEN_OVERLAY_MATERIALIZER_OUTPUT_FULLY_OPAQUE")

    output_dir.mkdir(mode=0o700)
    overlay_path = output_dir / "editorial_typography_overlay.png"
    receipt_path = output_dir / "explicit_overlay_materialization.json"
    tmp_overlay = output_dir / ".editorial_typography_overlay.png.tmp"
    tmp_receipt = output_dir / ".explicit_overlay_materialization.json.tmp"
    try:
        canvas.save(tmp_overlay, format="PNG", optimize=False, compress_level=9)
        os.replace(tmp_overlay, overlay_path)
        overlay_binding = _bind_file(repo_root, overlay_path, "QWEN_OVERLAY_MATERIALIZER_OUTPUT_INVALID")
        receipt: dict[str, Any] = {
            "schema": SCHEMA,
            "status": "QWEN_IMAGE_EXPLICIT_OVERLAY_MATERIALIZED",
            "story_snapshot_sha256": story_sha,
            "source_manifest": manifest_binding,
            "candidate_png": candidate,
            "layer_name": _ALLOWED_LAYER,
            "layer_source": "deterministic",
            "materializer_id": MATERIALIZER_ID,
            "renderer_contract": FULL_CANVAS_OVERLAY_CONTRACT,
            "canvas": {"width": width, "height": height},
            "tiles": tiles,
            "overlay_file": overlay_binding,
            "overlay_materialized": True,
            "composition_executed": False,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "genuine_golden_png_created": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "policy": {
                "layout_must_be_explicit": True,
                "repository_byte_bindings_required": True,
                "rgba_png_tiles_required": True,
                "integer_coordinates_required": True,
                "unique_explicit_z_order_required": True,
                "no_resize_or_transform": True,
                "no_font_or_text_decisions": True,
                "no_brand_or_identity_materialization": True,
                "materialization_is_not_composition": True,
            },
        }
        receipt["receipt_sha256"] = sha256_json(receipt)
        with tmp_receipt.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_receipt, receipt_path)
    except Exception:
        for path in (tmp_overlay, tmp_receipt, overlay_path, receipt_path):
            if path.exists():
                path.unlink()
        if output_dir.exists() and not any(output_dir.iterdir()):
            output_dir.rmdir()
        raise
    return ExplicitOverlayMaterializationRun(receipt_path=receipt_path, overlay_path=overlay_path)


def verify_explicit_overlay_materialization(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    receipt = _read_json(receipt_path, "QWEN_OVERLAY_MATERIALIZER_RECEIPT_INVALID")
    if receipt.get("schema") != SCHEMA:
        raise ValueError("QWEN_OVERLAY_MATERIALIZER_SCHEMA_DRIFT")
    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if claimed != sha256_json(unsigned):
        raise ValueError("QWEN_OVERLAY_MATERIALIZER_RECEIPT_DIGEST_MISMATCH")
    for field in _DOWNSTREAM_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_OVERLAY_MATERIALIZER_PREMATURE_AUTHORITY:{field}")
    if receipt.get("overlay_materialized") is not True:
        raise ValueError("QWEN_OVERLAY_MATERIALIZER_NOT_MATERIALIZED")
    source_manifest = receipt.get("source_manifest")
    manifest_path = _reopen_binding(repo_root, source_manifest, "QWEN_OVERLAY_MATERIALIZER_MANIFEST_INVALID")
    manifest = _read_json(manifest_path, "QWEN_OVERLAY_MATERIALIZER_MANIFEST_INVALID")
    story_sha, candidate, width, height, tiles = _validate_manifest(manifest, repo_root=repo_root)
    if (
        receipt.get("story_snapshot_sha256") != story_sha
        or receipt.get("candidate_png") != candidate
        or receipt.get("canvas") != {"width": width, "height": height}
        or receipt.get("tiles") != tiles
        or receipt.get("layer_name") != _ALLOWED_LAYER
        or receipt.get("layer_source") != "deterministic"
        or receipt.get("renderer_contract") != FULL_CANVAS_OVERLAY_CONTRACT
        or receipt.get("materializer_id") != MATERIALIZER_ID
    ):
        raise ValueError("QWEN_OVERLAY_MATERIALIZER_REPLAY_DRIFT")
    overlay_path = _reopen_binding(
        repo_root,
        receipt.get("overlay_file"),
        "QWEN_OVERLAY_MATERIALIZER_OUTPUT_INVALID",
    )
    overlay = _open_rgba_png(overlay_path, "QWEN_OVERLAY_MATERIALIZER_OUTPUT_INVALID")
    if overlay.size != (width, height):
        raise ValueError("QWEN_OVERLAY_MATERIALIZER_OUTPUT_CANVAS_DRIFT")
    alpha_min, alpha_max = overlay.getchannel("A").getextrema()
    if alpha_max == 0 or alpha_min == 255:
        raise ValueError("QWEN_OVERLAY_MATERIALIZER_OUTPUT_ALPHA_INVALID")
    return receipt
