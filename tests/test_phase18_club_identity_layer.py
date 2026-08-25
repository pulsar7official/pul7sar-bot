import tempfile
import unittest
from pathlib import Path

from PIL import Image

from engine.intelligence.club_identity_layer import ClubIdentity, ClubIdentityLayerRenderer


class ClubIdentityLayerTests(unittest.TestCase):
    def test_missing_crest_never_fabricates_identity_pixels(self):
        image = Image.new("RGBA", (1080, 1350), (8, 12, 20, 255))
        evidence = ClubIdentityLayerRenderer.render(
            image,
            home=ClubIdentity("NORTH CITY", "#E30613"),
            away=ClubIdentity("SOUTH UNITED", "#1D5EFF", "/missing/crest.png"),
        )
        self.assertFalse(evidence.home_crest_used)
        self.assertFalse(evidence.away_crest_used)
        self.assertFalse(evidence.fabricated_crest_used)
        self.assertEqual(evidence.crest_policy, "explicit_local_asset_only_no_fabrication")

    def test_explicit_png_crest_is_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            crest_path = Path(td) / "crest.png"
            Image.new("RGBA", (96, 96), (220, 30, 40, 255)).save(crest_path)
            image = Image.new("RGBA", (1080, 1350), (8, 12, 20, 255))
            evidence = ClubIdentityLayerRenderer.render(
                image,
                home=ClubIdentity("NORTH CITY", "#E30613", str(crest_path)),
                away=ClubIdentity("SOUTH UNITED", "#1D5EFF"),
            )
            self.assertTrue(evidence.home_crest_used)
            self.assertFalse(evidence.away_crest_used)
            self.assertFalse(evidence.fabricated_crest_used)

    def test_non_image_asset_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "crest.txt"
            path.write_text("not a crest", encoding="utf-8")
            self.assertIsNone(ClubIdentity("NORTH CITY", "#E30613", str(path)).verified_crest_path())


if __name__ == "__main__":
    unittest.main()
