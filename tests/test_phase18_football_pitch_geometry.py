import unittest

from engine.intelligence.football_pitch_geometry import FootballPitchGeometry


class FootballPitchGeometryTests(unittest.TestCase):
    def setUp(self):
        self.pitch = FootballPitchGeometry()

    def test_default_pitch_uses_regulation_reference_dimensions(self):
        self.assertEqual(self.pitch.length_m, 105.0)
        self.assertEqual(self.pitch.width_m, 68.0)
        self.assertGreater(self.pitch.aspect_ratio, 1.5)
        self.assertLess(self.pitch.aspect_ratio, 1.6)

    def test_exactly_one_halfway_line_and_centre_circle(self):
        receipt = self.pitch.integrity_receipt()
        self.assertEqual(receipt["halfway_line_count"], 1)
        self.assertEqual(receipt["centre_circle_count"], 1)

    def test_two_penalty_and_goal_areas_are_symmetric(self):
        receipt = self.pitch.integrity_receipt()
        self.assertEqual(receipt["penalty_area_count"], 2)
        self.assertEqual(receipt["goal_area_count"], 2)
        self.assertTrue(receipt["symmetric_penalty_areas"])

    def test_penalty_marks_are_eleven_metres_from_goal_lines(self):
        left, right = self.pitch.penalty_marks()
        self.assertEqual(left[0], 11.0)
        self.assertEqual(self.pitch.length_m - right[0], 11.0)
        self.assertEqual(left[1], self.pitch.width_m / 2.0)
        self.assertEqual(right[1], self.pitch.width_m / 2.0)

    def test_normalized_geometry_preserves_pitch_bounds(self):
        self.assertEqual(self.pitch.normalized_point(0, 0), (0.0, 0.0))
        self.assertEqual(self.pitch.normalized_point(105, 68), (1.0, 1.0))
        with self.assertRaises(ValueError):
            self.pitch.normalized_point(106, 20)


if __name__ == "__main__":
    unittest.main()
