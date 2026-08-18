"""Phase 13 integration tests for the Visual Engine bridge."""

import unittest
from io import BytesIO
from unittest.mock import Mock

from PIL import Image

from engine.bootstrap import create_engine
from engine.integration.article_adapter import render_article_with_engine


class TestVisualEngineArticleAdapter(unittest.TestCase):
    def test_real_adapter_returns_valid_jpeg_bytes(self) -> None:
        engine = create_engine()
        article = {"title": "Test", "summary": "Test summary"}
        original = dict(article)

        result = render_article_with_engine(article, engine=engine)

        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)
        self.assertEqual(article, original)

        decoded = Image.open(BytesIO(result))
        self.assertEqual(decoded.format, "JPEG")
        self.assertEqual(decoded.size, (1280, 720))
        self.assertEqual(decoded.mode, "RGB")

    def test_engine_instance_is_reusable_without_canvas_leak(self) -> None:
        engine = create_engine()

        first = render_article_with_engine({"title": "One"}, engine=engine)
        second = render_article_with_engine({"title": "Two"}, engine=engine)

        first_image = Image.open(BytesIO(first))
        second_image = Image.open(BytesIO(second))

        self.assertEqual(first_image.size, (1280, 720))
        self.assertEqual(second_image.size, (1280, 720))
        self.assertEqual(first_image.format, "JPEG")
        self.assertEqual(second_image.format, "JPEG")

    def test_article_is_not_mutated(self) -> None:
        engine = create_engine()
        article = {
            "title": "Immutable",
            "summary": "Original",
            "nested": {"value": 1},
        }
        original = {
            "title": "Immutable",
            "summary": "Original",
            "nested": {"value": 1},
        }

        render_article_with_engine(article, engine=engine)

        self.assertEqual(article, original)

    def test_adapter_rejects_non_bytes_engine_result(self) -> None:
        engine = Mock()
        engine.execute.return_value = "not-bytes"

        with self.assertRaises(TypeError):
            render_article_with_engine({}, engine=engine)

    def test_adapter_rejects_empty_engine_result(self) -> None:
        engine = Mock()
        engine.execute.return_value = b""

        with self.assertRaises(ValueError):
            render_article_with_engine({}, engine=engine)

    def test_adapter_does_not_accept_short_post(self) -> None:
        engine = Mock()
        engine.execute.return_value = b"x"

        with self.assertRaises(TypeError):
            render_article_with_engine({}, engine=engine, short_post="unused")


if __name__ == "__main__":
    unittest.main()
