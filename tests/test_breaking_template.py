import unittest
from unittest.mock import patch

from PIL import Image

from engine.core.content import RenderContent
from engine.core.context import RenderContext
from engine.templates.base import BaseTemplate
from engine.templates.implementations.breaking import BreakingNewsTemplate
from engine.templates.implementations.news import NewsTemplate
from engine.templates.components.breaking import (
    TEMPORARY_BREAKING_COLOR,
    breaking_edge_component,
)
from engine.themes.model import ResolvedTheme
from engine.layers.layer import Layer, LayerKind, LayerZone
from engine.validation.validator import ValidatedPayload
from engine.configuration.resolver import ResolvedConfiguration
from engine.assets.resolver import ResolvedAssets
from engine.fonts.resolver import ResolvedFonts


class TestBreakingTemplate(unittest.TestCase):
    def _context(self, image=None):
        return RenderContext(
            validated_payload=ValidatedPayload(data={}),
            resolved_configuration=ResolvedConfiguration(
                data={"engine": {"width": 1280, "height": 720}}
            ),
            resolved_assets=ResolvedAssets(data={}),
            resolved_fonts=ResolvedFonts(data={}),
            render_id="phase17",
            content=RenderContent(
                headline="ريال مدريد يحسم صفقة جديدة في الساعات الأخيرة",
                image=image,
            ),
            theme=ResolvedTheme(
                primary_color=(255, 255, 255),
                secondary_color=(254, 190, 16),
                text_color=(255, 255, 255),
                overlay_color=(11, 27, 58),
                overlay_opacity=0.72,
                accent_color=(254, 190, 16),
                entity_key="real_madrid",
                source="club",
                logo_treatment="contextual",
            ),
        )

    def test_inherits_base_directly_not_news(self):
        self.assertTrue(issubclass(BreakingNewsTemplate, BaseTemplate))
        self.assertFalse(issubclass(BreakingNewsTemplate, NewsTemplate))

    def test_breaking_edge_contract(self):
        layer = breaking_edge_component(1280)
        self.assertEqual(layer.kind, LayerKind.SHAPE)
        self.assertEqual(layer.z_index, 3)
        self.assertEqual(layer.properties["width"], 1280)
        self.assertEqual(layer.properties["height"], 4)
        self.assertEqual(
            layer.properties["color"],
            (*TEMPORARY_BREAKING_COLOR, 255),
        )

    @patch(
        "engine.templates.implementations.breaking.breaking_badge_component"
    )
    @patch(
        "engine.templates.implementations.breaking.headline_component",
        return_value=[],
    )
    @patch(
        "engine.templates.implementations.breaking.logo_component",
        return_value=None,
    )
    def test_breaking_layer_order_without_logo(
        self, _logo, _headline, badge
    ):
        badge.return_value = Layer(
            kind=LayerKind.IMAGE,
            zone=LayerZone.CONTENT,
            z_index=5,
            properties={"image": Image.new("RGBA", (50, 30))},
        )
        source = Image.new("RGB", (900, 600), (40, 80, 120))
        layers = BreakingNewsTemplate().execute(self._context(source))
        self.assertEqual(
            [(layer.kind, layer.z_index) for layer in layers],
            [
                (LayerKind.IMAGE, 0),
                (LayerKind.IMAGE, 1),
                (LayerKind.SHAPE, 2),
                (LayerKind.SHAPE, 3),
                (LayerKind.IMAGE, 5),
            ],
        )
        self.assertTrue(all(layer is not None for layer in layers))

    @patch(
        "engine.templates.implementations.breaking.breaking_badge_component"
    )
    @patch(
        "engine.templates.implementations.breaking.headline_component",
        return_value=[],
    )
    @patch(
        "engine.templates.implementations.breaking.logo_component",
        return_value=None,
    )
    def test_source_image_not_mutated(self, _logo, _headline, badge):
        badge.return_value = Layer(
            kind=LayerKind.IMAGE,
            zone=LayerZone.CONTENT,
            z_index=5,
            properties={"image": Image.new("RGBA", (50, 30))},
        )
        source = Image.new("RGB", (900, 600), (40, 80, 120))
        before = source.tobytes()
        BreakingNewsTemplate().execute(self._context(source))
        self.assertEqual(source.tobytes(), before)

    def test_breaking_color_is_provisional_constant(self):
        self.assertEqual(TEMPORARY_BREAKING_COLOR, (225, 6, 0))


if __name__ == "__main__":
    unittest.main()
