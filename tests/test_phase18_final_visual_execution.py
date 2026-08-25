import unittest

from engine.intelligence.concept_renderer_registry import ConceptRendererRegistry
from engine.intelligence.final_visual_execution import FinalVisualExecutionGate
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.visual_concept_director import VisualConceptArchetype


class FinalVisualExecutionTests(unittest.TestCase):
    def setUp(self):
        self.orchestrator = StoryToVisualOrchestrator()
        self.registry = ConceptRendererRegistry()
        self.gate = FinalVisualExecutionGate()

    def _story(self, *, event=EditorialEvent.RESULT, metadata=None):
        return VerifiedEditorialStory(
            event=event,
            sport='football',
            subject='Verified Subject',
            fact_phrase='verified fact',
            story_core='verified story core',
            tone=HeadlineTone.NEUTRAL,
            confidence=0.99,
            metadata=metadata or {},
        )

    def test_implemented_score_concept_is_admitted_locally(self):
        decision = self.orchestrator.decide(self._story())
        capability = self.registry.get(decision.visual_concept.archetype)
        final = self.gate.resolve(capability=capability, lower_level_route=decision.execution_route)
        self.assertEqual(decision.visual_concept.archetype, VisualConceptArchetype.SCORE_MONUMENT)
        self.assertTrue(final.execution_allowed)
        self.assertTrue(final.renderer_execution_allowed)
        self.assertFalse(final.provider_selection_allowed)
        self.assertFalse(final.generator_execution_allowed)

    def test_unqualified_generative_event_is_blocked_even_if_lower_route_allows_provider(self):
        decision = self.orchestrator.decide(self._story(event=EditorialEvent.PREVIEW))
        capability = self.registry.get(decision.visual_concept.archetype)
        self.assertEqual(decision.visual_concept.archetype, VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE)
        self.assertTrue(decision.execution_route.provider_selection_allowed)
        final = self.gate.resolve(capability=capability, lower_level_route=decision.execution_route)
        self.assertFalse(final.execution_allowed)
        self.assertFalse(final.renderer_execution_allowed)
        self.assertFalse(final.provider_selection_allowed)
        self.assertFalse(final.generator_execution_allowed)
        self.assertIn('cannot override concept readiness', final.reason)

    def test_contract_only_transfer_symbol_does_not_fall_back_to_family_renderer(self):
        decision = self.orchestrator.decide(self._story(event=EditorialEvent.TRANSFER_CONFIRMED))
        capability = self.registry.get(decision.visual_concept.archetype)
        self.assertEqual(decision.visual_concept.archetype, VisualConceptArchetype.SYMBOLIC_SIGNING_REVEAL)
        final = self.gate.resolve(capability=capability, lower_level_route=decision.execution_route)
        self.assertFalse(final.execution_allowed)
        self.assertFalse(final.provider_selection_allowed)

    def test_verified_decisive_moment_uses_admitted_photo_led_renderer(self):
        decision = self.orchestrator.decide(self._story(metadata={
            'verified_action_photo': True,
            'decisive_moment_known': True,
            'exact_club_assets': True,
        }))
        capability = self.registry.get(decision.visual_concept.archetype)
        self.assertEqual(decision.visual_concept.archetype, VisualConceptArchetype.DECISIVE_MOMENT)
        final = self.gate.resolve(capability=capability, lower_level_route=decision.execution_route)
        self.assertTrue(final.execution_allowed)
        self.assertTrue(final.renderer_execution_allowed)
        self.assertFalse(final.provider_selection_allowed)


if __name__ == '__main__':
    unittest.main()
