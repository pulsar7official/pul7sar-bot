import unittest

from engine.intelligence.assets import AssetBundle, AssetReference, AssetRole, AssetTreatment
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.post_composition import (
    AssetIntegrityRecord,
    CompositionElement,
    CompositionRole,
    PostCompositionPlan,
    PostCompositionPlanner,
    PostCompositionQualityGate,
)


class PostCompositionTests(unittest.TestCase):
    def setUp(self):
        self.package = GenerationPackage(
            platform="instagram_feed",
            canvas="1080x1350",
            scene_prompt="base scene",
            negative_constraints=("no humiliation",),
            asset_ids=("pul7sar-logo", "pul7sar-pulse", "arsenal-crest", "social-instagram"),
            factual_constraints=("fixture fact",),
            layout_boxes={
                "hero": {"x": 80, "y": 180, "width": 600, "height": 700},
                "logo": {"x": 60, "y": 60, "width": 260, "height": 90},
                "crest": {"x": 880, "y": 60, "width": 120, "height": 120},
                "headline": {"x": 620, "y": 420, "width": 380, "height": 250},
                "score": {"x": 400, "y": 70, "width": 260, "height": 100},
                "social_footer": {"x": 250, "y": 1200, "width": 580, "height": 70},
            },
            accent_hex="#EF0107",
            metadata={"dry_run": True},
        )
        logo_hash = "a" * 64
        crest_hash = "b" * 64
        self.assets = AssetBundle((
            AssetReference("pul7sar-logo", AssetRole.PUL7SAR_LOGO, AssetTreatment.EXACT, metadata={"sha256": logo_hash}),
            AssetReference("pul7sar-pulse", AssetRole.PUL7SAR_PULSE, AssetTreatment.TINTABLE_ACCENT),
            AssetReference("arsenal-crest", AssetRole.TEAM_CREST, AssetTreatment.EXACT, metadata={"sha256": crest_hash}),
            AssetReference("social-instagram", AssetRole.SOCIAL_ICON, AssetTreatment.EXACT, metadata={"platform": "instagram"}),
        ))
        self.planner = PostCompositionPlanner()
        self.gate = PostCompositionQualityGate()

    def test_exact_assets_and_text_are_planned_outside_image_model(self):
        plan = self.planner.compile(
            self.package,
            self.assets,
            headline="Arsenal move closer",
            score="2–1",
            social_handle="PUL7SAR",
        )
        roles = [item.role for item in plan.elements]
        self.assertIn(CompositionRole.BRAND_LOGO, roles)
        self.assertIn(CompositionRole.BRAND_PULSE, roles)
        self.assertIn(CompositionRole.TEAM_CREST, roles)
        self.assertIn(CompositionRole.HEADLINE, roles)
        self.assertIn(CompositionRole.SCORE, roles)
        self.assertIn(CompositionRole.SOCIAL_FOOTER, roles)

    def test_only_pulse_receives_entity_accent(self):
        plan = self.planner.compile(self.package, self.assets)
        logo = next(item for item in plan.elements if item.role is CompositionRole.BRAND_LOGO)
        pulse = next(item for item in plan.elements if item.role is CompositionRole.BRAND_PULSE)
        crest = next(item for item in plan.elements if item.role is CompositionRole.TEAM_CREST)
        self.assertIsNone(logo.tint_hex)
        self.assertEqual(pulse.tint_hex, "#EF0107")
        self.assertIsNone(crest.tint_hex)

    def test_missing_text_box_is_rejected(self):
        package = GenerationPackage(
            platform="x_feed",
            canvas="1600x900",
            scene_prompt="base",
            negative_constraints=(),
            asset_ids=("pul7sar-logo", "pul7sar-pulse"),
            factual_constraints=(),
            layout_boxes={"logo": {"x": 1, "y": 1, "width": 10, "height": 10}},
            accent_hex="#E10600",
        )
        with self.assertRaises(ValueError):
            self.planner.compile(package, self.assets, headline="Headline")

    def test_checksum_verified_assets_pass_quality_gate(self):
        plan = self.planner.compile(
            self.package,
            self.assets,
            integrity_records=(
                AssetIntegrityRecord("pul7sar-logo", "a" * 64),
                AssetIntegrityRecord("arsenal-crest", "b" * 64),
            ),
        )
        self.assertTrue(self.gate.evaluate(self.package, self.assets, plan).allowed)

    def test_missing_declared_logo_checksum_fails_closed(self):
        assets = AssetBundle((
            AssetReference("pul7sar-logo", AssetRole.PUL7SAR_LOGO, AssetTreatment.EXACT),
            AssetReference("pul7sar-pulse", AssetRole.PUL7SAR_PULSE, AssetTreatment.TINTABLE_ACCENT),
        ))
        plan = self.planner.compile(self.package, assets)
        decision = self.gate.evaluate(self.package, assets, plan)
        self.assertFalse(decision.allowed)
        self.assertIn("missing valid declared checksum for PUL7SAR logo: pul7sar-logo", decision.failures)

    def test_missing_runtime_logo_integrity_record_fails_closed(self):
        plan = self.planner.compile(self.package, self.assets, integrity_records=(AssetIntegrityRecord("arsenal-crest", "b" * 64),))
        decision = self.gate.evaluate(self.package, self.assets, plan)
        self.assertFalse(decision.allowed)
        self.assertIn("missing integrity record for PUL7SAR logo: pul7sar-logo", decision.failures)

    def test_checksum_mismatch_fails_closed(self):
        plan = self.planner.compile(
            self.package,
            self.assets,
            integrity_records=(
                AssetIntegrityRecord("pul7sar-logo", "c" * 64),
                AssetIntegrityRecord("arsenal-crest", "b" * 64),
            ),
        )
        decision = self.gate.evaluate(self.package, self.assets, plan)
        self.assertFalse(decision.allowed)
        self.assertIn("asset checksum mismatch: pul7sar-logo", decision.failures)

    def test_wordmark_tint_is_rejected(self):
        plan = PostCompositionPlan(
            platform=self.package.platform,
            canvas=self.package.canvas,
            elements=(
                CompositionElement(CompositionRole.BRAND_LOGO, "logo", asset_id="pul7sar-logo", tint_hex="#EF0107"),
            ),
            integrity_records=(AssetIntegrityRecord("pul7sar-logo", "a" * 64),),
        )
        self.assertFalse(self.gate.evaluate(self.package, self.assets, plan).allowed)

    def test_team_crest_tint_is_rejected(self):
        plan = PostCompositionPlan(
            platform=self.package.platform,
            canvas=self.package.canvas,
            elements=(
                CompositionElement(CompositionRole.BRAND_LOGO, "logo", asset_id="pul7sar-logo"),
                CompositionElement(CompositionRole.TEAM_CREST, "crest", asset_id="arsenal-crest", tint_hex="#EF0107"),
            ),
            integrity_records=(
                AssetIntegrityRecord("pul7sar-logo", "a" * 64),
                AssetIntegrityRecord("arsenal-crest", "b" * 64),
            ),
        )
        self.assertFalse(self.gate.evaluate(self.package, self.assets, plan).allowed)

    def test_platform_or_canvas_mismatch_fails(self):
        plan = self.planner.compile(self.package, self.assets, integrity_records=(AssetIntegrityRecord("pul7sar-logo", "a" * 64),))
        bad = PostCompositionPlan("x_feed", plan.canvas, plan.elements, plan.integrity_records)
        self.assertFalse(self.gate.evaluate(self.package, self.assets, bad).allowed)


if __name__ == "__main__":
    unittest.main()
