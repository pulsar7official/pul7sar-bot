import unittest

from tools.phase18_flux2_t4_quantized_preview import _aligned, _preview_canvas


class T4QuantizedPreviewTests(unittest.TestCase):
    def test_alignment_is_divisible_by_16(self):
        self.assertEqual(_aligned(769) % 16, 0)
        self.assertGreaterEqual(_aligned(200), 256)

    def test_preview_canvas_preserves_orientation_and_bounds_long_edge(self):
        width, height = _preview_canvas(1080, 1350, 768)
        self.assertLess(width, height)
        self.assertLessEqual(max(width, height), 768)
        self.assertEqual(width % 16, 0)
        self.assertEqual(height % 16, 0)

    def test_invalid_canvas_fails_closed(self):
        with self.assertRaises(ValueError):
            _preview_canvas(0, 1350, 768)


if __name__ == "__main__":
    unittest.main()
