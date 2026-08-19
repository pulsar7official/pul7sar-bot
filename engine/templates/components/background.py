from engine.core.context import RenderContext
from engine.core.exceptions import TemplateError
from engine.layers.layer import Layer, LayerKind, LayerZone
from engine.visual.image_utils import cover_image

def background_component(render_context: RenderContext, width: int, height: int) -> Layer:
    content = render_context.content
    theme = render_context.theme
    if content is None:
        raise TemplateError("Background component requires render content")
    if theme is None:
        raise TemplateError("Background component requires a resolved theme")
    if content.image is not None:
        covered = cover_image(content.image, width, height)
        return Layer(
            kind=LayerKind.IMAGE, zone=LayerZone.BACKGROUND, z_index=0,
            properties={"image": covered, "x": 0, "y": 0, "width": width, "height": height},
        )
    return Layer(
        kind=LayerKind.SHAPE, zone=LayerZone.BACKGROUND, z_index=0,
        properties={
            "shape_type": "rectangle", "x": 0, "y": 0,
            "width": width, "height": height,
            "color": (*theme.overlay_color, 255),
        },
    )
