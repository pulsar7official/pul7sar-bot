from typing import Sequence
from engine.core.context import RenderContext
from engine.core.exceptions import TemplateError
from engine.layers.layer import Layer
from engine.templates.base import BaseTemplate
from engine.templates.components import (
    accent_component, background_component, headline_component,
    logo_component, overlay_component,
)

class NewsTemplate(BaseTemplate):
    def execute(self, render_context: RenderContext) -> Sequence[Layer]:
        try:
            if render_context.content is None:
                raise TemplateError("NewsTemplate requires render content")
            if render_context.theme is None:
                raise TemplateError("NewsTemplate requires a resolved theme")

            width, height = self._get_dimensions(render_context)
            layers = [
                background_component(render_context, width, height),
                overlay_component(render_context, width, height),
                accent_component(render_context, width, height),
            ]
            layers.extend(headline_component(render_context, width, height))

            logo_layer = logo_component(render_context, width, height)
            if logo_layer is not None:
                layers.append(logo_layer)
            return layers
        except TemplateError:
            raise
        except Exception as exc:
            raise TemplateError(f"NewsTemplate execution failed: {exc}") from exc

    @staticmethod
    def _get_dimensions(render_context: RenderContext) -> tuple[int, int]:
        canvas = dict(render_context.canvas_information)
        if canvas.get("width") and canvas.get("height"):
            return int(canvas["width"]), int(canvas["height"])
        config = dict(render_context.resolved_configuration.data)
        engine = config.get("engine", {})
        return int(engine.get("width", 1280)), int(engine.get("height", 720))
