import unittest

from engine.intelligence.cross_family_visual_system import CrossFamilyVisualSystem
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


class CrossFamilyVisualSystemTests(unittest.TestCase):
    def test_every_family_has_at_least_four_distinct_archetypes(self):
        for family in EditorialSceneFamily:
            archetypes = CrossFamilyVisualSystem.archetypes(family)
            self.assertGreaterEqual(len(archetypes), 4, family.value)
            self.assertEqual(len({a.id for a in archetypes}), len(archetypes))

    def test_every_archetype_rejects_generic_centered_template(self):
        for family in EditorialSceneFamily:
            for archetype in CrossFamilyVisualSystem.archetypes(family):
                self.assertIn("generic centered template", archetype.forbidden_shortcuts)

    def test_recent_archetypes_are_avoided_within_family(self):
        family = EditorialSceneFamily.TRANSFER_SIGNATURE
        library = CrossFamilyVisualSystem.archetypes(family)
        recent = tuple(a.id for a in library[:3])
        decision = CrossFamilyVisualSystem.choose(family=family, story_key="transfer-next", recent_archetypes=recent, seed=9)
        self.assertNotIn(decision.archetype.id, recent)
        self.assertTrue(decision.anti_repetition_applied)

    def test_selection_is_reproducible_for_a_story(self):
        kwargs = dict(family=EditorialSceneFamily.EVENT_EDITORIAL, story_key="event-2026-001", seed=18)
        self.assertEqual(CrossFamilyVisualSystem.choose(**kwargs), CrossFamilyVisualSystem.choose(**kwargs))

    def test_tactical_archetypes_own_structure_not_decorative_portrait(self):
        joined = " ".join(a.hero for a in CrossFamilyVisualSystem.archetypes(EditorialSceneFamily.TACTICAL_BOARD))
        self.assertIn("tactical", joined)
        self.assertNotIn("decorative player portrait", joined)


if __name__ == "__main__":
    unittest.main()
