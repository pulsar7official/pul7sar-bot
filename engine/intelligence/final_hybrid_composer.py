"""Receipt-backed deterministic final compositor for PUL7SAR Phase 18.

This coordinator owns the exact post-generation stack. It composes deterministic
sport geometry, approved dynamic PUL7SAR branding and deterministic typography in
sequence. Each stage writes a new artifact and receipt; no stage may silently
claim completion.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Optional

from engine.intelligence.dynamic_brand import DynamicBrandDecision
from engine.intelligence.dynamic_brand_geometry import DynamicBrandGeometryRecipe
from engine.intelligence.dynamic_brand_renderer import DynamicBrandCompositionReceipt, DynamicBrandPlacement, PillowDynamicBrandRenderer
from engine.intelligence.football_hybrid_composer import FootballHybridComposer, FootballHybridCompositionReceipt
from engine.intelligence.football_pitch_placement import FootballCameraPreset
from engine.intelligence.typography import FontReference, TextLayout
from engine.intelligence.typography_renderer import PillowTypographyRenderer, TypographyCompositionReceipt


@dataclass(frozen=True)
class TypographyRenderJob:
    layout: TextLayout
    font: FontReference
    font_path: str
    fill_rgba: tuple[int, int, int, int] = (255, 255, 255, 255)


@dataclass(frozen=True)
class FinalHybridCompositionReceipt:
    status: str
    base_path: str
    output_path: str
    football_receipt: Optional[FootballHybridCompositionReceipt]
    brand_receipt: DynamicBrandCompositionReceipt
    typography_receipts: tuple[TypographyCompositionReceipt, ...]
    output_sha256: str
    deterministic_geometry_applied: bool
    exact_dynamic_brand_applied: bool
    exact_typography_applied: bool


class FinalHybridComposer:
    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def compose(
        self,
        *,
        base_path: str,
        output_path: str,
        work_dir: str,
        brand_recipe: DynamicBrandGeometryRecipe,
        brand_decision: DynamicBrandDecision,
        brand_font: FontReference,
        brand_font_path: str,
        brand_placement: DynamicBrandPlacement,
        typography_jobs: tuple[TypographyRenderJob, ...] = (),
        apply_football_geometry: bool = False,
        football_camera: FootballCameraPreset = FootballCameraPreset.HIGH_WIDE_CENTRAL,
    ) -> FinalHybridCompositionReceipt:
        source = Path(base_path)
        if not source.is_file():
            raise FileNotFoundError(base_path)
        work = Path(work_dir)
        work.mkdir(parents=True, exist_ok=True)
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        current = source
        football_receipt = None
        if apply_football_geometry:
            football_out = work / "01-football-geometry.png"
            football_receipt = FootballHybridComposer().compose_file(
                base_path=str(current),
                output_path=str(football_out),
                camera_preset=football_camera,
            )
            if not football_receipt.deterministic_geometry_applied or football_receipt.surface_opacity != 255:
                raise RuntimeError("football deterministic geometry receipt is incomplete")
            current = football_out

        brand_out = work / "02-dynamic-brand.png"
        brand_receipt = PillowDynamicBrandRenderer().render_on_file(
            base_path=str(current),
            output_path=str(brand_out),
            recipe=brand_recipe,
            decision=brand_decision,
            font=brand_font,
            font_path=brand_font_path,
            placement=brand_placement,
        )
        if not (brand_receipt.seven_accent_applied and brand_receipt.pulse_accent_applied):
            raise RuntimeError("dynamic brand receipt is incomplete")
        current = brand_out

        typography_receipts: list[TypographyCompositionReceipt] = []
        roles: set[str] = set()
        for index, job in enumerate(typography_jobs, 1):
            role = job.layout.role.value
            if role in roles:
                raise ValueError(f"duplicate deterministic typography role: {role}")
            roles.add(role)
            text_out = work / f"{index + 2:02d}-typography-{role}.png"
            receipt = PillowTypographyRenderer().render_on_file(
                base_path=str(current),
                output_path=str(text_out),
                layout=job.layout,
                font=job.font,
                font_path=job.font_path,
                fill_rgba=job.fill_rgba,
            )
            typography_receipts.append(receipt)
            current = text_out

        # Copy through Pillow so output encoding is deterministic PNG rather than
        # relying on filesystem rename semantics across Colab mount boundaries.
        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("Pillow is required for final hybrid composition") from exc
        with Image.open(current) as image:
            image.convert("RGBA").save(target, format="PNG")

        return FinalHybridCompositionReceipt(
            status="FINAL_HYBRID_COMPOSED",
            base_path=str(source),
            output_path=str(target),
            football_receipt=football_receipt,
            brand_receipt=brand_receipt,
            typography_receipts=tuple(typography_receipts),
            output_sha256=self._sha256(target),
            deterministic_geometry_applied=bool(football_receipt and football_receipt.deterministic_geometry_applied) if apply_football_geometry else True,
            exact_dynamic_brand_applied=True,
            exact_typography_applied=bool(typography_receipts) if typography_jobs else True,
        )
