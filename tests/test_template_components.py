import unittest
from unittest.mock import patch
from PIL import Image
from engine.core.context import RenderContext
from engine.core.content import RenderContent
from engine.entities.model import EntityContext
from engine.themes.model import ResolvedTheme
from engine.templates.components.background import background_component
from engine.templates.components.overlay import overlay_component
from engine.templates.components.accent import accent_component
from engine.templates.components.logo import logo_component
from engine.layers.layer import LayerKind
from engine.validation.validator import ValidatedPayload
from engine.configuration.resolver import ResolvedConfiguration
from engine.assets.resolver import ResolvedAssets
from engine.fonts.resolver import ResolvedFonts

def context(image=None):
    return RenderContext(
        validated_payload=ValidatedPayload(data={}),
        resolved_configuration=ResolvedConfiguration(data={"engine":{"width":1280,"height":720}}),
        resolved_assets=ResolvedAssets(data={}),
        resolved_fonts=ResolvedFonts(data={}),
        render_id="test",
        content=RenderContent(headline="خبر رياضي",image=image),
        entity=EntityContext(key="chelsea",kind="club",display_name="Chelsea"),
        theme=ResolvedTheme(
            primary_color=(3,70,148),secondary_color=(219,161,17),
            text_color=(255,255,255),overlay_color=(7,26,61),
            overlay_opacity=0.72,accent_color=(3,70,148),
            entity_key="chelsea",source="club",logo_treatment="contextual",
        ),
    )

class TestTemplateComponents(unittest.TestCase):
    def test_background_image(self):
        src=Image.new("RGB",(900,600),(50,100,150))
        before=src.tobytes()
        layer=background_component(context(src),1280,720)
        self.assertEqual(layer.kind,LayerKind.IMAGE)
        self.assertEqual(layer.z_index,0)
        self.assertEqual(src.tobytes(),before)

    def test_background_fallback_rgba(self):
        ctx=context()
        layer=background_component(ctx,1280,720)
        self.assertEqual(layer.kind,LayerKind.SHAPE)
        self.assertEqual(layer.properties["color"],(*ctx.theme.overlay_color,255))

    def test_overlay(self):
        layer=overlay_component(context(),1280,720)
        self.assertEqual(layer.kind,LayerKind.IMAGE)
        self.assertEqual(layer.z_index,1)
        img=layer.properties["image"]
        self.assertEqual(img.mode,"RGBA")
        self.assertEqual(img.getpixel((640,0))[3],0)
        self.assertGreater(img.getpixel((640,719))[3],0)

    def test_accent(self):
        ctx=context()
        layer=accent_component(ctx,1280,720)
        self.assertEqual(layer.kind,LayerKind.SHAPE)
        self.assertEqual(layer.z_index,2)
        self.assertEqual(layer.properties["y"],708)
        self.assertEqual(layer.properties["height"],12)

    @patch("engine.templates.components.logo._load_master_logo",return_value=None)
    def test_logo_missing_returns_none(self,_):
        self.assertIsNone(logo_component(context(),1280,720))

if __name__=="__main__":
    unittest.main()
