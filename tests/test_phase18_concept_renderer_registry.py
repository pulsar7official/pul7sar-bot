import unittest

from engine.intelligence.concept_renderer_registry import (
    ConceptRendererRegistry,
    ConceptRendererStatus,
    ConceptSurfaceClass,
)
from engine.intelligence.visual_concept_director import VisualConceptArchetype


class ConceptRendererRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = ConceptRendererRegistry()

    def test_registry_covers_every_visual_concept(self):
        snapshot = self.registry.snapshot()
        self.assertEqual({entry.archetype for entry in snapshot}, set(VisualConceptArchetype))
        self.assertEqual(len(snapshot), len(VisualConceptArchetype))

    def test_result_moment_and_score_concepts_route_to_different_renderers(self):
        moment = self.registry.require_implemented(VisualConceptArchetype.DECISIVE_MOMENT)
        celebration = self.registry.require_implemented(VisualConceptArchetype.CELEBRATION_MOMENT)
        score = self.registry.require_implemented(VisualConceptArchetype.SCORE_MONUMENT)
        self.assertEqual(moment.surface_class, ConceptSurfaceClass.PHOTO_LED)
        self.assertEqual(celebration.renderer_class, 'MomentLedResultRenderer')
        self.assertEqual(moment.renderer_class, celebration.renderer_class)
        self.assertNotEqual(moment.renderer_class, score.renderer_class)
        self.assertEqual(score.surface_class, ConceptSurfaceClass.PREMIUM_HYBRID)

    def test_symbolic_transfer_and_verified_detail_are_now_explicit_photo_led_concepts(self):
        signing = self.registry.require_implemented(VisualConceptArchetype.SYMBOLIC_SIGNING_REVEAL)
        detail = self.registry.require_implemented(VisualConceptArchetype.VERIFIED_EVIDENCE_DETAIL)
        self.assertEqual(signing.surface_class, ConceptSurfaceClass.PHOTO_LED)
        self.assertEqual(detail.surface_class, ConceptSurfaceClass.PHOTO_LED)
        self.assertEqual(signing.renderer_class, 'VerifiedDetailEditorialRenderer')
        self.assertEqual(detail.renderer_class, 'VerifiedDetailEditorialRenderer')

    def test_photographic_event_and_minimal_event_are_explicit_concepts(self):
        photographic = self.registry.require_implemented(VisualConceptArchetype.PHOTOGRAPHIC_EVENT)
        minimal = self.registry.require_implemented(VisualConceptArchetype.MINIMAL_EVENT_SYMBOL)
        self.assertEqual(photographic.surface_class, ConceptSurfaceClass.PHOTO_LED)
        self.assertEqual(minimal.surface_class, ConceptSurfaceClass.MINIMAL_EDITORIAL)

    def test_only_unqualified_local_generative_concept_remains_contract_only(self):
        for archetype in VisualConceptArchetype:
            cap = self.registry.get(archetype)
            if archetype is VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE:
                self.assertEqual(cap.status, ConceptRendererStatus.CONTRACT_ONLY)
                with self.assertRaisesRegex(ValueError, 'VISUAL_CONCEPT_RENDERER_NOT_IMPLEMENTED'):
                    self.registry.require_implemented(archetype)
            else:
                self.assertEqual(cap.status, ConceptRendererStatus.IMPLEMENTED)
                self.assertIs(self.registry.require_implemented(archetype), cap)

    def test_local_generative_atmosphere_is_explicit_but_not_qualified(self):
        cap = self.registry.get(VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE)
        self.assertEqual(cap.surface_class, ConceptSurfaceClass.LOCAL_GENERATIVE_ATMOSPHERE)
        self.assertTrue(cap.generator_required)
        self.assertFalse(cap.network_required)
        self.assertEqual(cap.required_asset_roles, ('qualified_local_gpu_runtime', 'semantic_inspection'))

    def test_no_concept_requires_network_and_none_authorizes_publication(self):
        for capability in self.registry.snapshot():
            self.assertFalse(capability.network_required)
            self.assertFalse(capability.publication_ready)


if __name__ == '__main__':
    unittest.main()
