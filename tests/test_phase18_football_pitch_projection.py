import unittest

from engine.intelligence.football_pitch_projection import FootballPitchProjectionPlanner, PerspectiveProjector


class FootballPitchProjectionTests(unittest.TestCase):
    def test_projector_maps_source_corners_exactly(self):
        source = ((0.0, 0.0), (10.0, 0.0), (10.0, 5.0), (0.0, 5.0))
        dest = ((100.0, 50.0), (500.0, 80.0), (450.0, 400.0), (140.0, 420.0))
        projector = PerspectiveProjector.from_quadrilateral(source=source, destination=dest)
        for s, d in zip(source, dest):
            px, py = projector.project(s)
            self.assertAlmostEqual(px, d[0], places=6)
            self.assertAlmostEqual(py, d[1], places=6)

    def test_pitch_projection_contains_core_regulation_markings(self):
        planner = FootballPitchProjectionPlanner()
        projected = planner.project_all_markings(((120, 180), (920, 210), (1040, 1120), (40, 1100)))
        roles = [item.role for item in projected.polylines]
        point_roles = [item.role for item in projected.points]
        self.assertEqual(roles.count("halfway_line"), 1)
        self.assertEqual(roles.count("centre_circle"), 1)
        self.assertEqual(roles.count("penalty_area_left"), 1)
        self.assertEqual(roles.count("penalty_area_right"), 1)
        self.assertEqual(roles.count("penalty_arc_left"), 1)
        self.assertEqual(roles.count("penalty_arc_right"), 1)
        self.assertEqual(sum(role.startswith("corner_arc_") for role in roles), 4)
        self.assertEqual(point_roles.count("centre_mark"), 1)
        self.assertEqual(point_roles.count("penalty_mark_left"), 1)
        self.assertEqual(point_roles.count("penalty_mark_right"), 1)

    def test_projected_circle_is_closed_and_sampled(self):
        planner = FootballPitchProjectionPlanner()
        markings = planner.project_markings(((0, 0), (1000, 0), (900, 1000), (100, 1000)), circle_samples=48)
        circle = next(item for item in markings if item.role == "centre_circle")
        self.assertTrue(circle.closed)
        self.assertEqual(len(circle.points), 49)
        self.assertAlmostEqual(circle.points[0][0], circle.points[-1][0], places=6)
        self.assertAlmostEqual(circle.points[0][1], circle.points[-1][1], places=6)

    def test_penalty_and_corner_arcs_remain_open_polylines(self):
        planner = FootballPitchProjectionPlanner()
        projected = planner.project_all_markings(((100, 120), (900, 150), (1000, 1100), (20, 1080)), arc_samples=24)
        arcs = [item for item in projected.polylines if "_arc_" in item.role]
        self.assertEqual(len(arcs), 6)
        self.assertTrue(all(not item.closed for item in arcs))
        self.assertTrue(all(len(item.points) == 24 for item in arcs))

    def test_degenerate_projection_is_rejected(self):
        source = ((0.0, 0.0), (10.0, 0.0), (10.0, 5.0), (0.0, 5.0))
        dest = ((0.0, 0.0), (100.0, 0.0), (200.0, 0.0), (300.0, 0.0))
        with self.assertRaises(ValueError):
            PerspectiveProjector.from_quadrilateral(source=source, destination=dest)


if __name__ == "__main__":
    unittest.main()
