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

    def test_score_monument_binds_deterministic_original_pixel_implementation(self):
        score = self.orchestrator.decide(self.story())
        binding = self.dispatcher.bind(
            archetype=score.visual_concept.archetype,
            lower_level_route=score.execution_route,
        )
        self.assertEqual(binding.archetype, VisualConceptArchetype.SCORE_MONUMENT)
        self.assertEqual(binding.renderer_class, 'ResultStatementStudyRenderer')
        self.assertTrue(binding.final_execution.execution_allowed)
        self.assertFalse(binding.final_execution.generator_execution_allowed)

    def test_verified_match_photo_does_not_create_photo_publication_binding(self):
        decision = self.orchestrator.decide(self.story(metadata={
            'verified_action_photo': True,
            'decisive_moment_known': True,
            'exact_club_assets': True,
        }))
        # Without explicit original-scene generation, the verified photograph is
        # reference evidence only and the final pixel route remains deterministic.
        self.assertEqual(decision.visual_concept.archetype, VisualConceptArchetype.SCORE_MONUMENT)
        binding = self.dispatcher.bind(
            archetype=decision.visual_concept.archetype,
            lower_level_route=decision.execution_route,
        )
        self.assertNotIn('moment_led_result_renderer', binding.renderer_module)

    def test_symbolic_transfer_binds_verified_detail_renderer_not_transfer_fallback(self):
        decision = self.orchestrator.decide(self.story(event=EditorialEvent.TRANSFER_CONFIRMED))
        self.assertEqual(decision.visual_concept.archetype, VisualConceptArchetype.SYMBOLIC_SIGNING_REVEAL)
        binding = self.dispatcher.bind(
            archetype=decision.visual_concept.archetype,
            lower_level_route=decision.execution_route,
        )
        self.assertEqual(binding.renderer_class, 'VerifiedDetailEditorialRenderer')
        self.assertNotIn('editorial_reference_scene', binding.renderer_module)

    def test_unqualified_original_scene_generation_cannot_bind_legacy_renderer(self):
        decision = self.orchestrator.decide(self.story(
            metadata={
                'allow_original_scene_generation': True,
                'verified_action_photo': True,
                'decisive_moment_known': True,
                'exact_club_assets': True,
            }
        ))
        self.assertEqual(decision.visual_concept.archetype, VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE)
        with self.assertRaisesRegex(ValueError, 'VISUAL_CONCEPT_PIXEL_DISPATCH_BLOCKED'):
            self.dispatcher.bind(
                archetype=decision.visual_concept.archetype,
                lower_level_route=decision.execution_route,
            )

    def test_registered_deterministic_renderer_class_is_importable(self):
        decision = self.orchestrator.decide(self.story())
        binding = self.dispatcher.bind(
            archetype=decision.visual_concept.archetype,
            lower_level_route=decision.execution_route,
        )
        self.assertTrue(isinstance(binding.renderer_type, type))
        self.assertTrue(binding.final_execution.execution_allowed)
        self.assertFalse(binding.final_execution.provider_selection_allowed)


if __name__ == '__main__':
    unittest.main()
