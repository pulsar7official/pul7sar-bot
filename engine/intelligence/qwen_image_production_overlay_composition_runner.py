"""Production-safe overlay composer for the first genuine Phase 18 Golden path.

The runner is intentionally narrow. It accepts the exact CS270 preflight mapping
handed to CS271 and composes only repository-byte-bound full-canvas PNG layers.
It never invents placement, typography, identity, brand geometry, facts, scores,
or assets. Unsupported or incomplete inputs fail closed.

This module is a top-level CS271 runner source: ``compose_visual`` has the exact
(preflight, output_path, repo_root) signature required by the one-shot boundary.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping

from PIL import Image

from engine.intelligence.qwen_image_canonical_candidate_deterministic_composition_request import (
    SCHEMA as CS269_SCHEMA,
    verify_deterministic_composition_request,
)

FULL_CANVAS_OVERLAY_CONTRACT = "pul7sar-phase18-full-canvas-rgba-overlay-v1"
RUNNER_ID = "pul7sar-phase18-production-overlay-composer-v1"


def _inside_repo_file(repo_root: Path, path: Path, code: str) -> Path:
    root = repo_root.resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(code) from exc
    if path.is_symlink() or not resolved.is_file():
        raise ValueError(code)
    return resolved


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
    path = _inside_repo_file(repo_root, repo_root / relative, code)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != binding.get("sha256") or len(raw) != binding.get("byte_size"):
        raise ValueError(f"{code}_BYTE_DRIFT")
    return path


def _open_full_canvas_png(path: Path, expected_size: tuple[int, int], code: str) -> Image.Image:
    try:
        with Image.open(path) as image:
            if image.format != "PNG":
                raise ValueError(f"{code}_NOT_PNG")
            rgba = image.convert("RGBA")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"{code}_DECODE_FAILED") from exc
    if rgba.size != expected_size:
        raise ValueError(f"{code}_CANVAS_DIMENSION_DRIFT")
    return rgba


def _load_cs269(preflight: Mapping[str, Any], repo_root: Path) -> Mapping[str, Any]:
    source = preflight.get("source_cs269_receipt")
    path = _reopen_binding(repo_root, source, "QWEN_PRODUCTION_COMPOSER_CS269_INVALID")
    cs269 = verify_deterministic_composition_request(path, repo_root=repo_root)
    if cs269.get("schema") != CS269_SCHEMA or cs269.get("composition_request_ready") is not True:
        raise ValueError("QWEN_PRODUCTION_COMPOSER_CS269_NOT_READY")
    if (
        cs269.get("story_snapshot_sha256") != preflight.get("story_snapshot_sha256")
        or cs269.get("candidate_png") != preflight.get("candidate_png")
    ):
        raise ValueError("QWEN_PRODUCTION_COMPOSER_CS269_LINEAGE_DRIFT")
    return cs269


def compose_visual(preflight: Mapping[str, Any], output_path: Path, repo_root: Path) -> None:
    """Compose one candidate using only exact full-canvas bound overlays.

    Layer order is the CS269 ``composition_layers`` order. ``atmosphere_base`` is
    already represented by the canonical candidate. Deterministic layers must
    use ``FULL_CANVAS_OVERLAY_CONTRACT`` and their payload binding must match the
    CS270 preflight. Verified assets must already be full-canvas transparent PNG
    overlays; this runner never guesses placement or resizes them.
    """
    if not isinstance(preflight, Mapping) or preflight.get("composition_execution_ready") is not True:
        raise ValueError("QWEN_PRODUCTION_COMPOSER_PREFLIGHT_NOT_READY")
    repo_root = repo_root.resolve()
    output_path = output_path.resolve()
    try:
        output_path.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError("QWEN_PRODUCTION_COMPOSER_OUTPUT_OUTSIDE_REPOSITORY") from exc
    if output_path.exists() or not output_path.parent.is_dir():
        raise ValueError("QWEN_PRODUCTION_COMPOSER_OUTPUT_INVALID")

    candidate_binding = preflight.get("candidate_png")
    candidate_path = _reopen_binding(repo_root, candidate_binding, "QWEN_PRODUCTION_COMPOSER_CANDIDATE_INVALID")
    try:
        with Image.open(candidate_path) as image:
            if image.format != "PNG":
                raise ValueError("QWEN_PRODUCTION_COMPOSER_CANDIDATE_NOT_PNG")
            canvas = image.convert("RGBA")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("QWEN_PRODUCTION_COMPOSER_CANDIDATE_DECODE_FAILED") from exc

    cs269 = _load_cs269(preflight, repo_root)
    layers = cs269.get("composition_layers")
    payloads = preflight.get("deterministic_payloads")
    if not isinstance(layers, list) or not isinstance(payloads, list):
        raise ValueError("QWEN_PRODUCTION_COMPOSER_LAYER_INPUT_INVALID")
    payload_by_name = {
        item.get("name"): item
        for item in payloads
        if isinstance(item, Mapping) and isinstance(item.get("name"), str)
    }

    seen_base = False
    for layer in layers:
        if not isinstance(layer, Mapping):
            raise ValueError("QWEN_PRODUCTION_COMPOSER_LAYER_INVALID")
        name = layer.get("name")
        source = layer.get("source")
        if not isinstance(name, str) or not name:
            raise ValueError("QWEN_PRODUCTION_COMPOSER_LAYER_INVALID")
        if source == "generative":
            if name != "atmosphere_base" or seen_base:
                raise ValueError("QWEN_PRODUCTION_COMPOSER_GENERATIVE_LAYER_INVALID")
            seen_base = True
            continue
        if source == "optional":
            continue
        if source == "deterministic":
            payload = payload_by_name.get(name)
            if not isinstance(payload, Mapping):
                raise ValueError(f"QWEN_PRODUCTION_COMPOSER_PAYLOAD_MISSING:{name}")
            if payload.get("renderer_contract") != FULL_CANVAS_OVERLAY_CONTRACT:
                raise ValueError(f"QWEN_PRODUCTION_COMPOSER_UNSUPPORTED_RENDERER_CONTRACT:{name}")
            overlay_path = _reopen_binding(
                repo_root,
                payload.get("payload_file"),
                f"QWEN_PRODUCTION_COMPOSER_PAYLOAD_INVALID:{name}",
            )
        elif source == "verified_asset":
            overlay_path = _reopen_binding(
                repo_root,
                layer.get("asset_file"),
                f"QWEN_PRODUCTION_COMPOSER_VERIFIED_ASSET_INVALID:{name}",
            )
        else:
            raise ValueError(f"QWEN_PRODUCTION_COMPOSER_LAYER_SOURCE_INVALID:{name}")

        overlay = _open_full_canvas_png(
            overlay_path,
            canvas.size,
            f"QWEN_PRODUCTION_COMPOSER_OVERLAY_INVALID:{name}",
        )
        canvas = Image.alpha_composite(canvas, overlay)

    if not seen_base:
        raise ValueError("QWEN_PRODUCTION_COMPOSER_ATMOSPHERE_BASE_MISSING")

    # Fixed PNG options, no metadata, no network, no model inference.
    canvas.save(output_path, format="PNG", optimize=False, compress_level=9)
