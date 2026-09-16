import unittest

from tools.phase18_flux2_t4_direct_preview import _aligned, _preview_canvas


class T4DirectPreviewCanvasTests(unittest.TestCase):
    def test_alignment_is_multiple_of_16(self):
        self.assertEqual(_aligned(959) % 16, 0)
        self.assertGreaterEqual(_aligned(959), 256)

    def test_portrait_request_preserves_orientation_and_caps_long_edge(self):
        width, height = _preview_canvas(1080, 1350, 960)
        self.assertLess(width, height)
        self.assertLessEqual(max(width, height), 960)
        self.assertEqual(width % 16, 0)
        self.assertEqual(height % 16, 0)

    def test_landscape_request_preserves_orientation(self):
        width, height = _preview_canvas(1920, 1080, 960)
        self.assertGreater(width, height)
        self.assertEqual(width, 960)

    def test_small_request_is_not_upscaled(self):
        self.assertEqual(_preview_canvas(640, 800, 960), (640, 800))


if __name__ == "__main__":
    unittest.main()
