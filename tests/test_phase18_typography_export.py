import unittest

from engine.intelligence.assets import AssetBundle, AssetReference, AssetRole, AssetTreatment
from engine.intelligence.final_export import FinalComposedOutput, FinalExportGate
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.post_composition import PostCompositionPlanner
from engine.intelligence.typography import (
    DeterministicTypographyEngine,
    FontReference,
    Pul7sarTypographyPolicy,
    TextBox,
    TextRole,
)


class TypographyExportTests(unittest.TestCase):
    def setUp(self):
        self.engine = DeterministicTypographyEngine()
        self.font = FontReference("pul7sar-ui-bold", "PUL7SAR UI", 700)
        self.headline_style = Pul7sarTypographyPolicy.headline(self.font)
        self.score_style = Pul7sarTypographyPolicy.score(self.font)
        self.footer_style = Pul7sarTypographyPolicy.social_footer(self.font)
        self.package = GenerationPackage(
            platform="instagram_feed",
            canvas="1080x1350",
            scene_prompt="base scene",
            negative_constraints=(),
            asset_ids=("logo", "pulse", "crest", "instagram"),
            factual_constraints=(),
            layout_boxes={
                "logo": {"x": 80, "y": 60, "width": 230, "height": 80},
                "crest": {"x": 880, "y": 60, "width": 120, "height": 120},
                "headline": {"x": 560, "y": 390, "width": 430, "height": 270},
                "score": {"x": 360, "y": 60, "width": 360, "height": 100},
                "social_footer": {"x": 240, "y": 1190, "width": 600, "height": 60},
            },
            accent_hex="#EF0107",
            metadata={},
        )
        self.assets = AssetBundle((
            AssetReference("logo", AssetRole.PUL7SAR_LOGO, AssetTreatment.EXACT),
            AssetReference("pulse", AssetRole.PUL7SAR_PULSE, AssetTreatment.TINTABLE_ACCENT),
            AssetReference("crest", AssetRole.TEAM_CREST, AssetTreatment.EXACT),
            AssetReference("instagram", AssetRole.SOCIAL_ICON, AssetTreatment.EXACT, metadata={"platform": "instagram"}),
        ))

    def text_box(self, role):
        box = self.package.layout_boxes[role]
        return TextBox(box["x"], box["y"], box["width"], box["height"])

    def test_headline_fits_without_silent_truncation(self):
        layout = self.engine.fit("Arsenal move closer to the deal", self.text_box("headline"), self.headline_style)
        self.assertFalse(layout.truncated)
        self.assertLessEqual(len(layout.lines), 3)

    def test_overlong_headline_fails_closed(self):
        tiny = TextBox(0, 0, 80, 40)
        with self.assertRaises(ValueError):
            self.engine.fit("This headline cannot possibly fit safely inside this tiny box", tiny, self.headline_style)

    def test_score_is_single_line(self):
        layout = self.engine.fit("3 - 1", self.text_box("score"), self.score_style)
        self.assertEqual(len(layout.lines), 1)

    def test_social_footer_is_compact_single_line(self):
        layout = self.engine.fit("PUL7SAR", self.text_box("social_footer"), self.footer_style)
        self.assertEqual(len(layout.lines), 1)

    def test_export_authorizes_complete_valid_output(self):
        plan = PostCompositionPlanner().compile(
            self.package,
            self.assets,
            headline="Arsenal move closer to the deal",
            score="3 - 1",
            social_handle="PUL7SAR",
        )
        layouts = (
            self.engine.fit("Arsenal move closer to the deal", self.text_box("headline"), self.headline_style),
            self.engine.fit("3 - 1", self.text_box("score"), self.score_style),
            self.engine.fit("PUL7SAR", self.text_box("social_footer"), self.footer_style),
        )
        output = FinalComposedOutput(
            "instagram_feed", "1080x1350", "base-scene", "composed-final", layouts
        )
        auth = FinalExportGate().authorize(
            self.package,
            self.assets,
            plan,
            output,
            approved_styles={
                TextRole.HEADLINE.value: self.headline_style,
                TextRole.SCORE.value: self.score_style,
                TextRole.SOCIAL_FOOTER.value: self.footer_style,
            },
        )
        self.assertTrue(auth.allowed)
        self.assertIsNotNone(auth.token)

    def test_export_rejects_missing_rendered_headline(self):
        plan = PostCompositionPlanner().compile(
            self.package,
            self.assets,
            headline="Arsenal move closer to the deal",
            social_handle="PUL7SAR",
        )
        output = FinalComposedOutput(
            "instagram_feed",
            "1080x1350",
            "base-scene",
            "composed-final",
            (self.engine.fit("PUL7SAR", self.text_box("social_footer"), self.footer_style),),
        )
        auth = FinalExportGate().authorize(
            self.package,
            self.assets,
            plan,
            output,
            approved_styles={TextRole.SOCIAL_FOOTER.value: self.footer_style},
        )
        self.assertFalse(auth.allowed)
        self.assertTrue(any("missing rendered text roles" in failure for failure in auth.failures))

    def test_export_rejects_wrong_text_geometry(self):
        plan = PostCompositionPlanner().compile(
            self.package, self.assets, headline="Arsenal move closer"
        )
        layout = self.engine.fit("Arsenal move closer", TextBox(0, 0, 430, 270), self.headline_style)
        output = FinalComposedOutput("instagram_feed", "1080x1350", "base", "final", (layout,))
        auth = FinalExportGate().authorize(
            self.package,
            self.assets,
            plan,
            output,
            approved_styles={TextRole.HEADLINE.value: self.headline_style},
        )
        self.assertFalse(auth.allowed)
        self.assertIn("text geometry mismatch: headline", auth.failures)

    def test_export_rejects_unapproved_font(self):
        plan = PostCompositionPlanner().compile(self.package, self.assets, headline="Arsenal move closer")
        wrong_style = Pul7sarTypographyPolicy.headline(FontReference("wrong-font", "Wrong", 700))
        layout = self.engine.fit("Arsenal move closer", self.text_box("headline"), wrong_style)
        output = FinalComposedOutput("instagram_feed", "1080x1350", "base", "final", (layout,))
        auth = FinalExportGate().authorize(
            self.package,
            self.assets,
            plan,
            output,
            approved_styles={TextRole.HEADLINE.value: self.headline_style},
        )
        self.assertFalse(auth.allowed)
        self.assertTrue(any("unapproved font reference" in failure for failure in auth.failures))


if __name__ == "__main__":
    unittest.main()
