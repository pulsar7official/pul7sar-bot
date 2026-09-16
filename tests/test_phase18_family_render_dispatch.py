import unittest

from engine.intelligence.family_render_dispatch import FamilyRenderDispatcher
from engine.intelligence.family_renderer_registry import FamilyRendererStatus
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.story_visual_editorial import EditorialEvent


class FamilyRenderDispatcherTests(unittest.TestCase):
    def setUp(self):
        self.dispatch = FamilyRenderDispatcher()

    def test_representative_event_for_each_family_resolves_real_renderer(self):
        expected = {
            EditorialEvent.TRANSFER_CONFIRMED: EditorialSceneFamily.TRANSFER_SIGNATURE,
            EditorialEvent.RESULT: EditorialSceneFamily.RESULT_STATEMENT,
            EditorialEvent.INJURY: EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
            EditorialEvent.TACTICS: EditorialSceneFamily.TACTICAL_BOARD,
            EditorialEvent.TABLE: EditorialSceneFamily.DATA_MONUMENT,
        }
        for event, family in expected.items():
            decision = self.dispatch.resolve(event)
            self.assertEqual(decision.family, family)
            self.assertEqual(decision.capability.status, FamilyRendererStatus.IMPLEMENTED)
            self.assertIsInstance(decision.renderer_class, type)
            self.assertFalse(decision.fallback_used)

    def test_all_editorial_events_resolve_without_cross_family_fallback(self):
        for event in EditorialEvent:
            decision = self.dispatch.resolve(event)
            self.assertFalse(decision.fallback_used)
            self.assertEqual(decision.capability.family, decision.family)
            self.assertEqual(decision.capability.status, FamilyRendererStatus.IMPLEMENTED)

    def test_event_mapping_matches_scene_director_contract(self):
        self.assertEqual(self.dispatch.family_for_event(EditorialEvent.DRAW), EditorialSceneFamily.DATA_MONUMENT)
        self.assertEqual(self.dispatch.family_for_event(EditorialEvent.SCHEDULE), EditorialSceneFamily.DATA_MONUMENT)
        self.assertEqual(self.dispatch.family_for_event(EditorialEvent.STATEMENT), EditorialSceneFamily.VERIFIED_SUBJECT_NEWS)
        self.assertEqual(self.dispatch.family_for_event(EditorialEvent.LIVE_MOMENT), EditorialSceneFamily.RESULT_STATEMENT)

    def test_non_event_fails_closed(self):
        with self.assertRaises(TypeError):
            self.dispatch.resolve('result')


if __name__ == '__main__':
    unittest.main()
