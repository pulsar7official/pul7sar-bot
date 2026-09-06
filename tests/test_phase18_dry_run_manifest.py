import unittest

from engine.intelligence.assets import AssetBundle, AssetReference, AssetRole, AssetTreatment
from engine.intelligence.batch_scene import PlatformScenePackage
from engine.intelligence.dry_run_manifest import DryRunManifestCompiler
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.layout_planner import DeterministicLayoutPlanner
from engine.intelligence.models import Sentiment
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.scene_spec import OriginalSceneSpecification


class DryRunManifestTests(unittest.TestCase):
    def setUp(self):
        self.registry = PlatformProfileRegistry()
        self.planner = DeterministicLayoutPlanner()
        self.compiler = DryRunManifestCompiler()

    def _item(self, platform, accent="#E10600"):
        profile = self.registry.get(platform)
        layout = self.planner.plan(profile, entity_accent_hex=accent)
        spec = OriginalSceneSpecification(
            platform=platform,
            width=profile.width,
            height=profile.height,
            aspect_ratio=profile.aspect_ratio,
            safe_area={"top": profile.safe_area.top, "right": profile.safe_area.right, "bottom": profile.safe_area.bottom, "left": profile.safe_area.left},
            family="general_world",
            concept="season opener",
            subject=None,
            identity_reference=None,
            environment="premium sports world",
            composition="platform-specific",
            camera_direction="editorial wide",
            emotional_mood=Sentiment.ANTICIPATORY.value,
            palette_strategy="brand_red",
        )
        boxes = {box.role.value: {"x": box.x, "y": box.y, "width": box.width, "height": box.height} for box in layout.boxes}
        package = GenerationPackage(
            platform=platform.value,
            canvas=f"{profile.width}x{profile.height}",
            scene_prompt="approved dry run",
            negative_constraints=("no humiliation",),
            asset_ids=("pul7sar-logo", "pul7sar-pulse"),
            factual_constraints=("season approaches",),
            layout_boxes=boxes,
            accent_hex=layout.accent_hex,
            metadata={"dry_run": True, "layout_strategy": layout.strategy},
        )
        return PlatformScenePackage(spec, package, layout)

    def test_manifest_contains_distinct_platform_geometry(self):
        manifest = self.compiler.compile("story-001", (
            self._item(SocialPlatform.INSTAGRAM_STORY),
            self._item(SocialPlatform.X_FEED),
        )).to_dict()
        story = manifest["platforms"][SocialPlatform.INSTAGRAM_STORY.value]
        x = manifest["platforms"][SocialPlatform.X_FEED.value]
        self.assertEqual(story["canvas"], "1080x1920")
        self.assertEqual(x["canvas"], "1600x900")
        self.assertNotEqual(story["layout_boxes"]["hero"], x["layout_boxes"]["hero"])

    def test_manifest_carries_accent_assets_facts_and_constraints(self):
        manifest = self.compiler.compile("arsenal-story", (
            self._item(SocialPlatform.INSTAGRAM_FEED, "#EF0107"),
        )).to_dict()
        data = manifest["platforms"][SocialPlatform.INSTAGRAM_FEED.value]
        self.assertEqual(data["accent_hex"], "#EF0107")
        self.assertIn("pul7sar-logo", data["asset_ids"])
        self.assertIn("season approaches", data["factual_constraints"])
        self.assertIn("no humiliation", data["negative_constraints"])

    def test_empty_manifest_is_rejected(self):
        with self.assertRaises(ValueError):
            self.compiler.compile("story-001", ())

    def test_duplicate_platform_is_rejected(self):
        item = self._item(SocialPlatform.THREADS_FEED)
        with self.assertRaises(ValueError):
            self.compiler.compile("story-001", (item, item))


if __name__ == "__main__":
    unittest.main()
