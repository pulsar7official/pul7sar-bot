import unittest
from PIL import Image

from engine.visual.image_utils import cover_image


class TestCoverImage(unittest.TestCase):
    def test_ratios_and_immutability(self):
        for size in ((1280, 720), (640, 480), (500, 500), (400, 600)):
            source = Image.new("RGB", size, (100, 150, 200))
            before = source.tobytes()
            result = cover_image(source, 1280, 720)
            self.assertEqual(result.size, (1280, 720))
            self.assertEqual(source.size, size)
            self.assertEqual(source.tobytes(), before)


if __name__ == "__main__":
    unittest.main()
