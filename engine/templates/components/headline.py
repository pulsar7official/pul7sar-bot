from pathlib import Path
from typing import List

from engine.core.context import RenderContext
from engine.core.exceptions import TemplateError
from engine.layers.layer import Layer, LayerKind, LayerZone
from engine.templates.components.constants import (
    HEADLINE_BOTTOM, HEADLINE_LEFT, HEADLINE_MAX_LINES,
    HEADLINE_RIGHT, HEADLINE_TOP,
)
from engine.visual.text_utils import fit_headline, render_rtl_line


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


def headline_component(
    render_context: RenderContext,
    width: int,
    height: int,
    *,
    max_lines: int = HEADLINE_MAX_LINES,
    min_font_size: int = 30,
    max_font_size: int = 58,
    y_offset: int = 0,
) -> List[Layer]:
    del width, height
    content = render_context.content
    theme = render_context.theme
    if content is None:
        raise TemplateError("Headline component requires render content")
    if theme is None:
        raise TemplateError("Headline component requires a resolved theme")

    fitted = fit_headline(
        content.headline,
        str(_resolve_headline_font(render_context)),
        max_width=HEADLINE_RIGHT - HEADLINE_LEFT,
        max_height=HEADLINE_BOTTOM - HEADLINE_TOP,
        max_lines=max_lines,
        min_font_size=min_font_size,
        max_font_size=max_font_size,
    )

    line_gap = max(8, int(fitted.font_size * 0.20))
    rendered_lines = [
        render_rtl_line(line, fitted.font, color=(*theme.text_color, 255))
        for line in fitted.logical_lines
    ]
    total_h = sum(img.height for img in rendered_lines)
    total_h += line_gap * max(0, len(rendered_lines) - 1)
    y = min(HEADLINE_TOP, HEADLINE_BOTTOM - total_h) + y_offset

    layers = []
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
    return layers
