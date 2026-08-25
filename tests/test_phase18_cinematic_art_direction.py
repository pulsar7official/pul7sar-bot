import unittest

from engine.intelligence.cinematic_art_direction import CinematicArtDirectionRegistry
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


class CinematicArtDirectionTests(unittest.TestCase):
    def test_every_family_has_distinct_camera_or_lens_language(self):
        signatures = set()
        for family in EditorialSceneFamily:
            d = CinematicArtDirectionRegistry.get(family)
            signatures.add((d.camera_xyz, d.look_at_xyz, d.lens_mm, d.aperture_fstop))
        self.assertEqual(len(signatures), len(tuple(EditorialSceneFamily)))

    def test_all_families_forbid_generic_centered_poster_and_placeholder_badge(self):
        for family in EditorialSceneFamily:
            avoid = CinematicArtDirectionRegistry.get(family).must_avoid
            self.assertIn("generic centered poster", avoid)
            self.assertIn("floating placeholder badge", avoid)
            self.assertIn("empty crest slot", avoid)

    def test_tactics_is_spatially_distinct_from_subject_news(self):
        tactics = CinematicArtDirectionRegistry.get(EditorialSceneFamily.TACTICAL_BOARD)
        subject = CinematicArtDirectionRegistry.get(EditorialSceneFamily.VERIFIED_SUBJECT_NEWS)
        self.assertGreater(tactics.camera_xyz[2], subject.camera_xyz[2])
        self.assertGreater(tactics.aperture_fstop, subject.aperture_fstop)
        self.assertIn("cropped mechanism", tactics.composition_language)
        self.assertIn("off-center subject", subject.composition_language)


if __name__ == "__main__":
    unittest.main()
