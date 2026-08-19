import unittest
from dataclasses import FrozenInstanceError

from engine.core.content import RenderContent


class TestRenderContent(unittest.TestCase):
    def test_valid_arabic(self):
        RenderContent(headline="ريال مدريد يفوز")

    def test_valid_english(self):
        RenderContent(headline="Real Madrid wins")

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            RenderContent(headline="")

    def test_whitespace_rejected(self):
        for value in ("   ", "\t\n"):
            with self.assertRaises(ValueError):
                RenderContent(headline=value)

    def test_non_string_rejected(self):
        for value in (None, 123):
            with self.assertRaises(TypeError):
                RenderContent(headline=value)  # type: ignore[arg-type]

    def test_frozen(self):
        content = RenderContent(headline="Test")
        with self.assertRaises(FrozenInstanceError):
            content.headline = "Changed"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
