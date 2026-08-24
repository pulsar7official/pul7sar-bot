import base64
import unittest

from engine.intelligence.brand_embedded_master import EmbeddedBrandMasterLoader


class EmbeddedBrandMasterTests(unittest.TestCase):
    def test_embedded_bundle_verifies_and_loads_three_layers(self):
        master = EmbeddedBrandMasterLoader().load()
        receipt = master.receipt
        self.assertEqual(receipt.contract, "pul7sar-embedded-layered-brand-master-v2-member-pinned")
        self.assertEqual(len(receipt.bundle_sha256), 64)
        self.assertTrue(receipt.member_integrity_pinned)
        self.assertFalse(receipt.container_sha_authoritative)
        self.assertEqual(receipt.texture_sha256, EmbeddedBrandMasterLoader.MEMBER_SHA256["texture.webp"])
        self.assertEqual(receipt.metallic_mask_sha256, EmbeddedBrandMasterLoader.MEMBER_SHA256["metal_mask.png"])
        self.assertEqual(receipt.accent_mask_sha256, EmbeddedBrandMasterLoader.MEMBER_SHA256["accent_mask.png"])
        self.assertEqual(receipt.football_mask_sha256, EmbeddedBrandMasterLoader.MEMBER_SHA256["ball_mask.png"])
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
        self.assertGreater(football_alpha.getbbox()[0], 650)
        self.assertLess(accent_alpha.getbbox()[0], 80)
        self.assertGreater(accent_alpha.getbbox()[2], 600)

    def test_transport_noise_does_not_replace_member_integrity(self):
        original = b"PUL7SAR transport test"
        encoded = base64.b64encode(original).decode("ascii")
        noisy = encoded[:8] + "!" + encoded[8:]
        self.assertEqual(EmbeddedBrandMasterLoader._decode_bundle_text(noisy), original)
        self.assertEqual(set(EmbeddedBrandMasterLoader.MEMBER_SHA256), {
            "texture.webp", "metal_mask.png", "accent_mask.png", "ball_mask.png"
        })
        self.assertTrue(all(len(value) == 64 for value in EmbeddedBrandMasterLoader.MEMBER_SHA256.values()))

    def test_literal_ellipsization_is_rejected_as_irrecoverable_truncation(self):
        original = base64.b64encode(b"PUL7SAR approved bytes").decode("ascii")
        truncated = original[:12] + "[...ELLIPSIZATION...]" + original[12:]
        with self.assertRaisesRegex(ValueError, "PUL7SAR_EMBEDDED_BRAND_TRANSPORT_TRUNCATED"):
            EmbeddedBrandMasterLoader._decode_bundle_text(truncated)


if __name__ == "__main__":
    unittest.main()
