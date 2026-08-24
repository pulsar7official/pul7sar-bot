"""Deterministic PNG rendering for generator-bypass PUL7SAR visuals.

The renderer consumes DirectVisualExecutionPlan only. It never invokes an image
provider, creates a GenerationPackage, or schedules GPU work. Output bytes are
SHA-256 receipted so later publication gates can bind review to exact pixels.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from typing import Mapping, Optional

from PIL import Image, ImageDraw, ImageFont

from engine.intelligence.direct_visual_execution import DirectBaseSource, DirectVisualExecutionPlan
from engine.intelligence.layout_planner import PlannedLayout
from engine.intelligence.layout_safety import LayoutRole


@dataclass(frozen=True)
class RenderAsset:
    asset_id: str
    path: str
    sha256: str

    def __post_init__(self) -> None:
        digest = self.sha256.strip().lower()
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError("sha256 must be a 64-character hexadecimal digest")
        object.__setattr__(self, "sha256", digest)


@dataclass(frozen=True)
class DirectRenderReceipt:
    output_path: str
    sha256: str
    width: int
    height: int
    format: str
    route: str
    base_source: str
    asset_sha256: tuple[tuple[str, str], ...]
    renderer_contract: str = "pul7sar-direct-renderer-v1"


class DirectVisualRenderer:
    """Render deterministic/verified-asset plans into exact PNG bytes."""

    def render(
        self,
        plan: DirectVisualExecutionPlan,
        layout: PlannedLayout,
        *,
        output_path: str,
        assets: Mapping[str, RenderAsset] | None = None,
        font_path: Optional[str] = None,
    ) -> DirectRenderReceipt:
        if not isinstance(plan, DirectVisualExecutionPlan):
            raise TypeError("plan must be DirectVisualExecutionPlan")
        if not isinstance(layout, PlannedLayout):
            raise TypeError("layout must be PlannedLayout")
        expected_canvas = f"{layout.profile.width}x{layout.profile.height}"
        if plan.canvas != expected_canvas or plan.platform != layout.profile.platform.value:
            raise ValueError("plan/layout mismatch")

        assets = dict(assets or {})
        required = set(plan.exact_asset_ids) | set(plan.verified_base_asset_ids)
        missing = sorted(required - set(assets))
        if missing:
            raise ValueError("missing render assets: " + ", ".join(missing))
        asset_receipts = tuple(sorted(self._verify_assets(assets, required).items()))

        image = Image.new("RGB", (layout.profile.width, layout.profile.height), self._background(plan.accent_hex))
        draw = ImageDraw.Draw(image)

        hero = layout.box_for(LayoutRole.HERO)
        if plan.base_source is DirectBaseSource.VERIFIED_ASSET:
            if hero is None:
                raise ValueError("verified-asset render requires hero layout box")
            base_id = plan.verified_base_asset_ids[0]
            self._place_cover(image, assets[base_id].path, hero.x, hero.y, hero.width, hero.height)
        elif hero is not None:
            self._draw_programmatic_hero(draw, hero.x, hero.y, hero.width, hero.height, plan.accent_hex)

        # Exact assets are deliberately composited from supplied bytes only.
        role_boxes = [LayoutRole.LOGO, LayoutRole.CREST, LayoutRole.SOCIAL_FOOTER]
        for asset_id, role in zip(plan.exact_asset_ids, role_boxes):
            box = layout.box_for(role)
            if box is not None:
                self._place_contain(image, assets[asset_id].path, box.x, box.y, box.width, box.height)

        headline_box = layout.box_for(LayoutRole.HEADLINE)
        if headline_box is None:
            raise ValueError("headline layout box is required")
        font = self._font(font_path, max(18, round(headline_box.height * 0.22)))
        self._draw_text_box(draw, plan.headline, headline_box.x, headline_box.y, headline_box.width, headline_box.height, font)

        if plan.score:
            score_box = layout.box_for(LayoutRole.SCORE)
            if score_box is None:
                raise ValueError("score layout box is required")
            score_font = self._font(font_path, max(20, round(score_box.height * 0.52)))
            self._draw_text_box(draw, plan.score, score_box.x, score_box.y, score_box.width, score_box.height, score_font)

        if plan.exact_data:
            data_font = self._font(font_path, max(16, round(layout.profile.width * 0.024)))
            y = headline_box.y + headline_box.height + 12
            for row in plan.exact_data:
                draw.text((headline_box.x, y), row, font=data_font, fill="white")
                y += round(data_font.size * 1.35)

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        buffer = BytesIO()
        image.save(buffer, format="PNG", optimize=False, compress_level=9)
        payload = buffer.getvalue()
        out.write_bytes(payload)
        return DirectRenderReceipt(
            output_path=str(out),
            sha256=sha256(payload).hexdigest(),
            width=image.width,
            height=image.height,
            format="PNG",
            route=plan.route.value,
            base_source=plan.base_source.value,
            asset_sha256=asset_receipts,
        )

    @staticmethod
    def _verify_assets(assets: Mapping[str, RenderAsset], required: set[str]) -> dict[str, str]:
        receipts: dict[str, str] = {}
        for asset_id in sorted(required):
            item = assets[asset_id]
            if item.asset_id != asset_id:
                raise ValueError(f"render asset id mismatch: {asset_id}")
            payload = Path(item.path).read_bytes()
            actual = sha256(payload).hexdigest()
            if actual != item.sha256:
                raise ValueError(f"render asset checksum mismatch: {asset_id}")
            receipts[asset_id] = actual
        return receipts

    @staticmethod
    def _background(accent_hex: str) -> tuple[int, int, int]:
        accent = tuple(int(accent_hex[i:i+2], 16) for i in (1, 3, 5))
        return tuple(max(8, round(channel * 0.10)) for channel in accent)

    @staticmethod
    def _draw_programmatic_hero(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, accent_hex: str) -> None:
        draw.rounded_rectangle((x, y, x + w, y + h), radius=max(8, round(min(w, h) * 0.035)), outline=accent_hex, width=max(2, round(w * 0.006)))
        for index in range(1, 5):
            yy = y + round(h * index / 5)
            draw.line((x + round(w * 0.08), yy, x + round(w * 0.92), yy), fill=accent_hex, width=1)

    @staticmethod
    def _place_cover(canvas: Image.Image, path: str, x: int, y: int, w: int, h: int) -> None:
        with Image.open(path) as source:
            source = source.convert("RGB")
            scale = max(w / source.width, h / source.height)
            resized = source.resize((max(1, round(source.width * scale)), max(1, round(source.height * scale))), Image.Resampling.LANCZOS)
            left = max(0, (resized.width - w) // 2)
            top = max(0, (resized.height - h) // 2)
            canvas.paste(resized.crop((left, top, left + w, top + h)), (x, y))

    @staticmethod
    def _place_contain(canvas: Image.Image, path: str, x: int, y: int, w: int, h: int) -> None:
        with Image.open(path) as source:
            source = source.convert("RGBA")
            source.thumbnail((w, h), Image.Resampling.LANCZOS)
            px = x + (w - source.width) // 2
            py = y + (h - source.height) // 2
            canvas.paste(source, (px, py), source)

    @staticmethod
    def _font(font_path: Optional[str], size: int):
        if font_path:
            return ImageFont.truetype(font_path, size=size)
        return ImageFont.load_default(size=size)

    @staticmethod
    def _draw_text_box(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, w: int, h: int, font) -> None:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = (current + " " + word).strip()
            if draw.textbbox((0, 0), candidate, font=font)[2] <= w or not current:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        line_h = max(1, round(h / max(1, len(lines))))
        for index, line in enumerate(lines[: max(1, h // max(1, line_h))]):
            draw.text((x, y + index * line_h), line, font=font, fill="white")
