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

    def test_photo_led_result_concepts_are_reference_only_not_publication_routes(self):
        for archetype in (
            VisualConceptArchetype.DECISIVE_MOMENT,
            VisualConceptArchetype.CELEBRATION_MOMENT,
            VisualConceptArchetype.VERIFIED_MATCH_MOMENT,
        ):
            cap = self.registry.get(archetype)
            self.assertEqual(cap.status, ConceptRendererStatus.CONTRACT_ONLY)
            self.assertEqual(cap.surface_class, ConceptSurfaceClass.PHOTO_LED)
            self.assertTrue(cap.reference_only)
            self.assertFalse(cap.original_pixels)
            with self.assertRaisesRegex(ValueError, "VISUAL_CONCEPT_RENDERER_NOT_IMPLEMENTED"):
                self.registry.require_implemented(archetype)

    def test_score_monument_is_original_deterministic_fallback(self):
        score = self.registry.require_implemented(VisualConceptArchetype.SCORE_MONUMENT)
        self.assertEqual(score.surface_class, ConceptSurfaceClass.DETERMINISTIC_INFORMATION)
        self.assertTrue(score.original_pixels)
        self.assertFalse(score.reference_only)

    def test_identity_conditioned_hero_waits_for_qualified_runtime(self):
        hero = self.registry.get(VisualConceptArchetype.HERO_ARRIVAL)
        self.assertEqual(hero.status, ConceptRendererStatus.CONTRACT_ONLY)
        self.assertEqual(hero.surface_class, ConceptSurfaceClass.IDENTITY_CONDITIONED_GENERATIVE)
        self.assertTrue(hero.generator_required)
        self.assertTrue(hero.original_pixels)

    def test_symbolic_and_verified_detail_use_original_minimal_editorial_routes(self):
        signing = self.registry.require_implemented(VisualConceptArchetype.SYMBOLIC_SIGNING_REVEAL)
        detail = self.registry.require_implemented(VisualConceptArchetype.VERIFIED_EVIDENCE_DETAIL)
        self.assertEqual(signing.surface_class, ConceptSurfaceClass.MINIMAL_EDITORIAL)
        self.assertEqual(detail.surface_class, ConceptSurfaceClass.MINIMAL_EDITORIAL)

    def test_photographic_event_is_quarantined_while_minimal_event_is_original(self):
        photographic = self.registry.get(VisualConceptArchetype.PHOTOGRAPHIC_EVENT)
        minimal = self.registry.require_implemented(VisualConceptArchetype.MINIMAL_EVENT_SYMBOL)
        self.assertEqual(photographic.status, ConceptRendererStatus.CONTRACT_ONLY)
        self.assertTrue(photographic.reference_only)
        self.assertFalse(photographic.original_pixels)
        self.assertEqual(minimal.surface_class, ConceptSurfaceClass.MINIMAL_EDITORIAL)
        self.assertTrue(minimal.original_pixels)

    def test_local_generative_atmosphere_is_explicit_but_not_qualified(self):
        cap = self.registry.get(VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE)
        self.assertEqual(cap.status, ConceptRendererStatus.CONTRACT_ONLY)
        self.assertEqual(cap.surface_class, ConceptSurfaceClass.LOCAL_GENERATIVE_ATMOSPHERE)
        self.assertTrue(cap.generator_required)
        self.assertFalse(cap.network_required)
        self.assertEqual(cap.required_asset_roles, ("qualified_local_gpu_runtime", "semantic_inspection"))

    def test_no_concept_requires_network_and_none_authorizes_publication(self):
        for capability in self.registry.snapshot():
            self.assertFalse(capability.network_required)
            self.assertFalse(capability.publication_ready)
            if capability.status is ConceptRendererStatus.IMPLEMENTED:
                self.assertTrue(capability.original_pixels)
                self.assertFalse(capability.reference_only)


if __name__ == "__main__":
    unittest.main()
