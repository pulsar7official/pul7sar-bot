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

    def test_exactly_one_halfway_line_centre_circle_and_centre_mark(self):
        receipt = self.pitch.integrity_receipt()
        self.assertEqual(receipt["halfway_line_count"], 1)
        self.assertEqual(receipt["centre_circle_count"], 1)
        self.assertEqual(receipt["centre_mark_count"], 1)

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
        self.assertEqual(self.pitch.integrity_receipt()["penalty_mark_count"], 2)

    def test_penalty_and_corner_arcs_are_present(self):
        receipt = self.pitch.integrity_receipt()
        self.assertEqual(receipt["penalty_arc_count"], 2)
        self.assertEqual(receipt["corner_arc_count"], 4)
        roles = {arc.role for arc in self.pitch.arcs()}
        self.assertIn("penalty_arc_left", roles)
        self.assertIn("penalty_arc_right", roles)
        self.assertIn("corner_arc_top_left", roles)
        self.assertIn("corner_arc_bottom_right", roles)

    def test_penalty_arcs_cross_penalty_area_boundary_from_correct_side(self):
        left = next(arc for arc in self.pitch.arcs() if arc.role == "penalty_arc_left")
        right = next(arc for arc in self.pitch.arcs() if arc.role == "penalty_arc_right")
        self.assertLess(left.start_degrees, 0)
        self.assertGreater(left.end_degrees, 0)
        self.assertGreater(right.start_degrees, 90)
        self.assertLess(right.end_degrees, 270)

    def test_normalized_geometry_preserves_pitch_bounds(self):
        self.assertEqual(self.pitch.normalized_point(0, 0), (0.0, 0.0))
        self.assertEqual(self.pitch.normalized_point(105, 68), (1.0, 1.0))
        with self.assertRaises(ValueError):
            self.pitch.normalized_point(106, 20)


if __name__ == "__main__":
    unittest.main()
