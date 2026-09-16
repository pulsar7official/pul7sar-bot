import unittest
from dataclasses import replace

from engine.intelligence.dynamic_visual_brain import DynamicVisualBrain
from engine.intelligence.dynamic_visual_brain_lock import (
    DynamicVisualBrainConceptLock,
    candidate_sha256,
    competition_sha256,
)


class DynamicVisualBrainConceptLockTests(unittest.TestCase):
    def _plan(self):
        return DynamicVisualBrain().plan({
            "headline": "League prepares for a new season",
            "summary": "The verified league season is scheduled to begin this weekend.",
            "sport": "football",
            "story_type": "preview",
            "primary_entity": "Verified League",
        })

    def test_explicit_concept_lock_is_deterministic_and_non_authoritative(self):
        plan = self._plan()
        selected = plan.concepts[0]
        first = DynamicVisualBrainConceptLock.lock(plan, selected.concept_id)
        second = DynamicVisualBrainConceptLock.lock(plan, selected.concept_id)
        self.assertEqual(first, second)
        self.assertEqual(first.status, "DYNAMIC_VISUAL_BRAIN_CONCEPT_LOCKED")
        self.assertEqual(first.story_fingerprint, plan.story_fingerprint)
        self.assertEqual(first.competition_sha256, competition_sha256(plan))
        self.assertEqual(first.selected_concept_sha256, candidate_sha256(selected))
        self.assertTrue(first.selection_locked_before_rendering)
        self.assertFalse(first.generation_authorized)
        self.assertFalse(first.human_visual_review_approved)
        self.assertFalse(first.golden_quality_approved)
        self.assertFalse(first.publication_ready)
        self.assertFalse(first.seeds_2_to_4_authorized)

    def test_competition_hash_changes_if_an_unselected_alternative_changes(self):
        plan = self._plan()
        original_hash = competition_sha256(plan)
        changed_alt = replace(plan.concepts[1], title=plan.concepts[1].title + " altered")
        changed_plan = replace(plan, concepts=(plan.concepts[0], changed_alt, *plan.concepts[2:]))
        self.assertNotEqual(original_hash, competition_sha256(changed_plan))

    def test_story_change_changes_story_and_competition_binding(self):
        first = self._plan()
        second = DynamicVisualBrain().plan({
            "headline": "League delays the new season",
            "summary": "The verified league season has been delayed by one week.",
            "sport": "football",
            "story_type": "schedule",
            "primary_entity": "Verified League",
        })
        self.assertNotEqual(first.story_fingerprint, second.story_fingerprint)
        self.assertNotEqual(competition_sha256(first), competition_sha256(second))

    def test_missing_or_ambiguous_concept_cannot_be_locked(self):
        plan = self._plan()
        with self.assertRaisesRegex(ValueError, "CONCEPT_NOT_UNIQUE_OR_MISSING"):
            DynamicVisualBrainConceptLock.lock(plan, "does-not-exist")
        duplicate = replace(plan, concepts=(plan.concepts[0], plan.concepts[0], plan.concepts[2]))
        with self.assertRaisesRegex(ValueError, "CONCEPT_NOT_UNIQUE_OR_MISSING"):
            DynamicVisualBrainConceptLock.lock(duplicate, plan.concepts[0].concept_id)

    def test_platform_name_leak_fails_closed(self):
        plan = self._plan()
        contaminated = replace(plan.concepts[0], scene_prompt="Render PUL7SAR branding inside the image")
        contaminated_plan = replace(plan, concepts=(contaminated, *plan.concepts[1:]))
        with self.assertRaisesRegex(ValueError, "PLATFORM_NAME_LEAK"):
            DynamicVisualBrainConceptLock.lock(contaminated_plan, contaminated.concept_id)

    def test_required_safety_markers_cannot_disappear(self):
        plan = self._plan()
        unsafe = replace(plan.concepts[0], forbidden_elements=("collage",))
        unsafe_plan = replace(plan, concepts=(unsafe, *plan.concepts[1:]))
        with self.assertRaisesRegex(ValueError, "SAFETY_MARKERS_MISSING"):
            DynamicVisualBrainConceptLock.lock(unsafe_plan, unsafe.concept_id)

    def test_provider_or_publication_authority_drift_is_rejected(self):
        plan = self._plan()
        provider_bound = replace(plan.concepts[0], metadata={"dynamic": True, "provider_agnostic": False, "publication_ready": False})
        with self.assertRaisesRegex(ValueError, "MUST_BE_PROVIDER_AGNOSTIC"):
            DynamicVisualBrainConceptLock.lock(replace(plan, concepts=(provider_bound, *plan.concepts[1:])), provider_bound.concept_id)

        publishing = replace(plan.concepts[0], metadata={"dynamic": True, "provider_agnostic": True, "publication_ready": True})
        with self.assertRaisesRegex(ValueError, "CANNOT_AUTHORIZE_PUBLICATION"):
            DynamicVisualBrainConceptLock.lock(replace(plan, concepts=(publishing, *plan.concepts[1:])), publishing.concept_id)


if __name__ == "__main__":
    unittest.main()
