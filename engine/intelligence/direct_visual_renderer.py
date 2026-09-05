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

        image = self._build_background(layout.profile.width, layout.profile.height, plan.accent_hex)
        draw = ImageDraw.Draw(image)
        hero = layout.box_for(LayoutRole.HERO)

        if plan.base_source is DirectBaseSource.VERIFIED_ASSET:
            if hero is None:
                raise ValueError("verified-asset render requires hero layout box")
            base_id = plan.verified_base_asset_ids[0]
            self._place_cover(image, assets[base_id].path, hero.x, hero.y, hero.width, hero.height)
            self._verified_asset_overlay(image, hero.x, hero.y, hero.width, hero.height)
        elif hero is not None:
            self._draw_programmatic_hero(draw, hero.x, hero.y, hero.width, hero.height, plan.accent_hex)

        role_boxes = [LayoutRole.LOGO, LayoutRole.CREST, LayoutRole.SOCIAL_FOOTER]
        for asset_id, role in zip(plan.exact_asset_ids, role_boxes):
            box = layout.box_for(role)
            if box is not None:
                self._place_contain(image, assets[asset_id].path, box.x, box.y, box.width, box.height)

        headline_box = layout.box_for(LayoutRole.HEADLINE)
        if headline_box is None:
            raise ValueError("headline layout box is required")
        font = self._font(font_path, max(24, round(headline_box.height * 0.30)), bold=True)
        self._draw_fitted_text_box(draw, plan.headline, headline_box.x, headline_box.y, headline_box.width, headline_box.height, font_path, font)

        if plan.score:
            score_box = layout.box_for(LayoutRole.SCORE)
            if score_box is None:
                raise ValueError("score layout box is required")
            score_font = self._font(font_path, max(24, round(score_box.height * 0.52)), bold=True)
            self._draw_fitted_text_box(draw, plan.score, score_box.x, score_box.y, score_box.width, score_box.height, font_path, score_font)

        if plan.exact_data:
            if hero is None:
                raise ValueError("exact data requires a hero/data layout box")
            self._draw_data_rows(draw, plan.exact_data, hero.x, hero.y, hero.width, hero.height, plan.accent_hex, font_path)

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
    def _build_background(width: int, height: int, accent_hex: str) -> Image.Image:
        accent = tuple(int(accent_hex[i:i+2], 16) for i in (1, 3, 5))
        image = Image.new("RGB", (width, height))
        pixels = image.load()
        for y in range(height):
            t = y / max(1, height - 1)
            for x in range(width):
                radial = max(0.0, 1.0 - (((x - width * 0.18) / width) ** 2 + ((y - height * 0.15) / height) ** 2) * 5.5)
                base = 11 + round(9 * (1.0 - t))
                pixels[x, y] = tuple(min(255, base + round(channel * radial * 0.055)) for channel in accent)
        return image

    @staticmethod
    def _draw_programmatic_hero(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, accent_hex: str) -> None:
        radius = max(14, round(min(w, h) * 0.04))
        draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=(20, 18, 18), outline=accent_hex, width=max(2, round(w * 0.004)))
        inner_left = x + round(w * 0.045)
        inner_right = x + w - round(w * 0.045)
        for index in range(1, 7):
            yy = y + round(h * index / 7)
            draw.line((inner_left, yy, inner_right, yy), fill=(65, 38, 38), width=1)
        draw.rectangle((x, y, x + round(w * 0.012), y + h), fill=accent_hex)

    @staticmethod
    def _verified_asset_overlay(image: Image.Image, x: int, y: int, w: int, h: int) -> None:
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        for row in range(h):
            alpha = round(170 * (row / max(1, h - 1)) ** 1.8)
            od.line((0, row, w, row), fill=(0, 0, 0, alpha))
        image.paste(overlay, (x, y), overlay)

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
            alpha = source.getchannel("A")
            bbox = alpha.getbbox()
            if bbox:
                source = source.crop(bbox)
            source.thumbnail((w, h), Image.Resampling.LANCZOS)
            px = x + (w - source.width) // 2
            py = y + (h - source.height) // 2
            canvas.paste(source, (px, py), source)

    @staticmethod
    def _font(font_path: Optional[str], size: int, *, bold: bool = False):
        if font_path:
            return ImageFont.truetype(font_path, size=size)
        system = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        if system.is_file():
            return ImageFont.truetype(str(system), size=size)
        return ImageFont.load_default(size=size)

    def _draw_fitted_text_box(self, draw: ImageDraw.ImageDraw, text: str, x: int, y: int, w: int, h: int, font_path: Optional[str], initial_font) -> None:
        size = getattr(initial_font, "size", max(18, round(h * 0.28)))
        while size >= 18:
            font = self._font(font_path, size, bold=True)
            lines = self._wrap(draw, text, font, w)
            line_height = round(size * 1.12)
            if lines and line_height * len(lines) <= h:
                for index, line in enumerate(lines):
                    draw.text((x, y + index * line_height), line, font=font, fill=(245, 245, 245))
                return
            size -= 2
        raise ValueError("headline cannot fit approved text box")

    def _draw_data_rows(self, draw: ImageDraw.ImageDraw, rows: tuple[str, ...], x: int, y: int, w: int, h: int, accent_hex: str, font_path: Optional[str]) -> None:
        pad_x = round(w * 0.055)
        pad_y = round(h * 0.075)
        usable_h = h - 2 * pad_y
        gap = max(10, round(h * 0.025))
        row_h = max(44, round((usable_h - gap * (len(rows) - 1)) / max(1, len(rows))))
        font = self._font(font_path, max(18, round(row_h * 0.30)), bold=True)
        index_font = self._font(font_path, max(16, round(row_h * 0.26)), bold=True)
        for idx, row in enumerate(rows):
            yy = y + pad_y + idx * (row_h + gap)
            draw.rounded_rectangle((x + pad_x, yy, x + w - pad_x, yy + row_h), radius=max(8, round(row_h * 0.18)), fill=(29, 25, 25), outline=(67, 55, 55), width=1)
            badge = max(34, round(row_h * 0.52))
            bx = x + pad_x + round(row_h * 0.18)
            by = yy + (row_h - badge) // 2
            draw.rounded_rectangle((bx, by, bx + badge, by + badge), radius=badge // 2, fill=accent_hex)
            label = f"{idx + 1:02d}"
            bb = draw.textbbox((0, 0), label, font=index_font)
            draw.text((bx + (badge - (bb[2] - bb[0])) / 2, by + (badge - (bb[3] - bb[1])) / 2 - bb[1]), label, font=index_font, fill="white")
            text = row
            if len(text) >= 3 and text[:2].isdigit() and text[2].isspace():
                text = text[3:].strip()
            tx = bx + badge + round(row_h * 0.20)
            ty = yy + (row_h - font.size) // 2 - round(font.size * 0.08)
            draw.text((tx, ty), text, font=font, fill=(235, 235, 235))

    @staticmethod
    def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = (current + " " + word).strip()
            width = draw.textbbox((0, 0), candidate, font=font)[2]
            if current and width > max_width:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        return lines
