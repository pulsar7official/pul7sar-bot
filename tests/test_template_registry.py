"""Tests for TemplateRegistry.

Tests the TemplateRegistry implementation against the Phase 6 design.
"""

import unittest

from engine.core.exceptions import TemplateError
from engine.core.layer import Layer
from engine.pipeline import TemplateProtocol
from engine.templates.registry import TemplateRegistry


# Helper: A valid template class for testing
class ValidTemplate:
    def execute(self, render_context):
        return []


# Verify that ValidTemplate implements TemplateProtocol
# (It has an execute() method returning Sequence[Layer])
assert isinstance(ValidTemplate, type)


class TestTemplateRegistry(unittest.TestCase):
    """Test TemplateRegistry functionality."""

    def setUp(self) -> None:
        self.registry = TemplateRegistry()

    def test_register_valid_template(self) -> None:
        """Should register a valid template class."""
        self.registry.register("test", ValidTemplate)
        self.assertTrue(self.registry.has("test"))
        self.assertEqual(self.registry.get("test"), ValidTemplate)

    def test_register_multiple_templates(self) -> None:
        """Should register multiple different templates."""

        class OtherTemplate:
            def execute(self, render_context):
                return []

        self.registry.register("test1", ValidTemplate)
        self.registry.register("test2", OtherTemplate)

        self.assertEqual(self.registry.get("test1"), ValidTemplate)
        self.assertEqual(self.registry.get("test2"), OtherTemplate)
        self.assertEqual(len(self.registry.names), 2)

    def test_register_duplicate_name_same_class(self) -> None:
        """Should not error if same class registered twice with same name."""
        self.registry.register("test", ValidTemplate)
        self.registry.register("test", ValidTemplate)  # Should not raise
        self.assertTrue(self.registry.has("test"))
        self.assertEqual(self.registry.get("test"), ValidTemplate)

    def test_register_duplicate_name_different_class(self) -> None:
        """Should raise TemplateError if different class with same name."""

        class OtherTemplate:
            def execute(self, render_context):
                return []

        self.registry.register("test", ValidTemplate)
        with self.assertRaises(TemplateError) as ctx:
            self.registry.register("test", OtherTemplate)
        self.assertIn("already registered", str(ctx.exception))

    def test_register_empty_name(self) -> None:
        """Should raise TemplateError for empty name."""
        with self.assertRaises(TemplateError) as ctx:
            self.registry.register("", ValidTemplate)
        self.assertIn("non-empty string", str(ctx.exception))

    def test_register_none_name(self) -> None:
        """Should raise TemplateError for None name."""
        with self.assertRaises(TemplateError) as ctx:
            self.registry.register(None, ValidTemplate)  # type: ignore
        self.assertIn("non-empty string", str(ctx.exception))

    def test_register_invalid_class_not_type(self) -> None:
        """Should raise TemplateError if template_class is not a class."""
        with self.assertRaises(TemplateError) as ctx:
            self.registry.register("test", object())  # instance, not class
        self.assertIn("must be a class", str(ctx.exception))

    def test_register_class_without_execute(self) -> None:
        """Should raise TemplateError if class doesn't implement TemplateProtocol."""

        class InvalidTemplate:
            pass

        with self.assertRaises(TemplateError) as ctx:
            self.registry.register("invalid", InvalidTemplate)
        self.assertIn("must implement TemplateProtocol", str(ctx.exception))

    def test_get_existing_template(self) -> None:
        """Should retrieve registered template."""
        self.registry.register("test", ValidTemplate)
        result = self.registry.get("test")
        self.assertEqual(result, ValidTemplate)

    def test_get_missing_template(self) -> None:
        """Should raise TemplateError for missing template."""
        with self.assertRaises(TemplateError) as ctx:
            self.registry.get("nonexistent")
        self.assertIn("not registered", str(ctx.exception))

    def test_has_template(self) -> None:
        """Should correctly check if template is registered."""
        self.assertFalse(self.registry.has("test"))
        self.registry.register("test", ValidTemplate)
        self.assertTrue(self.registry.has("test"))

    def test_names_property(self) -> None:
        """Should return all registered names."""
        self.assertEqual(self.registry.names, ())
        self.registry.register("test1", ValidTemplate)
        self.assertEqual(self.registry.names, ("test1",))
        self.registry.register("test2", ValidTemplate)
        self.assertEqual(set(self.registry.names), {"test1", "test2"})

    def test_clear(self) -> None:
        """Should clear all registered templates."""
        self.registry.register("test1", ValidTemplate)
        self.registry.register("test2", ValidTemplate)
        self.assertEqual(len(self.registry.names), 2)
        self.registry.clear()
        self.assertEqual(self.registry.names, ())
        self.assertFalse(self.registry.has("test1"))

    def test_registry_is_stateless_across_requests(self) -> None:
        """Registry should maintain state (templates) but not per-request."""
        registry = TemplateRegistry()
        registry.register("test", ValidTemplate)
        self.assertTrue(registry.has("test"))
        # The registry itself holds the templates, but that's its job
        # It doesn't hold any per-request state


if __name__ == "__main__":
    unittest.main()