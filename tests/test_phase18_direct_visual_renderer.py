import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from engine.intelligence.assets import AssetBundle, AssetReference, AssetRole, AssetTreatment
from engine.intelligence.direct_visual_execution import DirectVisualExecutionPlanner
from engine.intelligence.direct_visual_renderer import DirectVisualRenderer, RenderAsset
from engine.intelligence.layout_planner import DeterministicLayoutPlanner, LayoutRequirements
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.editorial_headline_grammar import HeadlineTone


class DirectVisualRendererTests(unittest.TestCase):
    def setUp(self):
        self.orchestrator = StoryToVisualOrchestrator()
        self.planner = DirectVisualExecutionPlanner()
        self.renderer = DirectVisualRenderer()
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.layout = DeterministicLayoutPlanner().plan(
            self.profile,
            LayoutRequirements(include_crest=False, include_social_footer=False),
            entity_accent_hex="#EF0107",
        )
        self.assets = AssetBundle(())

    def story(self, event):
        return VerifiedEditorialStory(
            event=event,
            sport="football",
            subject="Arsenal",
            fact_phrase="verified update",
            story_core="verified story core",
            tone=HeadlineTone.NEUTRAL,
            confidence=0.98,
        )

    def test_deterministic_table_renders_real_png_with_sha_receipt(self):
        decision = self.orchestrator.decide(self.story(EditorialEvent.TABLE))
        plan = self.planner.compile(
            decision.execution_route,
            self.layout,
            self.assets,
            headline=decision.headline,
            exact_data=("1 Arsenal 9 pts", "2 Chelsea 7 pts"),
        )
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "table.png"
            receipt = self.renderer.render(plan, self.layout, output_path=str(out))
            payload = out.read_bytes()
            self.assertTrue(payload.startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertEqual(receipt.sha256, hashlib.sha256(payload).hexdigest())
            self.assertEqual((receipt.width, receipt.height), (self.profile.width, self.profile.height))
            self.assertEqual(receipt.renderer_contract, "pul7sar-direct-renderer-v1")

    def test_same_inputs_produce_same_exact_png_bytes(self):
        decision = self.orchestrator.decide(self.story(EditorialEvent.TACTICS))
        plan = self.planner.compile(decision.execution_route, self.layout, self.assets, headline=decision.headline, exact_data=("4-3-3",))
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.png"
            b = Path(tmp) / "b.png"
            ra = self.renderer.render(plan, self.layout, output_path=str(a))
            rb = self.renderer.render(plan, self.layout, output_path=str(b))
            self.assertEqual(ra.sha256, rb.sha256)
            self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_verified_asset_checksum_is_fail_closed(self):
        decision = self.orchestrator.decide(self.story(EditorialEvent.INJURY))
        assets = AssetBundle((AssetReference("verified-subject", AssetRole.VERIFIED_IDENTITY_REFERENCE, AssetTreatment.REFERENCE_ONLY),))
        plan = self.planner.compile(decision.execution_route, self.layout, assets, headline=decision.headline)
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "subject.png"
            Image.new("RGB", (200, 300), (50, 50, 50)).save(source)
            render_asset = RenderAsset("verified-subject", str(source), "0" * 64)
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                self.renderer.render(plan, self.layout, output_path=str(Path(tmp) / "out.png"), assets={"verified-subject": render_asset})

    def test_verified_asset_route_uses_exact_source_bytes_and_receipts_them(self):
        decision = self.orchestrator.decide(self.story(EditorialEvent.INJURY))
        assets = AssetBundle((AssetReference("verified-subject", AssetRole.VERIFIED_IDENTITY_REFERENCE, AssetTreatment.REFERENCE_ONLY),))
        plan = self.planner.compile(decision.execution_route, self.layout, assets, headline=decision.headline)
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "subject.png"
            Image.new("RGB", (200, 300), (80, 90, 100)).save(source)
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            receipt = self.renderer.render(
                plan,
                self.layout,
                output_path=str(Path(tmp) / "injury.png"),
                assets={"verified-subject": RenderAsset("verified-subject", str(source), digest)},
            )
            self.assertIn(("verified-subject", digest), receipt.asset_sha256)
            self.assertEqual(receipt.base_source, "verified_asset")


if __name__ == "__main__":
    unittest.main()
