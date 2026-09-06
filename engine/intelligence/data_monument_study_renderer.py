"""Premium deterministic Data Monument renderer for PUL7SAR Phase 18.

Exact values remain code-owned. The renderer deliberately avoids spreadsheet-like
visual density: one dominant fact/leader, a short supporting ranking, restrained
context and the adaptive PUL7SAR signature. No stadium, generated number or
network dependency is required.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.data_monument_composition import DataMonumentComposition
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.premium_editorial_surface import EditorialSurfaceStyle, PremiumEditorialSurface


@dataclass(frozen=True)
class DataMonumentRow:
    rank: int
    label: str
    value: str
    emphasized: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.rank, int) or isinstance(self.rank, bool) or self.rank <= 0:
            raise ValueError("rank must be a positive integer")
        if not self.label.strip() or not self.value.strip():
            raise ValueError("label and value are required")


@dataclass(frozen=True)
class DataMonumentStudyReceipt:
    output_path: str
    output_sha256: str
    width: int
    height: int
    row_count: int
    dominant_value: str
    exact_values_code_owned: bool
    spreadsheet_grid_used: bool
    stadium_used: bool
    brand_zone: str
    brand_width: int
    brand_height: int
    atmosphere_contract: str
    generator_used: bool = False
    network_used: bool = False
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-data-monument-study-renderer-v1-premium"


class DataMonumentStudyRenderer:
    MAX_ROWS = 5

    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _rgb(value: str) -> tuple[int, int, int]:
        text = value.strip().upper()
        if len(text) != 7 or not text.startswith("#"):
            raise ValueError("accent must be #RRGGBB")
        return tuple(int(text[i:i + 2], 16) for i in (1, 3, 5))

    @staticmethod
    def _box(box, profile: PlatformImageProfile) -> tuple[int, int, int, int]:
        return (
            round(box.x * profile.width),
            round(box.y * profile.height),
            round((box.x + box.width) * profile.width),
            round((box.y + box.height) * profile.height),
        )

    @staticmethod
    def _fit_font(draw: ImageDraw.ImageDraw, text: str, font_path: str, max_width: int, max_height: int, start: int) -> ImageFont.FreeTypeFont:
        size = max(12, start)
        while size >= 12:
            font = ImageFont.truetype(font_path, size=size)
            b = draw.textbbox((0, 0), text, font=font)
            if b[2] - b[0] <= max_width and b[3] - b[1] <= max_height:
                return font
            size -= 2
        return ImageFont.truetype(font_path, size=12)

    def render(
        self,
        composition: DataMonumentComposition,
        *,
        profile: PlatformImageProfile,
        output_path: str,
        headline: str,
        context: str,
        rows: tuple[DataMonumentRow, ...],
        accent_hex: str,
        font_path: str,
        seed_key: str = "data-monument",
    ) -> DataMonumentStudyReceipt:
        if not isinstance(composition, DataMonumentComposition):
            raise TypeError("composition must be DataMonumentComposition")
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        if not headline.strip() or not context.strip():
            raise ValueError("headline and context are required")
        if not 1 <= len(rows) <= self.MAX_ROWS:
            raise ValueError(f"rows must contain 1..{self.MAX_ROWS} entries")
        if len({row.rank for row in rows}) != len(rows):
            raise ValueError("row ranks must be unique")
        if not Path(font_path).is_file():
            raise FileNotFoundError(font_path)

        accent = self._rgb(accent_hex)
        surface = PremiumEditorialSurface()
        canvas = surface.render(
            size=(profile.width, profile.height),
            style=EditorialSurfaceStyle(
                base_top=(8, 15, 27),
                base_bottom=(2, 6, 12),
                accent=accent,
                secondary_accent=(53, 105, 145),
                glow_strength=88,
                grain_strength=11,
                vignette_strength=110,
            ),
            seed_key=seed_key,
        )
        draw = ImageDraw.Draw(canvas, "RGBA")

        hx0, hy0, hx1, hy1 = self._box(composition.headline_box, profile)
        headline_font = self._fit_font(draw, headline, font_path, hx1 - hx0, hy1 - hy0, round((hy1 - hy0) * 0.58))
        draw.text((hx0, hy0), headline, font=headline_font, fill=(241, 246, 249, 255))
        draw.rounded_rectangle((hx0, hy1 + 8, hx0 + round((hx1 - hx0) * 0.17), hy1 + 13), radius=2, fill=(*accent, 230))

        dx0, dy0, dx1, dy1 = self._box(composition.data_box, profile)
        PremiumEditorialSurface.glass_panel(canvas, (dx0, dy0, dx1, dy1), radius=max(20, round(profile.width * 0.024)), opacity=58, border_alpha=32)
        draw = ImageDraw.Draw(canvas, "RGBA")

        # Dominant value becomes the visual monument; remaining rows are support,
        # not a spreadsheet. The first row is always dominant by rank order.
        ordered = tuple(sorted(rows, key=lambda row: row.rank))
        leader = ordered[0]
        leader_value_font = self._fit_font(draw, leader.value, font_path, round((dx1 - dx0) * 0.34), round((dy1 - dy0) * 0.25), round((dy1 - dy0) * 0.23))
        leader_label_font = self._fit_font(draw, leader.label, font_path, round((dx1 - dx0) * 0.46), round((dy1 - dy0) * 0.10), round((dy1 - dy0) * 0.075))
        rank_font = ImageFont.truetype(font_path, size=max(14, round((dy1 - dy0) * 0.055)))

        left = dx0 + round((dx1 - dx0) * 0.07)
        top = dy0 + round((dy1 - dy0) * 0.10)
        draw.text((left, top), f"#{leader.rank}", font=rank_font, fill=(*accent, 235))
        draw.text((left, top + round((dy1 - dy0) * 0.09)), leader.label, font=leader_label_font, fill=(232, 239, 244, 255))
        draw.text((left, top + round((dy1 - dy0) * 0.20)), leader.value, font=leader_value_font, fill=(248, 251, 252, 255))

        # Thin vertical accent blade creates depth without boxing the leader.
        blade_x = dx0 + round((dx1 - dx0) * 0.035)
        draw.rounded_rectangle((blade_x, top, blade_x + 5, top + round((dy1 - dy0) * 0.29)), radius=2, fill=(*accent, 220))

        support = ordered[1:]
        if support:
            row_area_top = dy0 + round((dy1 - dy0) * 0.53)
            row_area_bottom = dy1 - round((dy1 - dy0) * 0.08)
            slot_h = max(1, (row_area_bottom - row_area_top) // len(support))
            label_font = ImageFont.truetype(font_path, size=max(16, round(slot_h * 0.30)))
            value_font = ImageFont.truetype(font_path, size=max(17, round(slot_h * 0.34)))
            for index, row in enumerate(support):
                y = row_area_top + index * slot_h
                if index:
                    draw.line((left, y, dx1 - round((dx1 - dx0) * 0.07), y), fill=(255, 255, 255, 18), width=1)
                draw.text((left, y + round(slot_h * 0.28)), f"{row.rank:02d}", font=label_font, fill=(151, 170, 187, 220))
                label_x = left + round((dx1 - dx0) * 0.10)
                draw.text((label_x, y + round(slot_h * 0.25)), row.label, font=label_font, fill=(220, 229, 236, 245))
                vb = draw.textbbox((0, 0), row.value, font=value_font)
                draw.text((dx1 - round((dx1 - dx0) * 0.07) - (vb[2] - vb[0]), y + round(slot_h * 0.23)), row.value, font=value_font, fill=(239, 244, 247, 255))

        cx0, cy0, cx1, cy1 = self._box(composition.context_box, profile)
        context_font = self._fit_font(draw, context, font_path, cx1 - cx0, cy1 - cy0, round((cy1 - cy0) * 0.46))
        draw.text((cx0, cy0), context, font=context_font, fill=(161, 178, 191, 235))

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        prebrand = target.with_name(target.stem + ".prebrand.png")
        canvas.convert("RGB").save(prebrand, format="PNG")
        brand = AdaptiveBrandOverlayRenderer().render_on_file(
            base_path=str(prebrand),
            output_path=str(target),
            adaptive=composition.brand,
            profile=profile,
            accent_hex=accent_hex,
        )
        prebrand.unlink(missing_ok=True)

        return DataMonumentStudyReceipt(
            output_path=str(target),
            output_sha256=self._sha(target),
            width=profile.width,
            height=profile.height,
            row_count=len(rows),
            dominant_value=leader.value,
            exact_values_code_owned=True,
            spreadsheet_grid_used=False,
            stadium_used=False,
            brand_zone=brand.zone,
            brand_width=brand.width,
            brand_height=brand.height,
            atmosphere_contract=PremiumEditorialSurface.CONTRACT,
        )
