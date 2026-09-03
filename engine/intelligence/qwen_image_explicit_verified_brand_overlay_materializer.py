from __future__ import annotations

"""Materialize an explicitly placed, byte-bound PUL7SAR verified-brand tile.

This primitive is intentionally narrow.  It does not draw, resize, recolor,
re-typeset, or auto-place the PUL7SAR mark.  The caller must supply an exact
RGBA PNG tile plus explicit canvas coordinates.  Publication brand approval
remains a later human/final-presentation authority.
"""

from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping

from PIL import Image

CONTRACT = "pul7sar-phase18-explicit-verified-brand-overlay-materialization-v1"
LAYER_NAME = "pul7sar_brand"
LAYER_SOURCE = "verified_asset"
OUTPUT_RENDERER_CONTRACT = "pul7sar-phase18-full-canvas-rgba-overlay-v1"


class BrandOverlayMaterializationError(RuntimeError):
    pass


@dataclass(frozen=True)
class MaterializedVerifiedBrandOverlay:
    contract: str
    story_sha256: str
    layer_name: str
    layer_source: str
    candidate_sha256: str
    candidate_size_bytes: int
    brand_tile_sha256: str
    brand_tile_size_bytes: int
    placement_x: int
    placement_y: int
    canvas_width: int
    canvas_height: int
    output_path: str
    output_sha256: str
    output_size_bytes: int
    output_mode: str
    renderer_contract: str
    overlay_materialized: bool
    brand_publication_approved: bool
    owner_brand_approval_required: bool
    composition_executed: bool
    semantic_approved: bool
    human_visual_review_approved: bool
    golden_quality_approved: bool
    genuine_golden_png_created: bool
    publication_ready: bool
    authoritative: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _sha(data: bytes) -> str:
    return sha256(data).hexdigest()


def _require_sha(value: object, field: str) -> str:
    text = str(value or "").strip().lower()
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise BrandOverlayMaterializationError(f"invalid_{field}")
    return text


def _repo_file(repo_root: Path, raw_path: object, field: str) -> Path:
    root = repo_root.resolve()
    raw = str(raw_path or "").strip()
    if not raw:
        raise BrandOverlayMaterializationError(f"missing_{field}_path")
    candidate = (root / raw).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise BrandOverlayMaterializationError(f"{field}_path_outside_repository") from exc
    if not candidate.is_file() or candidate.is_symlink():
        raise BrandOverlayMaterializationError(f"{field}_file_unavailable")
    return candidate


def _bound_bytes(repo_root: Path, payload: Mapping[str, Any], field: str) -> tuple[Path, bytes]:
    path = _repo_file(repo_root, payload.get("path"), field)
    data = path.read_bytes()
    expected_sha = _require_sha(payload.get("sha256"), f"{field}_sha256")
    expected_size = int(payload.get("size_bytes", -1))
    if _sha(data) != expected_sha:
        raise BrandOverlayMaterializationError(f"{field}_byte_drift")
    if len(data) != expected_size:
        raise BrandOverlayMaterializationError(f"{field}_size_drift")
    return path, data


def materialize_explicit_verified_brand_overlay(
    manifest: Mapping[str, Any],
    output_path: str | Path,
    repo_root: str | Path,
) -> MaterializedVerifiedBrandOverlay:
    if str(manifest.get("contract", "")) != CONTRACT:
        raise BrandOverlayMaterializationError("unsupported_contract")
    if str(manifest.get("layer_name", "")) != LAYER_NAME:
        raise BrandOverlayMaterializationError("unsupported_layer_name")
    if str(manifest.get("layer_source", "")) != LAYER_SOURCE:
        raise BrandOverlayMaterializationError("unsupported_layer_source")
    if manifest.get("owner_brand_approval_required") is not True:
        raise BrandOverlayMaterializationError("owner_brand_approval_must_remain_required")

    story_sha = _require_sha(manifest.get("story_sha256"), "story_sha256")
    root = Path(repo_root)
    candidate_meta = manifest.get("candidate")
    tile_meta = manifest.get("brand_tile")
    placement = manifest.get("placement")
    if not isinstance(candidate_meta, Mapping):
        raise BrandOverlayMaterializationError("missing_candidate")
    if not isinstance(tile_meta, Mapping):
        raise BrandOverlayMaterializationError("missing_brand_tile")
    if not isinstance(placement, Mapping):
        raise BrandOverlayMaterializationError("missing_placement")

    _, candidate_bytes = _bound_bytes(root, candidate_meta, "candidate")
    _, tile_bytes = _bound_bytes(root, tile_meta, "brand_tile")

    from io import BytesIO

    try:
        with Image.open(BytesIO(candidate_bytes)) as candidate_img:
            candidate_img.verify()
        with Image.open(BytesIO(candidate_bytes)) as candidate_img:
            canvas_width, canvas_height = candidate_img.size
        with Image.open(BytesIO(tile_bytes)) as tile_img:
            if tile_img.format != "PNG" or tile_img.mode != "RGBA":
                raise BrandOverlayMaterializationError("brand_tile_must_be_native_rgba_png")
            tile = tile_img.copy()
    except BrandOverlayMaterializationError:
        raise
    except Exception as exc:
        raise BrandOverlayMaterializationError("invalid_png_input") from exc

    expected_width = int(candidate_meta.get("width", -1))
    expected_height = int(candidate_meta.get("height", -1))
    if (canvas_width, canvas_height) != (expected_width, expected_height):
        raise BrandOverlayMaterializationError("candidate_dimension_drift")
    if tile.getbbox() is None or tile.getchannel("A").getbbox() is None:
        raise BrandOverlayMaterializationError("brand_tile_has_empty_alpha")

    x = int(placement.get("x", -1))
    y = int(placement.get("y", -1))
    if x < 0 or y < 0 or x + tile.width > canvas_width or y + tile.height > canvas_height:
        raise BrandOverlayMaterializationError("brand_tile_out_of_bounds")

    canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
    canvas.alpha_composite(tile, dest=(x, y))

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, format="PNG")
    output_bytes = output.read_bytes()

    return MaterializedVerifiedBrandOverlay(
        contract=CONTRACT,
        story_sha256=story_sha,
        layer_name=LAYER_NAME,
        layer_source=LAYER_SOURCE,
        candidate_sha256=_sha(candidate_bytes),
        candidate_size_bytes=len(candidate_bytes),
        brand_tile_sha256=_sha(tile_bytes),
        brand_tile_size_bytes=len(tile_bytes),
        placement_x=x,
        placement_y=y,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        output_path=str(output),
        output_sha256=_sha(output_bytes),
        output_size_bytes=len(output_bytes),
        output_mode="RGBA",
        renderer_contract=OUTPUT_RENDERER_CONTRACT,
        overlay_materialized=True,
        brand_publication_approved=False,
        owner_brand_approval_required=True,
        composition_executed=False,
        semantic_approved=False,
        human_visual_review_approved=False,
        golden_quality_approved=False,
        genuine_golden_png_created=False,
        publication_ready=False,
        authoritative=False,
    )
