"""Phase 15 integration tests for the Visual Engine bridge."""

import copy
import unittest
from io import BytesIO
from unittest.mock import Mock

from PIL import Image

from engine.bootstrap import create_engine
from engine.entities.model import EntityContext
from engine.integration.article_adapter import render_article_with_engine


class TestVisualEngineArticleAdapter(unittest.TestCase):
    def _image(self):
        return Image.new("RGB", (900, 600), (40, 90, 130))

    def test_real_adapter_returns_valid_jpeg_bytes(self) -> None:
        engine = create_engine()
        article = {"title": "اختبار خبر رياضي", "summary": "Test summary"}
        original = copy.deepcopy(article)
        source = self._image()
        source_before = source.tobytes()

        result = render_article_with_engine(
            article,
            engine=engine,
            selected_image=source,
            entity="chelsea",
        )

        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)
        self.assertEqual(article, original)
        self.assertEqual(source.tobytes(), source_before)

        decoded = Image.open(BytesIO(result))
        self.assertEqual(decoded.format, "JPEG")
        self.assertEqual(decoded.size, (1280, 720))
        self.assertEqual(decoded.mode, "RGB")

    def test_engine_instance_is_reusable_without_canvas_leak(self) -> None:
        engine = create_engine()
        source = self._image()

        first = render_article_with_engine(
            {"title": "خبر أول"}, engine=engine, selected_image=source, entity="chelsea"
        )
        second = render_article_with_engine(
            {"title": "خبر ثان"}, engine=engine, selected_image=source, entity="liverpool"
        )

        self.assertEqual(Image.open(BytesIO(first)).size, (1280, 720))
        self.assertEqual(Image.open(BytesIO(second)).size, (1280, 720))
        self.assertNotEqual(first, second)

    def test_article_is_not_mutated(self) -> None:
        engine = create_engine()
        article = {
            "title": "Immutable",
            "summary": "Original",
            "nested": {"value": 1},
        }
        original = copy.deepcopy(article)

        render_article_with_engine(
            article,
            engine=engine,
            selected_image=self._image(),
        )
        self.assertEqual(article, original)

    def test_adapter_accepts_entity_context(self):
        engine = Mock()
        engine.execute.return_value = b"x"
        entity = EntityContext(key="chelsea", kind="club", display_name="Chelsea")
        render_article_with_engine({"title": "X"}, engine=engine, entity=entity)
        request = engine.execute.call_args.args[0]
        self.assertEqual(request["entity"]["key"], "chelsea")
        self.assertNotIn("entity", request["content"])

    def test_adapter_normalizes_entity_string(self):
        engine = Mock()
        engine.execute.return_value = b"x"
        render_article_with_engine({"title": "X"}, engine=engine, entity="Chelsea FC")
        request = engine.execute.call_args.args[0]
        self.assertEqual(request["entity"]["key"], "chelsea")

    def test_adapter_rejects_non_bytes_engine_result(self) -> None:
        engine = Mock()
        engine.execute.return_value = "not-bytes"
        with self.assertRaises(TypeError):
            render_article_with_engine({"title": "X"}, engine=engine)

    def test_adapter_rejects_empty_engine_result(self) -> None:
        engine = Mock()
        engine.execute.return_value = b""
        with self.assertRaises(ValueError):
            render_article_with_engine({"title": "X"}, engine=engine)

    def test_adapter_does_not_accept_short_post(self) -> None:
        engine = Mock()
        engine.execute.return_value = b"x"
        with self.assertRaises(TypeError):
            render_article_with_engine(
                {"title": "X"}, engine=engine, short_post="unused"
            )


if __name__ == "__main__":
    unittest.main()
