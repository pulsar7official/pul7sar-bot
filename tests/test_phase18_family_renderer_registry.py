import unittest

from engine.intelligence.family_renderer_registry import FamilyRendererRegistry, FamilyRendererStatus
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


class FamilyRendererRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = FamilyRendererRegistry()

    def test_all_six_editorial_families_have_explicit_pixel_renderers(self):
        snapshot = self.registry.snapshot()
        self.assertEqual(len(snapshot), len(EditorialSceneFamily))
        self.assertEqual({cap.family for cap in snapshot}, set(EditorialSceneFamily))
        for cap in snapshot:
            self.assertEqual(cap.status, FamilyRendererStatus.IMPLEMENTED)
            self.assertTrue(cap.renderer_module)
            self.assertTrue(cap.renderer_class)
            self.assertTrue(cap.renderer_contract)
            self.assertFalse(cap.generator_required)
            self.assertFalse(cap.network_required)
            self.assertFalse(cap.may_inherit_other_family_renderer)

    def test_no_two_families_share_the_same_renderer_class(self):
        classes = [cap.renderer_class for cap in self.registry.snapshot()]
        self.assertEqual(len(classes), len(set(classes)))

    def test_data_and_event_are_no_longer_contract_only(self):
        for family in (EditorialSceneFamily.DATA_MONUMENT, EditorialSceneFamily.EVENT_EDITORIAL):
            cap = self.registry.require_implemented(family)
            self.assertEqual(cap.status, FamilyRendererStatus.IMPLEMENTED)

    def test_event_renderer_reserves_pulse_for_brand_master(self):
        cap = self.registry.require_implemented(EditorialSceneFamily.EVENT_EDITORIAL)
        self.assertEqual(cap.renderer_module, 'engine.intelligence.event_editorial_runtime_v2')
        self.assertEqual(cap.renderer_contract, 'pul7sar-event-editorial-study-renderer-v2-no-duplicate-pulse')

    def test_registry_version_declares_event_pulse_exclusivity(self):
        self.assertEqual(self.registry.VERSION, 'pul7sar-family-renderer-registry-v3-event-pulse-exclusive')


if __name__ == '__main__':
    unittest.main()
