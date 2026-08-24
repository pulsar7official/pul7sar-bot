"""Editorial visual study v4 with final reference-derived PUL7SAR branding.

The existing editorial renderer remains useful for scene/layout evaluation, but
its study-only font recreation of the brand is no longer allowed to survive in
the final review PNG. This wrapper renders that scene to a temporary stage,
removes the complete lower legacy-study brand zone, and then applies the
checksum-locked embedded reference-derived master as the final deterministic
brand layer.

This remains a composition study, not a publication authorization.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from engine.intelligence.brand_reference_renderer import (
    BrandReferencePlacement,
    BrandReferenceRenderer,
)
from engine.intelligence.editorial_scene_study_renderer import EditorialSceneStudyRenderer
from engine.intelligence.visual_study_handoff import VisualStudyHandoff


@dataclass(frozen=True)
class EditorialReferenceSceneStudyReceipt:
    output_path: str
    output_sha256: str
    handoff_sha256: str
    accent_hex: str
    width: int
    height: int
    base_scene_study_sha256: str
    brand_source_mode: str
    embedded_bundle_sha256: str | None
    approximate_brand_zone_removed: bool
    exact_reference_shape_used: bool
    transparent_reference_layers_used: bool
    final_brand_font_recreation_used: bool
    final_brand_generic_ecg_recreation_used: bool
    final_brand_generator_used: bool
    final_brand_network_used: bool
    generator_used_for_scene: bool = False
    verified_player_asset_used: bool = False
    subject_placeholder_used: bool = True
    arabic_raqm_used: bool = True
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-editorial-reference-scene-study-renderer-v4"


class EditorialReferenceSceneStudyRenderer:
    WIDTH = 1080
    HEIGHT = 1350
    # Covers the entire previous BrandStudyRenderer placement plus glow/shadow.
    BRAND_ERASE_BOX = (105, 1000, 975, 1315)
    BRAND_PLACEMENT = BrandReferencePlacement(x=105, y=1040, width=870)

    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @classmethod
    def _erase_approximate_brand_zone(cls, input_path: Path, output_path: Path) -> None:
        """Remove every pixel belonging to the superseded approximate brand stage."""
        from PIL import Image, ImageDraw, ImageFilter

        with Image.open(input_path) as raw:
            image = raw.convert("RGBA")

        left, top, right, bottom = cls.BRAND_ERASE_BOX
        # Build an internally feathered dark identity shelf. This is intentionally
        # non-brand geometry; the exact brand is composited afterwards.
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw.rounded_rectangle(
            (left, top, right, bottom),
            radius=44,
            fill=(2, 8, 15, 246),
            outline=(40, 58, 74, 70),
            width=2,
        )
        # A restrained vertical fade avoids a hard pasted rectangle while still
        # guaranteeing the old study logo cannot remain visible beneath it.
        glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.rounded_rectangle(
            (left + 18, top + 16, right - 18, bottom - 16),
            radius=38,
            fill=(8, 18, 29, 96),
        )
        overlay = Image.alpha_composite(overlay, glow.filter(ImageFilter.GaussianBlur(22)))
        image = Image.alpha_composite(image, overlay)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.convert("RGB").save(output_path, format="PNG")

    def render(
        self,
        handoff: VisualStudyHandoff,
        *,
        output_path: str,
        accent_hex: str,
        font_path: str,
        seed: int = 7007,
    ) -> EditorialReferenceSceneStudyReceipt:
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        stage = target.with_name(target.stem + ".approx-brand-stage.png")
        clean = target.with_name(target.stem + ".brand-cleared-stage.png")

        base_receipt = EditorialSceneStudyRenderer().render(
            handoff,
            output_path=str(stage),
            accent_hex=accent_hex,
            font_path=font_path,
            seed=seed,
        )
        self._erase_approximate_brand_zone(stage, clean)

        brand_receipt = BrandReferenceRenderer().render_on_file(
            base_path=str(clean),
            output_path=str(target),
            placement=self.BRAND_PLACEMENT,
            accent_hex=accent_hex,
        )

        stage.unlink(missing_ok=True)
        clean.unlink(missing_ok=True)
        if not target.is_file():
            raise RuntimeError("reference-branded editorial study did not create output")

        return EditorialReferenceSceneStudyReceipt(
            output_path=str(target),
            output_sha256=self._sha(target),
            handoff_sha256=handoff.payload_sha256,
            accent_hex=accent_hex.upper(),
            width=self.WIDTH,
            height=self.HEIGHT,
            base_scene_study_sha256=base_receipt.output_sha256,
            brand_source_mode=brand_receipt.brand_source_mode,
            embedded_bundle_sha256=brand_receipt.embedded_bundle_sha256,
            approximate_brand_zone_removed=True,
            exact_reference_shape_used=brand_receipt.exact_reference_shape_used,
            transparent_reference_layers_used=brand_receipt.transparent_reference_layers_used,
            final_brand_font_recreation_used=brand_receipt.font_recreation_used,
            final_brand_generic_ecg_recreation_used=brand_receipt.generic_ecg_recreation_used,
            final_brand_generator_used=brand_receipt.generator_used,
            final_brand_network_used=brand_receipt.network_used,
            generator_used_for_scene=base_receipt.generator_used,
            verified_player_asset_used=base_receipt.verified_player_asset_used,
            subject_placeholder_used=base_receipt.subject_placeholder_used,
            arabic_raqm_used=base_receipt.arabic_raqm_used,
        )
