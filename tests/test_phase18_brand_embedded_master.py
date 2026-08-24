import base64
import unittest

from engine.intelligence.brand_embedded_master import EmbeddedBrandMasterLoader


class EmbeddedBrandMasterTests(unittest.TestCase):
    def test_embedded_bundle_verifies_and_loads_three_layers(self):
        master = EmbeddedBrandMasterLoader().load()
        receipt = master.receipt
        self.assertEqual(receipt.contract, "pul7sar-embedded-layered-brand-master-v1")
        self.assertEqual(receipt.bundle_sha256, EmbeddedBrandMasterLoader.BUNDLE_SHA256)
        self.assertEqual((receipt.width, receipt.height), (820, 266))
        self.assertEqual(master.metallic.size, (820, 266))
        self.assertEqual(master.accent.size, (820, 266))
        self.assertEqual(master.football.size, (820, 266))
        self.assertTrue(receipt.self_contained)
        self.assertTrue(receipt.reference_derived)
        self.assertFalse(receipt.network_required)
        self.assertFalse(receipt.font_required)
        self.assertFalse(receipt.generator_required)
        self.assertTrue(receipt.study_only)
        self.assertFalse(receipt.publication_ready)

    def test_layer_masks_have_real_nonempty_alpha_and_are_separate(self):
        master = EmbeddedBrandMasterLoader().load()
        metal_alpha = master.metallic.getchannel("A")
        accent_alpha = master.accent.getchannel("A")
        football_alpha = master.football.getchannel("A")
        self.assertGreater(metal_alpha.getbbox()[2] - metal_alpha.getbbox()[0], 300)
        self.assertGreater(accent_alpha.getbbox()[2] - accent_alpha.getbbox()[0], 300)
        self.assertGreater(football_alpha.getbbox()[2] - football_alpha.getbbox()[0], 30)
        # The football occupies the far-right zone; the enlarged 7/pulse owns
        # the centre; the metallic wordmark spans both sides.
        self.assertGreater(football_alpha.getbbox()[0], 650)
        self.assertLess(accent_alpha.getbbox()[0], 80)
        self.assertGreater(accent_alpha.getbbox()[2], 600)

    def test_transport_noise_can_be_ignored_only_before_binary_sha_verification(self):
        original = b"PUL7SAR transport test"
        encoded = base64.b64encode(original).decode("ascii")
        noisy = encoded[:8] + "!" + encoded[8:]
        self.assertEqual(EmbeddedBrandMasterLoader._decode_bundle_text(noisy), original)
        # The production loader still pins the exact decoded archive SHA; this
        # recovery helper does not alter or replace that binary integrity lock.
        self.assertEqual(
            EmbeddedBrandMasterLoader.BUNDLE_SHA256,
            "49ed35398dbb3a62460ff4ee52b7eea7b0db295b165271cef1126484d3d15d62",
        )

    def test_literal_ellipsization_is_rejected_as_irrecoverable_truncation(self):
        original = base64.b64encode(b"PUL7SAR approved bytes").decode("ascii")
        truncated = original[:12] + "[...ELLIPSIZATION...]" + original[12:]
        with self.assertRaisesRegex(ValueError, "PUL7SAR_EMBEDDED_BRAND_TRANSPORT_TRUNCATED"):
            EmbeddedBrandMasterLoader._decode_bundle_text(truncated)


if __name__ == "__main__":
    unittest.main()
