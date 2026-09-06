import unittest
from dataclasses import replace

from PIL import Image, ImageDraw

from engine.intelligence.brand_reference_layers import BrandReferenceLayerExtractor
from engine.intelligence.brand_reference_master import APPROVED_BRAND_REFERENCE_MASTER


class BrandReferenceLayerExtractorTests(unittest.TestCase):
    def _synthetic_crop(self):
        image = Image.new("RGBA", (985, 320), (3, 8, 18, 255))
        draw = ImageDraw.Draw(image)
        # Neutral metallic samples live only inside measured letter ownership boxes.
        for box in BrandReferenceLayerExtractor._LETTER_BOXES:
            left, top, right, bottom = box
            draw.rectangle((left + 18, top + 25, right - 18, bottom - 25), fill=(205, 211, 220, 255))
        # Blue reference accent: enlarged 7 area + lower baseline/wave sample.
        draw.polygon(((430, 20), (590, 20), (520, 88), (490, 235), (440, 235), (475, 88)), fill=(20, 95, 245, 255))
        draw.line((40, 215, 825, 215), fill=(12, 105, 255, 255), width=8)
        draw.line((355, 215, 385, 160, 410, 270, 440, 130, 470, 245, 505, 205), fill=(18, 120, 255, 255), width=8)
        # Fixed football sample.
        draw.ellipse((885, 205, 955, 275), fill=(225, 228, 232, 255), outline=(35, 38, 44, 255), width=7)
        # Bright blue distractor outside approved accent ownership must not become accent.
        draw.ellipse((930, 40, 952, 62), fill=(15, 125, 255, 255))
        return image

    def test_reference_master_remains_study_only_and_sha_locked(self):
        APPROVED_BRAND_REFERENCE_MASTER.assert_safe()
        self.assertEqual(len(APPROVED_BRAND_REFERENCE_MASTER.source_sha256), 64)
        self.assertFalse(APPROVED_BRAND_REFERENCE_MASTER.publication_asset)
        forged = replace(APPROVED_BRAND_REFERENCE_MASTER, publication_asset=True)
        with self.assertRaisesRegex(ValueError, "NOT_PUBLICATION_ASSET"):
            forged.assert_safe()

    def test_seed_masks_separate_metal_accent_and_ball(self):
        crop = self._synthetic_crop()
        metal, accent, football = BrandReferenceLayerExtractor._seed_masks(crop)
        self.assertGreater(metal.getpixel((80, 110)), 0)
        self.assertEqual(accent.getpixel((80, 110)), 0)
        self.assertGreater(accent.getpixel((500, 70)), 0)
        self.assertEqual(metal.getpixel((500, 70)), 0)
        self.assertGreater(accent.getpixel((200, 215)), 0)
        self.assertGreater(football.getpixel((920, 235)), 0)
        self.assertEqual(accent.getpixel((940, 50)), 0)

    def test_resolved_ownership_blocks_tint_leakage_into_letters(self):
        crop = self._synthetic_crop()
        metal, accent, football = BrandReferenceLayerExtractor._seed_masks(crop)
        metal = BrandReferenceLayerExtractor._expand(metal, size=7, blur=1.1)
        accent = BrandReferenceLayerExtractor._expand(accent, size=11, blur=1.15)
        football = BrandReferenceLayerExtractor._expand(football, size=7, blur=1.0)
        metal, accent, football = BrandReferenceLayerExtractor._resolve_ownership(metal, accent, football)
        # Baseline crosses the U letter box in the source, but club tint must not
        # paint over the metallic letter surface.
        self.assertEqual(accent.getpixel((200, 215)), 0)
        self.assertGreater(metal.getpixel((200, 205)), 0)
        # The enlarged 7 remains foreground-owned in its central overlap zone.
        self.assertGreater(accent.getpixel((500, 70)), 0)
        self.assertEqual(metal.getpixel((500, 70)), 0)
        # Ball wins every overlap.
        self.assertGreater(football.getpixel((920, 235)), 0)
        self.assertEqual(accent.getpixel((920, 235)), 0)
        self.assertEqual(metal.getpixel((920, 235)), 0)

    def test_unverified_source_can_never_enter_exact_extraction(self):
        with self.assertRaises((FileNotFoundError, ValueError)):
            BrandReferenceLayerExtractor().extract("/tmp/not-the-approved-pul7sar-board.png")


if __name__ == "__main__":
    unittest.main()
