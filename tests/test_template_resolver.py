"""Tests for TemplateResolver.

Tests the TemplateResolver implementation against the Phase 6 design.
"""

import unittest

from engine.configuration.resolver import ResolvedConfiguration
from engine.core.exceptions import TemplateError
from engine.pipeline import TemplateProtocol
from engine.templates.registry import TemplateRegistry
from engine.templates.resolver import TemplateResolver
from engine.validation.validator import ValidatedPayload


# Helper: A valid template class for testing
class DefaultTemplate:
    def execute(self, render_context):
        return []


class PayloadTemplate:
    def execute(self, render_context):
        return []


class ConfigTemplate:
    def execute(self, render_context):
        return []


class TestTemplateResolver(unittest.TestCase):
    """Test TemplateResolver functionality."""

    def setUp(self) -> None:
        self.registry = TemplateRegistry()
        self.registry.register("default", DefaultTemplate)
        self.registry.register("payload", PayloadTemplate)
        self.registry.register("config", ConfigTemplate)
        self.resolver = TemplateResolver(self.registry)

    def test_resolve_payload_template(self) -> None:
        """Should resolve template instance from payload."""
        payload = ValidatedPayload(data={"template": "payload"})
        config = ResolvedConfiguration(data={})
        result = self.resolver.resolve(payload, config)
        self.assertIsInstance(result, PayloadTemplate)
        self.assertIsInstance(result, TemplateProtocol)

    def test_resolve_payload_takes_precedence(self) -> None:
        """Payload should take precedence over configuration."""
        payload = ValidatedPayload(data={"template": "payload"})
        config = ResolvedConfiguration(data={"template": "config"})
        result = self.resolver.resolve(payload, config)
        self.assertIsInstance(result, PayloadTemplate)

    def test_resolve_configuration_template_nested(self) -> None:
        """Should resolve template instance from configuration (nested format)."""
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={"template": {"name": "config"}})
        result = self.resolver.resolve(payload, config)
        self.assertIsInstance(result, ConfigTemplate)

    def test_resolve_configuration_template_flat(self) -> None:
        """Should resolve template instance from configuration (flat format)."""
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={"template": "config"})
        result = self.resolver.resolve(payload, config)
        self.assertIsInstance(result, ConfigTemplate)

    def test_resolve_default_template(self) -> None:
        """Should resolve default template instance when no other selection."""
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={})
        result = self.resolver.resolve(payload, config)
        self.assertIsInstance(result, DefaultTemplate)

    def test_resolve_with_custom_default(self) -> None:
        """Should use custom default template name."""
        resolver = TemplateResolver(self.registry, default_template="config")
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={})
        result = resolver.resolve(payload, config)
        self.assertIsInstance(result, ConfigTemplate)

    def test_resolve_does_not_modify_payload(self) -> None:
        """Should not modify the payload."""
        payload = ValidatedPayload(data={"template": "payload"})
        config = ResolvedConfiguration(data={})
        original_data = dict(payload.data)
        self.resolver.resolve(payload, config)
        self.assertEqual(dict(payload.data), original_data)

    def test_resolve_does_not_modify_configuration(self) -> None:
        """Should not modify the configuration."""
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={"template": "config"})
        original_data = dict(config.data)
        self.resolver.resolve(payload, config)
        self.assertEqual(dict(config.data), original_data)

    def test_resolve_is_stateless(self) -> None:
        """Resolver should not hold per-request state."""
        resolver = TemplateResolver(self.registry)

        # First request
        payload1 = ValidatedPayload(data={"template": "payload"})
        config1 = ResolvedConfiguration(data={})
        result1 = resolver.resolve(payload1, config1)

        # Second request
        payload2 = ValidatedPayload(data={"template": "config"})
        config2 = ResolvedConfiguration(data={})
        result2 = resolver.resolve(payload2, config2)

        self.assertIsInstance(result1, PayloadTemplate)
        self.assertIsInstance(result2, ConfigTemplate)
        # No cross-contamination between requests

    def test_resolve_returns_instance_not_class(self) -> None:
        """Should return template instance, not class."""
        payload = ValidatedPayload(data={"template": "payload"})
        config = ResolvedConfiguration(data={})
        result = self.resolver.resolve(payload, config)
        self.assertIsInstance(result, TemplateProtocol)
        self.assertFalse(isinstance(result, type))

    def test_resolve_instance_has_execute_method(self) -> None:
        """Returned instance should have callable execute method."""
        payload = ValidatedPayload(data={"template": "payload"})
        config = ResolvedConfiguration(data={})
        result = self.resolver.resolve(payload, config)
        self.assertTrue(hasattr(result, "execute"))
        self.assertTrue(callable(result.execute))

    def test_resolve_missing_template_raises_error(self) -> None:
        """Should raise TemplateError when template not in registry."""
        resolver = TemplateResolver(self.registry, default_template="nonexistent")
        payload = ValidatedPayload(data={"template": "nonexistent"})
        config = ResolvedConfiguration(data={})
        with self.assertRaises(TemplateError) as ctx:
            resolver.resolve(payload, config)
        self.assertIn("not registered", str(ctx.exception))

    def test_resolve_empty_registry_raises_error(self) -> None:
        """Should raise TemplateError when registry is empty."""
        empty_registry = TemplateRegistry()
        resolver = TemplateResolver(empty_registry)
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={})
        with self.assertRaises(TemplateError) as ctx:
            resolver.resolve(payload, config)
        self.assertIn("no templates are registered", str(ctx.exception))

    def test_resolve_with_available_templates_message(self) -> None:
        """Error message should list available templates."""
        registry = TemplateRegistry()
        registry.register("test1", DefaultTemplate)
        registry.register("test2", DefaultTemplate)
        resolver = TemplateResolver(registry, default_template="nonexistent")
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={})
        with self.assertRaises(TemplateError) as ctx:
            resolver.resolve(payload, config)
        self.assertIn("test1", str(ctx.exception))
        self.assertIn("test2", str(ctx.exception))


