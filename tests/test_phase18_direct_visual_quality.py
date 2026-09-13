import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from engine.intelligence.assets import AssetBundle
from engine.intelligence.direct_visual_execution import DirectVisualExecutionPlanner
from engine.intelligence.direct_visual_quality import DirectRenderQualityGate
from engine.intelligence.direct_visual_renderer import DirectVisualRenderer
from engine.intelligence.layout_planner import DeterministicLayoutPlanner, LayoutRequirements
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.editorial_headline_grammar import HeadlineTone


class DirectRenderQualityGateTests(unittest.TestCase):
    def setUp(self):
        self.orchestrator = StoryToVisualOrchestrator()
        self.planner = DirectVisualExecutionPlanner()
        self.renderer = DirectVisualRenderer()
        self.gate = DirectRenderQualityGate()
        profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.layout = DeterministicLayoutPlanner().plan(
            profile,
            LayoutRequirements(include_crest=False, include_social_footer=False),
        )
        story = VerifiedEditorialStory(
            event=EditorialEvent.TABLE,
            sport="football",
            subject="Arsenal",
            fact_phrase="verified table update",
            story_core="verified table story",
            tone=HeadlineTone.NEUTRAL,
            confidence=0.99,
        )
        decision = self.orchestrator.decide(story)
        self.plan = self.planner.compile(
            decision.execution_route,
            self.layout,
            AssetBundle(()),
            headline=decision.headline,
            exact_data=("1 Arsenal 9 pts",),
        )

    def test_real_direct_png_passes_publication_integrity_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.renderer.render(self.plan, self.layout, output_path=str(Path(tmp) / "golden-direct.png"))
            decision = self.gate.evaluate(self.plan, self.layout, receipt)
            self.assertTrue(decision.allowed, decision.failures)

    def test_modified_png_after_receipt_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "golden-direct.png"
            receipt = self.renderer.render(self.plan, self.layout, output_path=str(path))
            path.write_bytes(path.read_bytes() + b"tampered")
            decision = self.gate.evaluate(self.plan, self.layout, receipt)
            self.assertFalse(decision.allowed)
            self.assertIn("render output checksum does not match receipt", decision.failures)

    def test_wrong_route_receipt_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.renderer.render(self.plan, self.layout, output_path=str(Path(tmp) / "golden-direct.png"))
            forged = replace(receipt, route="verified_asset_only")
            decision = self.gate.evaluate(self.plan, self.layout, forged)
            self.assertFalse(decision.allowed)
            self.assertIn("receipt route does not match execution plan", decision.failures)

    def test_missing_output_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self.renderer.render(self.plan, self.layout, output_path=str(Path(tmp) / "golden-direct.png"))
            Path(receipt.output_path).unlink()
            decision = self.gate.evaluate(self.plan, self.layout, receipt)
            self.assertFalse(decision.allowed)
            self.assertEqual(decision.failures, ("render output is missing",))


if __name__ == "__main__":
    unittest.main()
