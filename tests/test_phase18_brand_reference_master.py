import unittest
from dataclasses import replace

from engine.intelligence.brand_reference_master import APPROVED_BRAND_REFERENCE_MASTER


class BrandReferenceMasterTests(unittest.TestCase):
    def test_approved_board_and_crop_are_locked(self):
        ref = APPROVED_BRAND_REFERENCE_MASTER
        ref.assert_safe()
        self.assertEqual(ref.source_sha256, "a6d0f33c815bc2801b923bf00b255000b46eff3120d9f16bd7d6981e6f3cbbb1")
        self.assertEqual(ref.crop_sha256, "5e4a94502134291f4a6522fbc3dbe54ed741b691c2f6e81f80df095cbcb9026c")
        self.assertEqual((ref.crop_left, ref.crop_top, ref.crop_right, ref.crop_bottom), (50, 70, 1035, 390))
        self.assertTrue(ref.exact_shape_reference)
        self.assertFalse(ref.publication_asset)

    def test_reference_crop_cannot_silently_drift(self):
        forged = replace(APPROVED_BRAND_REFERENCE_MASTER, crop_left=51)
        with self.assertRaisesRegex(ValueError, "BRAND_REFERENCE_CROP_DRIFTED"):
            forged.assert_safe()

    def test_reference_board_is_not_promoted_to_publication_asset(self):
        forged = replace(APPROVED_BRAND_REFERENCE_MASTER, publication_asset=True)
        with self.assertRaisesRegex(ValueError, "IDENTITY_BOARD_CROP_IS_NOT_PUBLICATION_ASSET"):
            forged.assert_safe()


if __name__ == "__main__":
    unittest.main()
