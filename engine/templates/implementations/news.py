"""First real PUL7SAR news-card template."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

from PIL import Image

from engine.core.context import RenderContext
from engine.core.exceptions import TemplateError
from engine.layers.layer import Layer, LayerKind, LayerZone
from engine.templates.base import BaseTemplate
from engine.visual.image_utils import cover_image
from engine.visual.text_utils import fit_headline, render_rtl_line


HEADLINE_LEFT = 64
HEADLINE_RIGHT = 1216
HEADLINE_TOP = 430
HEADLINE_BOTTOM = 660
HEADLINE_MAX_LINES = 3

LOGO_X = 58
LOGO_Y = 48
LOGO_MAX_WIDTH = 180


class NewsTemplate(BaseTemplate):
    """Full-bleed news image + readability overlay + Arabic headline + logo."""

    def execute(self, render_context: RenderContext) -> Sequence[Layer]:
        try:
            content = render_context.content
            if content is None:
                raise TemplateError("NewsTemplate requires render content")

            width, height = self._get_dimensions(render_context)
            layers: list[Layer] = []

            if content.image is not None:
                covered = cover_image(content.image, width, height)
                layers.append(
                    Layer(
                        kind=LayerKind.IMAGE,
                        zone=LayerZone.BACKGROUND,
                        z_index=0,
                        properties={
                            "image": covered,
                            "x": 0,
                            "y": 0,
                            "width": width,
                            "height": height,
                        },
                    )
                )
            else:
                layers.append(
                    Layer(
                        kind=LayerKind.SHAPE,
                        zone=LayerZone.BACKGROUND,
                        z_index=0,
                        properties={
                            "shape_type": "rectangle",
                            "x": 0,
                            "y": 0,
                            "width": width,
                            "height": height,
                            "color": (13, 20, 34, 255),
                        },
                    )
                )

            # Uniform overlay: intentionally simple for first viable template.
            layers.append(
                Layer(
                    kind=LayerKind.OVERLAY,
                    zone=LayerZone.CONTENT,
                    z_index=1,
                    properties={
                        "overlay_type": "color_overlay",
                        "x": 0,
                        "y": 0,
                        "width": width,
                        "height": height,
                        "color": (0, 0, 0, 150),
                        "opacity": 1.0,
                    },
                )
            )

            # Minimal brand accent.
            layers.append(
                Layer(
                    kind=LayerKind.SHAPE,
                    zone=LayerZone.CONTENT,
                    z_index=2,
                    properties={
                        "shape_type": "rectangle",
                        "x": 0,
                        "y": height - 18,
                        "width": width,
                        "height": 18,
                        "color": (0, 112, 255, 230),
                    },
                )
            )

            font_path = self._resolve_headline_font(render_context)
            fitted = fit_headline(
                content.headline,
                str(font_path),
                max_width=HEADLINE_RIGHT - HEADLINE_LEFT,
                max_height=HEADLINE_BOTTOM - HEADLINE_TOP,
                max_lines=HEADLINE_MAX_LINES,
                min_font_size=30,
                max_font_size=58,
            )

            line_gap = max(8, int(fitted.font_size * 0.20))
            rendered_lines = [
                render_rtl_line(line, fitted.font)
                for line in fitted.logical_lines
            ]
            total_h = sum(img.height for img in rendered_lines)
            total_h += line_gap * max(0, len(rendered_lines) - 1)
            y = min(HEADLINE_TOP, HEADLINE_BOTTOM - total_h)

            for line_image in rendered_lines:
                x = HEADLINE_RIGHT - line_image.width
                layers.append(
                    Layer(
                        kind=LayerKind.IMAGE,
                        zone=LayerZone.CONTENT,
                        z_index=4,
                        properties={
                            "image": line_image,
                            "x": max(HEADLINE_LEFT, x),
                            "y": y,
                            "width": line_image.width,
                            "height": line_image.height,
                        },
                    )
                )
                y += line_image.height + line_gap

            logo = self._load_logo()
            if logo is not None:
                logo = logo.copy()
                ratio = min(1.0, LOGO_MAX_WIDTH / max(1, logo.width))
                target_w = max(1, int(logo.width * ratio))
                target_h = max(1, int(logo.height * ratio))
                layers.append(
                    Layer(
                        kind=LayerKind.IMAGE,
                        zone=LayerZone.BRAND,
                        z_index=10,
                        properties={
                            "image": logo,
                            "x": LOGO_X,
                            "y": LOGO_Y,
                            "width": target_w,
                            "height": target_h,
                        },
                    )
                )

            return layers

        except TemplateError:
            raise
        except Exception as exc:
            raise TemplateError(
                f"NewsTemplate execution failed: {exc}"
            ) from exc

    @staticmethod
    def _get_dimensions(render_context: RenderContext) -> tuple[int, int]:
        canvas = dict(render_context.canvas_information)
        if canvas.get("width") and canvas.get("height"):
            return int(canvas["width"]), int(canvas["height"])

        config = dict(render_context.resolved_configuration.data)
        engine = config.get("engine", {})
        return int(engine.get("width", 1280)), int(engine.get("height", 720))

    @staticmethod
    def _resolve_headline_font(render_context: RenderContext) -> Path:
        fonts = dict(render_context.resolved_fonts.data)
        path = (
            fonts.get("arabic")
            or fonts.get("headline")
            or fonts.get("bold")
            or fonts.get("fallback")
        )
        if path is None:
            raise TemplateError("No usable headline font was resolved")
        return Path(path)

    @staticmethod
    def _load_logo() -> Optional[Image.Image]:
        # news.py -> implementations -> templates -> engine -> repo root
        repo_root = Path(__file__).resolve().parents[3]
        logo_path = repo_root / "logo.png"
        if not logo_path.is_file():
            return None
        try:
            with Image.open(logo_path) as image:
                return image.convert("RGBA").copy()
        except Exception:
            return None
