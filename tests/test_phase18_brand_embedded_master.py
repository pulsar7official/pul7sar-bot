import tempfile
import unittest
from pathlib import Path

from engine.intelligence.brand_embedded_master import EmbeddedBrandMasterLoader


class EmbeddedBrandMasterTests(unittest.TestCase):
    def test_compact_master_verifies_and_loads_three_reference_layers(self):
        master = EmbeddedBrandMasterLoader().load()
        receipt = master.receipt
        self.assertEqual(receipt.contract, "pul7sar-embedded-layered-brand-master-v3-compact-member-pinned")
        self.assertEqual(len(receipt.bundle_sha256), 64)
        self.assertTrue(receipt.member_integrity_pinned)
        self.assertFalse(receipt.container_sha_authoritative)
        self.assertEqual(receipt.texture_sha256, EmbeddedBrandMasterLoader.RAW_SHA256["luma"])
        self.assertEqual(receipt.metallic_mask_sha256, EmbeddedBrandMasterLoader.RAW_SHA256["metal"])
        self.assertEqual(receipt.accent_mask_sha256, EmbeddedBrandMasterLoader.RAW_SHA256["accent"])
        self.assertEqual(receipt.football_mask_sha256, EmbeddedBrandMasterLoader.RAW_SHA256["ball"])
        self.assertEqual((receipt.compact_source_width, receipt.compact_source_height), (300, 97))
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

    def test_every_transport_fragment_and_decoded_raster_is_sha_pinned(self):
        self.assertEqual(set(EmbeddedBrandMasterLoader.TRANSPORT_SHA256), {
            "metal.b85", "accent.b85", "ball.b85", "luma.part1.b85", "luma.part2.b85"
        })
        self.assertEqual(set(EmbeddedBrandMasterLoader.RAW_SHA256), {"metal", "accent", "ball", "luma"})
        self.assertTrue(all(len(value) == 64 for value in EmbeddedBrandMasterLoader.TRANSPORT_SHA256.values()))
        self.assertTrue(all(len(value) == 64 for value in EmbeddedBrandMasterLoader.RAW_SHA256.values()))

    def test_transport_tampering_fails_closed(self):
        source = Path("assets/brand/compact_v1")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "assets/brand/compact_v1"
            root.mkdir(parents=True)
            for path in source.iterdir():
                if path.is_file():
                    (root / path.name).write_bytes(path.read_bytes())
            path = root / "accent.b85"
            text = path.read_text(encoding="ascii")
            path.write_text(("A" if text[0] != "A" else "B") + text[1:], encoding="ascii")
            with self.assertRaisesRegex(ValueError, "TRANSPORT_SHA_MISMATCH"):
                EmbeddedBrandMasterLoader().load(repository_root=tmp)


if __name__ == "__main__":
    unittest.main()
