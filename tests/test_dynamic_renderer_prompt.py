import unittest

from engine.intelligence.dynamic_renderer_prompt import (
    DynamicConceptRenderSelector,
    DynamicRendererPromptCompiler,
)
from engine.intelligence.dynamic_visual_brain import DynamicVisualBrain


class DynamicRendererPromptTests(unittest.TestCase):
    def setUp(self):
        self.article = {
            "headline": "Midfielder completes move to a new club",
            "summary": "A midfielder has completed a permanent transfer to a new club after an agreement was reached between the two sides.",
            "sport": "football",
            "story_type": "transfer_confirmed",
            "primary_entity": "Test Midfielder",
            "secondary_entities": ["Destination Club"],
            "event_status": "confirmed",
        }
        self.plan = DynamicVisualBrain().plan(self.article)

    def test_selector_penalizes_split_screen_prone_transfer_concept(self):
        selected = DynamicConceptRenderSelector().choose(self.plan.concepts)
        self.assertEqual(selected.concept_id, "dynamic-transfer-threshold")

    def test_unverified_person_prompt_has_no_entity_names_and_forbids_people(self):
        concept = next(c for c in self.plan.concepts if c.concept_id == "dynamic-transfer-threshold")
        decision = DynamicRendererPromptCompiler().compile(
            story=self.plan.story,
            event=self.plan.event,
            concept=concept,
            verified_person_asset=False,
        )
        prompt = decision.prompt
        self.assertNotIn("Test Midfielder", prompt)
        self.assertNotIn("Destination Club", prompt)
        self.assertIn("NO people or human figures", prompt)
        self.assertIn("ONE continuous physical scene only", prompt)
        self.assertIn("No readable text", prompt)
        self.assertIn("No football pitch", prompt)

    def test_two_worlds_is_normalized_to_one_spatial_transition(self):
        concept = next(c for c in self.plan.concepts if c.concept_id == "dynamic-transfer-two-worlds")
        decision = DynamicRendererPromptCompiler().compile(
            story=self.plan.story,
            event=self.plan.event,
            concept=concept,
            verified_person_asset=False,
        )
        self.assertIn("one uninterrupted floor plane", decision.prompt)
        self.assertIn("no central divider", decision.prompt)
        self.assertEqual(decision.renderer_risk, "multi-zone-concept-normalized-to-single-scene")


if __name__ == "__main__":
    unittest.main()
