from PIL import Image, ImageDraw
from engine.core.context import RenderContext
from engine.core.exceptions import TemplateError
from engine.layers.layer import Layer, LayerKind, LayerZone
from engine.templates.components.constants import GRADIENT_START_RATIO

def overlay_component(render_context: RenderContext, width: int, height: int) -> Layer:
    theme = render_context.theme
    if theme is None:
        raise TemplateError("Overlay component requires a resolved theme")
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    start_y = int(height * GRADIENT_START_RATIO)
    span = max(1, height - start_y)
    max_alpha = int(255 * theme.overlay_opacity)
    for y in range(start_y, height):
        t = (y - start_y) / span
        smooth = t * t * (3.0 - 2.0 * t)
        alpha = int(max_alpha * smooth)
        draw.line((0, y, width, y), fill=(*theme.overlay_color, alpha))
    return Layer(
        kind=LayerKind.IMAGE, zone=LayerZone.CONTENT, z_index=1,
        properties={"image": overlay, "x": 0, "y": 0, "width": width, "height": height},
    )
