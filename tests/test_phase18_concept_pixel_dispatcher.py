import unittest

from engine.intelligence.concept_pixel_dispatcher import ConceptPixelDispatcher
from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.visual_concept_director import VisualConceptArchetype


class ConceptPixelDispatcherTests(unittest.TestCase):
    def setUp(self):
        self.orchestrator = StoryToVisualOrchestrator()
        self.dispatcher = ConceptPixelDispatcher()

    def story(self, event=EditorialEvent.RESULT, **kwargs):
        data = dict(
            event=event,
            sport='football',
            subject='Verified Subject',
            fact_phrase='verified fact',
            story_core='verified story core',
            tone=HeadlineTone.NEUTRAL,
            confidence=0.99,
        )
        data.update(kwargs)
        return VerifiedEditorialStory(**data)

    def test_score_and_decisive_moment_bind_different_pixel_implementations(self):
        score = self.orchestrator.decide(self.story())
        moment = self.orchestrator.decide(self.story(metadata={
            'verified_action_photo': True,
            'decisive_moment_known': True,
            'exact_club_assets': True,
        }))
        score_binding = self.dispatcher.bind(
            archetype=score.visual_concept.archetype,
            lower_level_route=score.execution_route,
        )
        moment_binding = self.dispatcher.bind(
            archetype=moment.visual_concept.archetype,
            lower_level_route=moment.execution_route,
        )
        self.assertEqual(score_binding.archetype, VisualConceptArchetype.SCORE_MONUMENT)
        self.assertEqual(moment_binding.archetype, VisualConceptArchetype.DECISIVE_MOMENT)
        self.assertNotEqual(score_binding.renderer_module, moment_binding.renderer_module)
        self.assertNotEqual(score_binding.renderer_class, moment_binding.renderer_class)

    def test_symbolic_transfer_now_binds_verified_detail_renderer_not_transfer_fallback(self):
        decision = self.orchestrator.decide(self.story(event=EditorialEvent.TRANSFER_CONFIRMED))
        self.assertEqual(decision.visual_concept.archetype, VisualConceptArchetype.SYMBOLIC_SIGNING_REVEAL)
        binding = self.dispatcher.bind(
            archetype=decision.visual_concept.archetype,
            lower_level_route=decision.execution_route,
        )
        self.assertEqual(binding.renderer_class, 'VerifiedDetailEditorialRenderer')
        self.assertNotIn('editorial_reference_scene', binding.renderer_module)

    def test_unqualified_local_generative_event_cannot_bind_any_renderer(self):
        decision = self.orchestrator.decide(self.story(event=EditorialEvent.PREVIEW))
        self.assertEqual(decision.visual_concept.archetype, VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE)
        with self.assertRaisesRegex(ValueError, 'VISUAL_CONCEPT_PIXEL_DISPATCH_BLOCKED'):
            self.dispatcher.bind(
                archetype=decision.visual_concept.archetype,
                lower_level_route=decision.execution_route,
            )

    def test_registered_renderer_class_is_importable(self):
        decision = self.orchestrator.decide(self.story(metadata={
            'verified_action_photo': True,
            'decisive_moment_known': True,
            'exact_club_assets': True,
        }))
        binding = self.dispatcher.bind(
            archetype=decision.visual_concept.archetype,
            lower_level_route=decision.execution_route,
        )
        self.assertTrue(isinstance(binding.renderer_type, type))
        self.assertTrue(binding.final_execution.execution_allowed)
        self.assertFalse(binding.final_execution.provider_selection_allowed)


if __name__ == '__main__':
    unittest.main()
