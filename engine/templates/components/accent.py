from engine.core.context import RenderContext
from engine.core.exceptions import TemplateError
from engine.layers.layer import Layer, LayerKind, LayerZone
from engine.templates.components.constants import ACCENT_HEIGHT

def accent_component(render_context: RenderContext, width: int, height: int) -> Layer:
    theme = render_context.theme
    if theme is None:
        raise TemplateError("Accent component requires a resolved theme")
    return Layer(
        kind=LayerKind.SHAPE, zone=LayerZone.CONTENT, z_index=2,
        properties={
            "shape_type": "rectangle", "x": 0, "y": height - ACCENT_HEIGHT,
            "width": width, "height": ACCENT_HEIGHT,
            "color": (*theme.accent_color, 255),
        },
    )
