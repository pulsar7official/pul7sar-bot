import unittest
from dataclasses import replace

from engine.intelligence.dynamic_renderer_prompt import DynamicRendererPromptCompiler
from engine.intelligence.dynamic_visual_brain import DynamicVisualBrain
from engine.intelligence.dynamic_visual_brain_lock import DynamicVisualBrainConceptLock
from engine.intelligence.dynamic_visual_brain_original_scene import DynamicVisualBrainOriginalSceneBridge
from engine.intelligence.original_scene_runtime_contract import OriginalSceneRuntimeKind
from engine.intelligence.visual_concept_director import VisualConceptArchetype


class DynamicVisualBrainOriginalSceneBridgeTests(unittest.TestCase):
    def _plan_and_lock(self, story_type="preview"):
        plan = DynamicVisualBrain().plan({
            "headline": "Verified League prepares for a new season",
            "summary": "Verified sources state that Verified League is scheduled to begin this weekend.",
            "sport": "football",
            "story_type": story_type,
            "primary_entity": "Verified League",
        })
        lock = DynamicVisualBrainConceptLock.lock(plan, plan.concepts[0].concept_id)
        return plan, lock

    def test_locked_concept_becomes_renderer_safe_provider_neutral_atmosphere_request(self):
        plan, lock = self._plan_and_lock()
        request, receipt = DynamicVisualBrainOriginalSceneBridge.compile(plan=plan, lock=lock, seed=17)
        self.assertEqual(request.runtime_kind, OriginalSceneRuntimeKind.ATMOSPHERE)
        self.assertEqual(request.archetype, VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE)
        self.assertNotEqual(request.scene_intent, plan.concepts[0].scene_prompt)
        self.assertEqual(receipt.renderer_prompt_contract, DynamicRendererPromptCompiler.CONTRACT)
        self.assertEqual(len(receipt.renderer_prompt_sha256), 64)
        self.assertTrue(receipt.renderer_identity_neutral)
        folded = request.scene_intent.casefold()
        self.assertNotIn("verified league", folded)
        self.assertNotIn("pul7sar", folded)
        self.assertNotIn("pulsar", folded)
        self.assertIn("no readable text", folded)
        self.assertIn("no football pitch", folded)
        self.assertEqual(request.safe_negative_space, plan.concepts[0].negative_space_strategy)
        self.assertFalse(request.identity_reference_ids)
        self.assertIn("readable_text", request.exact_fact_roles_reserved_for_compositor)
        self.assertIn("pul7sar_brand", request.exact_fact_roles_reserved_for_compositor)
        self.assertIn("exact_score", request.exact_fact_roles_reserved_for_compositor)
        self.assertIn("club_crest", request.exact_fact_roles_reserved_for_compositor)
        self.assertIn("exact_sport_geometry", request.exact_fact_roles_reserved_for_compositor)
        self.assertTrue(receipt.semantic_inspection_required)
        self.assertFalse(receipt.provider_selected)
        self.assertFalse(receipt.generator_selected)
        self.assertFalse(receipt.identity_generation_allowed)
        self.assertFalse(receipt.exact_facts_generated)
        self.assertFalse(receipt.exact_sport_geometry_generated)
        self.assertFalse(receipt.publication_ready)

    def test_person_led_story_still_cannot_generate_identity_without_reference(self):
        plan = DynamicVisualBrain().plan({
            "headline": "Verified Player ruled out",
            "summary": "Verified Club confirmed that Verified Player will miss the next match.",
            "sport": "football",
            "story_type": "injury",
            "primary_entity": "Verified Player",
            "secondary_entities": ["Verified Club"],
        })
        lock = DynamicVisualBrainConceptLock.lock(plan, plan.concepts[0].concept_id)
        request, receipt = DynamicVisualBrainOriginalSceneBridge.compile(plan=plan, lock=lock, seed=9)
        self.assertEqual(request.runtime_kind, OriginalSceneRuntimeKind.ATMOSPHERE)
        self.assertFalse(request.identity_reference_ids)
        self.assertIn("no specific real-person depiction", request.forbidden_visual_claims)
        self.assertNotIn("verified player", request.scene_intent.casefold())
        self.assertNotIn("verified club", request.scene_intent.casefold())
        self.assertFalse(receipt.identity_generation_allowed)

    def test_result_story_keeps_exact_score_and_marks_outside_generation(self):
        plan = DynamicVisualBrain().plan({
            "headline": "Club A defeats Club B",
            "summary": "Club A won the verified match against Club B.",
            "sport": "football",
            "story_type": "result",
            "primary_entity": "Club A",
            "secondary_entities": ["Club B"],
        })
        lock = DynamicVisualBrainConceptLock.lock(plan, plan.concepts[0].concept_id)
        request, receipt = DynamicVisualBrainOriginalSceneBridge.compile(plan=plan, lock=lock, seed=3)
        reserved = set(request.exact_fact_roles_reserved_for_compositor)
        self.assertTrue({"exact_score", "club_crest", "exact_numbers", "entity_marks"}.issubset(reserved))
        self.assertIn("without readable score", request.scene_intent)
        self.assertIn("disrespect toward the losing side", request.scene_intent)
        self.assertNotIn("club a", request.scene_intent.casefold())
        self.assertNotIn("club b", request.scene_intent.casefold())
        self.assertFalse(receipt.exact_facts_generated)

    def test_competition_drift_after_lock_fails_closed(self):
        plan, lock = self._plan_and_lock()
        changed = replace(plan.concepts[1], title=plan.concepts[1].title + " drift")
        changed_plan = replace(plan, concepts=(plan.concepts[0], changed, *plan.concepts[2:]))
        with self.assertRaisesRegex(ValueError, "COMPETITION_DRIFT"):
            DynamicVisualBrainOriginalSceneBridge.compile(plan=changed_plan, lock=lock, seed=1)

    def test_selected_concept_drift_after_lock_fails_closed(self):
        plan, lock = self._plan_and_lock()
        changed = replace(plan.concepts[0], camera_language="changed camera after lock")
        changed_plan = replace(plan, concepts=(changed, *plan.concepts[1:]))
        with self.assertRaisesRegex(ValueError, "COMPETITION_DRIFT|SELECTED_CONCEPT_DRIFT"):
            DynamicVisualBrainOriginalSceneBridge.compile(plan=changed_plan, lock=lock, seed=1)

    def test_authority_drift_in_lock_fails_closed(self):
        plan, lock = self._plan_and_lock()
        unsafe = replace(lock, publication_ready=True)
        with self.assertRaisesRegex(ValueError, "AUTHORITY_DRIFT"):
            DynamicVisualBrainOriginalSceneBridge.compile(plan=plan, lock=unsafe, seed=1)

    def test_invalid_seed_is_rejected(self):
        plan, lock = self._plan_and_lock()
        with self.assertRaisesRegex(ValueError, "SEED_INVALID"):
            DynamicVisualBrainOriginalSceneBridge.compile(plan=plan, lock=lock, seed=-1)


if __name__ == "__main__":
    unittest.main()
