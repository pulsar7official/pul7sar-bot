import unittest

from engine.intelligence.cross_family_visual_system import CrossFamilyVisualSystem
from engine.intelligence.sdxl_compact_prompt import SDXLCompactPromptCompiler
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


class SDXLCompactPromptTests(unittest.TestCase):
    def test_every_generative_archetype_has_compact_prompt(self):
        for family in EditorialSceneFamily:
            if family is EditorialSceneFamily.TACTICAL_BOARD:
                continue
            for archetype in CrossFamilyVisualSystem.archetypes(family):
                plan = SDXLCompactPromptCompiler.compile(family, archetype.id)
                self.assertEqual(plan.family, family)
                self.assertEqual(plan.archetype_id, archetype.id)
                self.assertIn("Association soccer", plan.prompt)
                self.assertLess(len(plan.prompt.split()), 55)

    def test_prompts_do_not_delegate_exact_identity_or_result(self):
        banned = ("Arsenal", "Liverpool", "3-1", "PUL7SAR", "logo", "crest")
        for family in EditorialSceneFamily:
            if family is EditorialSceneFamily.TACTICAL_BOARD:
                continue
            for archetype in CrossFamilyVisualSystem.archetypes(family):
                prompt = SDXLCompactPromptCompiler.compile(family, archetype.id).prompt
                for token in banned:
                    self.assertNotIn(token, prompt)

    def test_data_number_sculpture_stays_engineered_not_natural(self):
        plan = SDXLCompactPromptCompiler.compile(EditorialSceneFamily.DATA_MONUMENT, "number_sculpture")
        self.assertIn("engineered", plan.prompt)
        self.assertIn("blank", plan.prompt)
        self.assertNotIn("rock", plan.prompt.lower())
        self.assertNotIn("mountain", plan.prompt.lower())

    def test_tactical_stays_outside_sdxl(self):
        with self.assertRaises(ValueError):
            SDXLCompactPromptCompiler.compile(EditorialSceneFamily.TACTICAL_BOARD, "topology_map")


if __name__ == "__main__":
    unittest.main()
