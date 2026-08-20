"""Breaking-news-specific visual primitives."""

from pathlib import Path
from PIL import ImageFont

from engine.core.context import RenderContext
from engine.core.exceptions import TemplateError
from engine.layers.layer import Layer, LayerKind, LayerZone
from engine.visual.text_utils import render_rtl_line

BREAKING_BADGE_TEXT = "عاجل"
BREAKING_BADGE_FONT_SIZE = 36
BREAKING_BADGE_TOP = 340
BREAKING_BADGE_RIGHT_MARGIN = 64
BREAKING_BADGE_Z_INDEX = 5
BREAKING_EDGE_HEIGHT = 4
BREAKING_EDGE_Z_INDEX = 3

# TEMPORARY / PROVISIONAL ONLY — NOT the final PUL7SAR Signature Red.
TEMPORARY_BREAKING_COLOR = (225, 6, 0)


def _resolve_badge_font_path(render_context: RenderContext) -> Path:
    fonts = dict(render_context.resolved_fonts.data)
    path = (
        fonts.get("arabic")
        or fonts.get("headline")
        or fonts.get("bold")
        or fonts.get("fallback")
    )
    if path is None:
        raise TemplateError("Breaking badge requires a resolved Arabic/headline font")
    return Path(path)


def breaking_badge_component(
    render_context: RenderContext,
    width: int,
) -> Layer:
    font_path = _resolve_badge_font_path(render_context)
    font = ImageFont.truetype(str(font_path), BREAKING_BADGE_FONT_SIZE)
    badge_image = render_rtl_line(
        BREAKING_BADGE_TEXT,
        font,
        color=(*TEMPORARY_BREAKING_COLOR, 255),
    )
    x = max(0, width - BREAKING_BADGE_RIGHT_MARGIN - badge_image.width)
    return Layer(
        kind=LayerKind.IMAGE,
        zone=LayerZone.CONTENT,
        z_index=BREAKING_BADGE_Z_INDEX,
        properties={
            "image": badge_image,
            "x": x,
            "y": BREAKING_BADGE_TOP,
            "width": badge_image.width,
            "height": badge_image.height,
        },
    )


def breaking_edge_component(width: int) -> Layer:
    return Layer(
        kind=LayerKind.SHAPE,
        zone=LayerZone.CONTENT,
        z_index=BREAKING_EDGE_Z_INDEX,
        properties={
            "shape_type": "rectangle",
            "x": 0,
            "y": 0,
            "width": width,
            "height": BREAKING_EDGE_HEIGHT,
            "color": (*TEMPORARY_BREAKING_COLOR, 255),
        },
    )
