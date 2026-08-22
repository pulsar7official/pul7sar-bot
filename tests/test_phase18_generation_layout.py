import unittest

from engine.intelligence.assets import AssetBundle, AssetReference, AssetRole, AssetTreatment
from engine.intelligence.generation_package import GenerationPackageCompiler
from engine.intelligence.layout_planner import DeterministicLayoutPlanner, LayoutRequirements
from engine.intelligence.models import Sentiment, VisualIntent
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.scene_spec import OriginalSceneSpecification


class GenerationLayoutPackageTests(unittest.TestCase):
    def setUp(self):
        self.registry = PlatformProfileRegistry()
        self.layout_planner = DeterministicLayoutPlanner()
        self.compiler = GenerationPackageCompiler()
        self.assets = AssetBundle((
            AssetReference("pul7sar-wordmark", AssetRole.BRAND_WORDMARK, AssetTreatment.EXACT),
            AssetReference("pul7sar-pulse", AssetRole.BRAND_ACCENT, AssetTreatment.TINTABLE_ACCENT),
        ))

    def _spec(self, platform):
        profile = self.registry.get(platform)
        return OriginalSceneSpecification(
            platform=platform,
            width=profile.width,
            height=profile.height,
            aspect_ratio=profile.aspect_ratio,
            safe_area={
                "top": profile.safe_area.top,
                "right": profile.safe_area.right,
                "bottom": profile.safe_area.bottom,
                "left": profile.safe_area.left,
            },
            family="general_world",
            concept="global sports season opener",
            subject=None,
            identity_reference=None,
            environment="global sports editorial world",
            composition="platform-specific editorial composition",
            camera_direction="wide premium framing",
            emotional_mood=Sentiment.ANTICIPATORY.value,
            palette_strategy="brand_red",
        )

    def test_layout_geometry_reaches_generation_package(self):
        profile = self.registry.get(SocialPlatform.INSTAGRAM_STORY)
        layout = self.layout_planner.plan(profile)
        package = self.compiler.compile(self._spec(SocialPlatform.INSTAGRAM_STORY), self.assets, planned_layout=layout)
        self.assertEqual(package.canvas, "1080x1920")
        self.assertIn("hero", package.layout_boxes)
        self.assertIn("logo", package.layout_boxes)
        self.assertIn("headline", package.layout_boxes)
        self.assertIn("social_footer", package.layout_boxes)
        self.assertEqual(package.accent_hex, "#E10600")
        self.assertEqual(package.metadata["layout_strategy"], "pul7sar-deterministic-v1")

    def test_entity_accent_reaches_package(self):
        profile = self.registry.get(SocialPlatform.INSTAGRAM_FEED)
        layout = self.layout_planner.plan(profile, entity_accent_hex="#DB0007")
        package = self.compiler.compile(self._spec(SocialPlatform.INSTAGRAM_FEED), self.assets, planned_layout=layout)
        self.assertEqual(package.accent_hex, "#DB0007")
        self.assertIn("#DB0007", package.scene_prompt)

    def test_result_geometry_can_include_score_and_crest(self):
        profile = self.registry.get(SocialPlatform.FACEBOOK_FEED)
        layout = self.layout_planner.plan(
            profile,
            LayoutRequirements(include_crest=True, include_score=True),
        )
        package = self.compiler.compile(self._spec(SocialPlatform.FACEBOOK_FEED), self.assets, planned_layout=layout)
        self.assertIn("score", package.layout_boxes)
        self.assertIn("crest", package.layout_boxes)

    def test_mismatched_platform_layout_is_rejected(self):
        x_layout = self.layout_planner.plan(self.registry.get(SocialPlatform.X_FEED))
        with self.assertRaises(ValueError):
            self.compiler.compile(self._spec(SocialPlatform.INSTAGRAM_FEED), self.assets, planned_layout=x_layout)


if __name__ == "__main__":
    unittest.main()
