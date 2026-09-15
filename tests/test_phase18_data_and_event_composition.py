import unittest

from engine.intelligence.adaptive_brand_placement import BrandZone
from engine.intelligence.data_monument_composition import DataMonumentComposer
from engine.intelligence.event_editorial_composition import EventEditorialComposer
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform


class DataAndEventCompositionTests(unittest.TestCase):
    def setUp(self):
        self.profiles = PlatformProfileRegistry()

    def test_data_monument_keeps_exact_values_code_owned(self):
        plan = DataMonumentComposer().plan(self.profiles.get(SocialPlatform.INSTAGRAM_FEED))
        self.assertTrue(plan.exact_data_required)
        self.assertFalse(plan.generated_exact_values_allowed)
        self.assertFalse(plan.unnecessary_stadium_allowed)
        self.assertFalse(plan.dense_paragraph_allowed)
        self.assertEqual(plan.brand.zone, BrandZone.LOWER_RIGHT)
        self.assertFalse(plan.publication_ready)

    def test_event_editorial_forces_no_unneeded_motif(self):
        plan = EventEditorialComposer().plan(self.profiles.get(SocialPlatform.INSTAGRAM_FEED))
        self.assertTrue(plan.single_story_anchor_required)
        self.assertFalse(plan.full_pitch_required)
        self.assertFalse(plan.person_required)
        self.assertFalse(plan.decorative_stats_required)
        self.assertFalse(plan.dense_copy_allowed)
        self.assertEqual(plan.brand.zone, BrandZone.LOWER_CENTER)
        self.assertFalse(plan.publication_ready)

    def test_data_and_general_are_not_same_composition(self):
        profile = self.profiles.get(SocialPlatform.X_FEED)
        data = DataMonumentComposer().plan(profile)
        event = EventEditorialComposer().plan(profile)
        self.assertNotEqual(data.contract, event.contract)
        self.assertNotEqual(data.brand.zone, event.brand.zone)
        self.assertNotEqual(data.data_box, event.anchor_box)

    def test_both_art_direct_portrait_and_landscape(self):
        data = DataMonumentComposer()
        event = EventEditorialComposer()
        p = self.profiles.get(SocialPlatform.INSTAGRAM_FEED)
        l = self.profiles.get(SocialPlatform.X_FEED)
        self.assertNotEqual(data.plan(p).data_box, data.plan(l).data_box)
        self.assertNotEqual(event.plan(p).anchor_box, event.plan(l).anchor_box)


if __name__ == "__main__":
    unittest.main()
