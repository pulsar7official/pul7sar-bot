import unittest

from engine.intelligence.cost_policy import BillingClass, ProviderEconomics
from engine.intelligence.provider_capabilities import (
    ProviderCapabilities, ProviderEligibilityGate, ProviderFeature, ProviderRequirements,
)
from engine.intelligence.provider_selection import ProviderSelector


class ProviderEligibilityTests(unittest.TestCase):
    def setUp(self):
        self.gate = ProviderEligibilityGate()
        self.requirements = ProviderRequirements(
            width=1080,
            height=1920,
            aspect_ratio="9:16",
            required_features=frozenset({
                ProviderFeature.TEXT_TO_IMAGE,
                ProviderFeature.REFERENCE_IMAGE,
                ProviderFeature.TRANSPARENT_PNG_INPUT,
                ProviderFeature.NEGATIVE_INSTRUCTIONS,
            }),
            reference_image_count=2,
        )

    def capable(self, provider_id="capable"):
        return ProviderCapabilities(
            provider_id=provider_id,
            features=frozenset({
                ProviderFeature.TEXT_TO_IMAGE,
                ProviderFeature.REFERENCE_IMAGE,
                ProviderFeature.MULTIPLE_REFERENCES,
                ProviderFeature.TRANSPARENT_PNG_INPUT,
                ProviderFeature.NEGATIVE_INSTRUCTIONS,
                ProviderFeature.POST_COMPOSITING,
            }),
            max_width=2048,
            max_height=2048,
            supported_aspect_ratios=frozenset({"9:16", "4:5", "16:9"}),
            max_reference_images=4,
        )

    @staticmethod
    def free(provider_id):
        return ProviderEconomics(provider_id, BillingClass.LOCAL_FREE)

    def test_capable_provider_is_eligible(self):
        self.assertTrue(self.gate.evaluate(self.capable(), self.requirements).eligible)

    def test_missing_reference_support_is_rejected(self):
        provider = ProviderCapabilities(
            "weak",
            frozenset({ProviderFeature.TEXT_TO_IMAGE}),
            2048, 2048,
            frozenset({"9:16"}),
            0,
        )
        decision = self.gate.evaluate(provider, self.requirements)
        self.assertFalse(decision.eligible)
        self.assertIn("reference_image", decision.missing_features)
        self.assertIn("transparent_png_input", decision.missing_features)

    def test_insufficient_resolution_is_rejected(self):
        provider = self.capable("small")
        provider = ProviderCapabilities(provider.provider_id, provider.features, 1024, 1024, provider.supported_aspect_ratios, 4)
        decision = self.gate.evaluate(provider, self.requirements)
        self.assertFalse(decision.eligible)
        self.assertTrue(any("exceeds provider maximum" in reason for reason in decision.reasons))

    def test_unsupported_aspect_ratio_is_rejected(self):
        provider = self.capable("square-only")
        provider = ProviderCapabilities(provider.provider_id, provider.features, 2048, 2048, frozenset({"1:1"}), 4)
        decision = self.gate.evaluate(provider, self.requirements)
        self.assertFalse(decision.eligible)
        self.assertIn("unsupported aspect ratio: 9:16", decision.reasons)

    def test_reference_count_is_enforced(self):
        provider = self.capable("one-ref")
        provider = ProviderCapabilities(provider.provider_id, provider.features, 2048, 2048, provider.supported_aspect_ratios, 1)
        decision = self.gate.evaluate(provider, self.requirements)
        self.assertFalse(decision.eligible)
        self.assertTrue(any("requires 2 reference images" in reason for reason in decision.reasons))

    def test_selector_skips_ineligible_provider_and_uses_explicit_free_fallback(self):
        weak = ProviderCapabilities("preferred-but-ineligible", frozenset({ProviderFeature.TEXT_TO_IMAGE}), 2048, 2048, frozenset({"9:16"}), 0)
        fallback = self.capable("approved-fallback")
        economics = {
            "preferred-but-ineligible": self.free("preferred-but-ineligible"),
            "approved-fallback": self.free("approved-fallback"),
        }
        selection = ProviderSelector().select((weak, fallback), self.requirements, economics=economics)
        self.assertEqual(selection.selected_provider_id, "approved-fallback")
        self.assertFalse(selection.decisions[0].eligible)
        self.assertTrue(selection.decisions[1].eligible)

    def test_paid_provider_is_blocked_in_zero_cost_mode(self):
        provider = self.capable("paid-provider")
        economics = {
            "paid-provider": ProviderEconomics("paid-provider", BillingClass.PAID_USAGE, requires_payment_method=True)
        }
        selection = ProviderSelector().select((provider,), self.requirements, economics=economics)
        self.assertFalse(selection.found)
        self.assertTrue(any("paid-usage provider is disabled" in item for item in selection.cost_rejections))

    def test_undeclared_economics_are_blocked(self):
        provider = self.capable("unknown-cost")
        selection = ProviderSelector().select((provider,), self.requirements)
        self.assertFalse(selection.found)
        self.assertTrue(any("zero-cost status unproven" in item for item in selection.cost_rejections))

    def test_free_tier_without_payment_method_is_allowed(self):
        provider = self.capable("free-tier")
        economics = {"free-tier": ProviderEconomics("free-tier", BillingClass.FREE_TIER, requires_payment_method=False)}
        selection = ProviderSelector().select((provider,), self.requirements, economics=economics)
        self.assertEqual(selection.selected_provider_id, "free-tier")

    def test_free_tier_requiring_payment_method_is_blocked(self):
        provider = self.capable("free-but-card-required")
        economics = {
            "free-but-card-required": ProviderEconomics(
                "free-but-card-required", BillingClass.FREE_TIER, requires_payment_method=True
            )
        }
        selection = ProviderSelector().select((provider,), self.requirements, economics=economics)
        self.assertFalse(selection.found)

    def test_selector_returns_no_provider_when_none_can_comply(self):
        weak = ProviderCapabilities("weak", frozenset({ProviderFeature.TEXT_TO_IMAGE}), 1024, 1024, frozenset({"1:1"}), 0)
        selection = ProviderSelector().select((weak,), self.requirements, economics={"weak": self.free("weak")})
        self.assertFalse(selection.found)
        self.assertIsNone(selection.selected_provider_id)

    def test_duplicate_provider_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            ProviderSelector().select((self.capable("same"), self.capable("same")), self.requirements)


if __name__ == "__main__":
    unittest.main()
