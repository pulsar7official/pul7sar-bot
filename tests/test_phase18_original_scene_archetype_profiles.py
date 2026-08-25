import unittest

from engine.intelligence.cross_family_visual_system import CrossFamilyVisualSystem
from engine.intelligence.original_scene_archetype_profiles import OriginalSceneArchetypeProfileRegistry
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


class OriginalSceneArchetypeProfilesTests(unittest.TestCase):
    def test_every_generative_cross_family_archetype_has_atmosphere_profile(self):
        for family in EditorialSceneFamily:
            if family is EditorialSceneFamily.TACTICAL_BOARD:
                continue
            archetypes = CrossFamilyVisualSystem.archetypes(family)
            self.assertEqual(len(archetypes), 4)
            for archetype in archetypes:
                profile = OriginalSceneArchetypeProfileRegistry.get(family, archetype.id)
                self.assertEqual(profile.family, family)
                self.assertEqual(profile.archetype_id, archetype.id)
                self.assertGreater(len(profile.atmosphere_prompt), 25)

    def test_wrong_family_archetype_fails_closed(self):
        with self.assertRaises(KeyError):
            OriginalSceneArchetypeProfileRegistry.get(
                EditorialSceneFamily.RESULT_STATEMENT,
                "threshold_arrival",
            )

    def test_tactical_remains_deterministic_first(self):
        with self.assertRaisesRegex(ValueError, "TACTICAL_BOARD_REMAINS_DETERMINISTIC_FIRST"):
            OriginalSceneArchetypeProfileRegistry.get(
                EditorialSceneFamily.TACTICAL_BOARD,
                "topology_map",
            )


if __name__ == "__main__":
    unittest.main()
