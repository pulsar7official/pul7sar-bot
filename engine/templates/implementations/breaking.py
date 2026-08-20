"""BreakingNewsTemplate — first specialized PUL7SAR editorial template."""

from typing import Sequence

from engine.core.context import RenderContext
from engine.core.exceptions import TemplateError
from engine.layers.layer import Layer
from engine.templates.base import BaseTemplate
from engine.templates.components.accent import accent_component
from engine.templates.components.background import background_component
from engine.templates.components.breaking import (
    breaking_badge_component,
    breaking_edge_component,
)
from engine.templates.components.headline import headline_component
from engine.templates.components.logo import logo_component
from engine.templates.components.overlay import overlay_component


class BreakingNewsTemplate(BaseTemplate):
    def execute(self, render_context: RenderContext) -> Sequence[Layer]:
        try:
            if render_context.content is None:
                raise TemplateError("BreakingNewsTemplate requires render content")
            if render_context.theme is None:
                raise TemplateError("BreakingNewsTemplate requires a resolved theme")

            width, height = self._get_dimensions(render_context)

            layers = [
                background_component(render_context, width, height),
                overlay_component(
                    render_context,
                    width,
                    height,
                    start_ratio=0.30,
                    max_opacity=0.82,
                ),
                accent_component(render_context, width, height),
                breaking_edge_component(width),
            ]

            layers.extend(
                headline_component(
                    render_context,
                    width,
                    height,
                    max_lines=2,
                    min_font_size=32,
                    max_font_size=62,
                    y_offset=-40,
                )
            )

            layers.append(breaking_badge_component(render_context, width))

            logo_layer = logo_component(render_context, width, height)
            if logo_layer is not None:
                layers.append(logo_layer)

            return layers

        except TemplateError:
            raise
        except Exception as exc:
            raise TemplateError(
                f"BreakingNewsTemplate execution failed: {exc}"
            ) from exc

    @staticmethod
    def _get_dimensions(render_context: RenderContext) -> tuple[int, int]:
        canvas = dict(render_context.canvas_information)
        if canvas.get("width") and canvas.get("height"):
            return int(canvas["width"]), int(canvas["height"])

        config = dict(render_context.resolved_configuration.data)
        engine = config.get("engine", {})
        return int(engine.get("width", 1280)), int(engine.get("height", 720))
