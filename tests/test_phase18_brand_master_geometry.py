import unittest

from engine.intelligence.brand_master_geometry import (
    BrandMasterGeometryGate,
    BrandMasterGeometryState,
    ExactBrandGeometryAsset,
)


class BrandMasterGeometryGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = BrandMasterGeometryGate()
        digest_a = "a" * 64
        digest_b = "b" * 64
        self.wordmark = ExactBrandGeometryAsset(
            "pul7sar-metallic-wordmark-master",
            "assets/brand/pul7sar-metallic-wordmark-master.png",
            digest_a,
            "user-approved-phase18-brand-master",
        )
        self.pulse = ExactBrandGeometryAsset(
            "pul7sar-pulse-seven-master",
            "assets/brand/pul7sar-pulse-seven-master.png",
            digest_b,
            "user-approved-phase18-brand-master",
        )

    def test_requires_both_separate_components(self):
        with self.assertRaisesRegex(ValueError, "METALLIC_WORDMARK"):
            self.gate.require(BrandMasterGeometryState())
        with self.assertRaisesRegex(ValueError, "PULSE_SEVEN"):
            self.gate.require(BrandMasterGeometryState(self.wordmark, None))
        state = self.gate.require(BrandMasterGeometryState(self.wordmark, self.pulse))
        self.assertTrue(state.ready)

    def test_legacy_logo_png_cannot_be_registered_as_master_geometry(self):
        with self.assertRaisesRegex(ValueError, "LEGACY_REPO_BRAND_ASSET_CANNOT_BE_MASTER_GEOMETRY"):
            ExactBrandGeometryAsset("legacy", "logo.png", "c" * 64, "legacy")
        with self.assertRaisesRegex(ValueError, "LEGACY_REPO_BRAND_ASSET_CANNOT_BE_MASTER_GEOMETRY"):
            ExactBrandGeometryAsset("legacy", "pulsar7.PNG", "d" * 64, "legacy")

    def test_components_must_not_share_same_asset_id(self):
        duplicate = ExactBrandGeometryAsset(
            self.wordmark.asset_id,
            "assets/brand/pulse.png",
            "e" * 64,
            "approved",
        )
        with self.assertRaisesRegex(ValueError, "SEPARATE_ASSETS"):
            self.gate.require(BrandMasterGeometryState(self.wordmark, duplicate))

    def test_runtime_checksum_is_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "CHECKSUM_MISMATCH"):
            self.gate.verify_runtime_bytes(self.wordmark, "f" * 64)


if __name__ == "__main__":
    unittest.main()