class TestTemplateResolverPayloadExtraction(unittest.TestCase):
    """Test payload template extraction."""

    def setUp(self) -> None:
        self.registry = TemplateRegistry()
        self.registry.register("test", DefaultTemplate)
        self.resolver = TemplateResolver(self.registry)

    def test_payload_template_string(self) -> None:
        """Should extract string template from payload."""
        payload = ValidatedPayload(data={"template": "test"})
        result = self.resolver._get_payload_template(payload)
        self.assertEqual(result, "test")

    def test_payload_template_none(self) -> None:
        """Should return None when template not in payload."""
        payload = ValidatedPayload(data={})
        result = self.resolver._get_payload_template(payload)
        self.assertIsNone(result)

    def test_payload_template_non_string(self) -> None:
        """Should return None when template is not string."""
        payload = ValidatedPayload(data={"template": 123})
        result = self.resolver._get_payload_template(payload)
        self.assertIsNone(result)


class TestTemplateResolverConfigurationExtraction(unittest.TestCase):
    """Test configuration template extraction."""

    def setUp(self) -> None:
        self.registry = TemplateRegistry()
        self.registry.register("test", DefaultTemplate)
        self.resolver = TemplateResolver(self.registry)

    def test_config_template_nested(self) -> None:
        """Should extract template from nested configuration."""
        config = ResolvedConfiguration(data={"template": {"name": "test"}})
        result = self.resolver._get_configuration_template(config)
        self.assertEqual(result, "test")

    def test_config_template_flat(self) -> None:
        """Should extract template from flat configuration."""
        config = ResolvedConfiguration(data={"template": "test"})
        result = self.resolver._get_configuration_template(config)
        self.assertEqual(result, "test")

    def test_config_template_none(self) -> None:
        """Should return None when template not in configuration."""
        config = ResolvedConfiguration(data={})
        result = self.resolver._get_configuration_template(config)
        self.assertIsNone(result)

    def test_config_template_invalid_dict(self) -> None:
        """Should return None when template dict missing name."""
        config = ResolvedConfiguration(data={"template": {"other": "value"}})
        result = self.resolver._get_configuration_template(config)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()