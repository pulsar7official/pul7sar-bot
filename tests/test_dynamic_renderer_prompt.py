import unittest

from engine.intelligence.dynamic_renderer_prompt import (
    DynamicConceptRenderSelector,
    DynamicRendererPromptCompiler,
)
from engine.intelligence.dynamic_visual_brain import DynamicVisualBrain


class DynamicRendererPromptTests(unittest.TestCase):
    def setUp(self):
        self.article = {
            "headline": "Test Midfielder completes move to Destination Club",
            "summary": "Test Midfielder has completed a permanent transfer to Destination Club after an agreement was reached between the two sides.",
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
        self.assertNotIn("PUL7SAR", prompt.upper())
        self.assertIn("NO people or human figures", prompt)
        self.assertIn("ONE continuous physical scene only", prompt)
        self.assertIn("No readable text", prompt)
        self.assertIn("No football pitch", prompt)
        self.assertIn("later deterministic headline and brand layers", prompt)

    def test_generic_story_strips_known_entities_and_platform_name(self):
        plan = DynamicVisualBrain().plan({
            "headline": "Verified League prepares for a new season",
            "summary": "PUL7SAR reports that Verified League begins this weekend.",
            "sport": "football",
            "story_type": "preview",
            "primary_entity": "Verified League",
        })
        concept = plan.concepts[0]
        decision = DynamicRendererPromptCompiler().compile(
            story=plan.story,
            event=plan.event,
            concept=concept,
            verified_person_asset=False,
        )
        folded = decision.prompt.casefold()
        self.assertNotIn("verified league", folded)
        self.assertNotIn("pul7sar", folded)
        self.assertNotIn("pulsar", folded)
        self.assertIn("specific real venue", folded)
        self.assertIn("specific real-person depiction", folded)

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
