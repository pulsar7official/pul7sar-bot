import unittest
from unittest.mock import patch

from PIL import Image

from engine.core.context import RenderContext
from engine.core.content import RenderContent
from engine.templates.implementations.news import NewsTemplate
from engine.templates.components.overlay import overlay_component
from engine.themes.model import ResolvedTheme
from engine.layers.layer import Layer, LayerKind, LayerZone
from engine.validation.validator import ValidatedPayload
from engine.configuration.resolver import ResolvedConfiguration
from engine.assets.resolver import ResolvedAssets
from engine.fonts.resolver import ResolvedFonts


class TestNewsTemplateRefactor(unittest.TestCase):
    def _ctx(self, image=None):
        return RenderContext(
            validated_payload=ValidatedPayload(data={}),
            resolved_configuration=ResolvedConfiguration(
                data={"engine": {"width": 1280, "height": 720}}
            ),
            resolved_assets=ResolvedAssets(data={}),
            resolved_fonts=ResolvedFonts(data={}),
            render_id="phase17-regression",
            content=RenderContent(
                headline="ريال مدريد يحسم المواجهة",
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

    @patch(
        "engine.templates.implementations.news.headline_component",
        return_value=[],
    )
    @patch(
        "engine.templates.implementations.news.logo_component",
        return_value=None,
    )
    def test_fixed_base_order(self, _, __):
        source = Image.new("RGB", (900, 600), (40, 80, 120))
        layers = NewsTemplate().execute(self._ctx(source))
        self.assertEqual(
            [(layer.kind, layer.z_index) for layer in layers],
            [
                (LayerKind.IMAGE, 0),
                (LayerKind.IMAGE, 1),
                (LayerKind.SHAPE, 2),
            ],
        )

    @patch(
        "engine.templates.implementations.news.logo_component",
        return_value=None,
    )
    @patch("engine.templates.implementations.news.headline_component")
    def test_headline_image_z4(self, mock_headline, _):
        mock_headline.return_value = [
            Layer(
                kind=LayerKind.IMAGE,
                zone=LayerZone.CONTENT,
                z_index=4,
                properties={"image": Image.new("RGBA", (100, 30))},
            )
        ]
        layers = NewsTemplate().execute(self._ctx())
        self.assertEqual(layers[3].kind, LayerKind.IMAGE)
        self.assertEqual(layers[3].z_index, 4)

    @patch(
        "engine.templates.implementations.news.headline_component",
        return_value=[],
    )
    @patch(
        "engine.templates.implementations.news.logo_component",
        return_value=None,
    )
    def test_fallback_rgba(self, _, __):
        layers = NewsTemplate().execute(self._ctx())
        self.assertEqual(layers[0].kind, LayerKind.SHAPE)
        self.assertEqual(layers[0].properties["color"], (11, 27, 58, 255))
        self.assertTrue(all(layer is not None for layer in layers))

    def test_overlay_default_uses_theme_opacity(self):
        context = self._ctx()
        layer = overlay_component(context, 1280, 720)
        image = layer.properties["image"]
        expected = int(255 * context.theme.overlay_opacity)
        alpha = image.getpixel((640, 719))[3]
        self.assertGreaterEqual(alpha, expected - 2)
        self.assertLessEqual(alpha, expected)

    def test_breaking_override_can_be_stronger_than_normal(self):
        context = self._ctx()
        normal = overlay_component(context, 1280, 720)
        stronger = overlay_component(
            context,
            1280,
            720,
            start_ratio=0.30,
            max_opacity=0.82,
        )
        normal_alpha = normal.properties["image"].getpixel((640, 719))[3]
        stronger_alpha = stronger.properties["image"].getpixel((640, 719))[3]
        self.assertGreater(stronger_alpha, normal_alpha)


if __name__ == "__main__":
    unittest.main()
