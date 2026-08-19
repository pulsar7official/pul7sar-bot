import unittest

from engine.entities.model import EntityContext
from engine.pipeline.pipeline import Pipeline
from engine.themes.model import ResolvedTheme
from engine.validation.validator import ValidatedPayload
from engine.configuration.resolver import ResolvedConfiguration
from engine.assets.resolver import ResolvedAssets
from engine.fonts.resolver import ResolvedFonts


class Resolver:
    def resolve(self, entity):
        return ResolvedTheme(
            primary_color=(1,2,3),
            secondary_color=None,
            text_color=(255,255,255),
            overlay_color=(0,0,0),
            overlay_opacity=0.7,
            accent_color=(4,5,6),
            entity_key=entity.key if entity else None,
        )


class TestPipelineThemeAssembly(unittest.TestCase):
    def test_parse_entity_and_resolve_theme_helpers(self):
        pipeline = object.__new__(Pipeline)
        pipeline._theme_resolver = Resolver()
        payload = ValidatedPayload(
            data={
                "content": {"headline": "Test"},
                "entity": {"key": "chelsea", "kind": "club", "display_name": "Chelsea"},
            }
        )
        context = pipeline._assemble_render_context(
            validated_payload=payload,
            resolved_configuration=ResolvedConfiguration(data={}),
            resolved_assets=ResolvedAssets(data={}),
            resolved_fonts=ResolvedFonts(data={}),
        )
        self.assertIsInstance(context.entity, EntityContext)
        self.assertEqual(context.entity.key, "chelsea")
        self.assertEqual(context.theme.entity_key, "chelsea")


if __name__ == "__main__":
    unittest.main()
