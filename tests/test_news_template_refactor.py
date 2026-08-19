import unittest
from unittest.mock import patch
from PIL import Image
from engine.core.context import RenderContext
from engine.core.content import RenderContent
from engine.templates.implementations.news import NewsTemplate
from engine.themes.model import ResolvedTheme
from engine.layers.layer import Layer,LayerKind,LayerZone
from engine.validation.validator import ValidatedPayload
from engine.configuration.resolver import ResolvedConfiguration
from engine.assets.resolver import ResolvedAssets
from engine.fonts.resolver import ResolvedFonts

class TestNewsTemplateRefactor(unittest.TestCase):
    def _ctx(self,image=None):
        return RenderContext(
            validated_payload=ValidatedPayload(data={}),
            resolved_configuration=ResolvedConfiguration(data={"engine":{"width":1280,"height":720}}),
            resolved_assets=ResolvedAssets(data={}),
            resolved_fonts=ResolvedFonts(data={}),
            render_id="phase16",
            content=RenderContent(headline="ريال مدريد يحسم المواجهة",image=image),
            theme=ResolvedTheme(
                primary_color=(255,255,255),secondary_color=(254,190,16),
                text_color=(255,255,255),overlay_color=(11,27,58),
                overlay_opacity=0.72,accent_color=(254,190,16),
                entity_key="real_madrid",source="club",logo_treatment="contextual",
            ),
        )

    @patch("engine.templates.implementations.news.headline_component",return_value=[])
    @patch("engine.templates.implementations.news.logo_component",return_value=None)
    def test_fixed_base_order(self,_,__):
        src=Image.new("RGB",(900,600),(40,80,120))
        layers=NewsTemplate().execute(self._ctx(src))
        self.assertEqual([(x.kind,x.z_index) for x in layers],[
            (LayerKind.IMAGE,0),(LayerKind.IMAGE,1),(LayerKind.SHAPE,2)
        ])

    @patch("engine.templates.implementations.news.logo_component",return_value=None)
    @patch("engine.templates.implementations.news.headline_component")
    def test_headline_image_z4(self,mock_headline,_):
        mock_headline.return_value=[Layer(
            kind=LayerKind.IMAGE,zone=LayerZone.CONTENT,z_index=4,
            properties={"image":Image.new("RGBA",(100,30))}
        )]
        layers=NewsTemplate().execute(self._ctx())
        self.assertEqual(layers[3].kind,LayerKind.IMAGE)
        self.assertEqual(layers[3].z_index,4)

    @patch("engine.templates.implementations.news.headline_component",return_value=[])
    @patch("engine.templates.implementations.news.logo_component",return_value=None)
    def test_fallback_rgba(self,_,__):
        layers=NewsTemplate().execute(self._ctx())
        self.assertEqual(layers[0].kind,LayerKind.SHAPE)
        self.assertEqual(layers[0].properties["color"],(11,27,58,255))
        self.assertTrue(all(x is not None for x in layers))

if __name__=="__main__":
    unittest.main()
