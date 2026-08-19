import unittest
from dataclasses import FrozenInstanceError

from engine.branding.defaults import TEMPORARY_BRAND_PRIMARY, get_default_brand_palette


class TestBranding(unittest.TestCase):
    def test_brand_palette_is_frozen(self):
        palette = get_default_brand_palette()
        with self.assertRaises(FrozenInstanceError):
            palette.primary = (1, 2, 3)  # type: ignore[misc]

    def test_temporary_primary_is_centralized(self):
        self.assertEqual(get_default_brand_palette().primary, TEMPORARY_BRAND_PRIMARY)
        self.assertEqual(get_default_brand_palette().brand_id, "pul7sar_temp")


if __name__ == "__main__":
    unittest.main()
