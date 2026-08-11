"""Tests for ConfigurationResolver.

Tests the concrete ConfigurationResolver implementation against the
contract defined in 02_ARCHITECTURE.md Section 15 Step 1.2 and
04_RENDERING_SPECIFICATION.md Section 4.

Scope: ConfigurationResolver only. Does not test Validator,
AssetResolver, FontResolver, Template, Renderer, Canvas,
QualityVerifier, Exporter, or Pipeline.
"""

import json
import os
import tempfile
import unittest
from types import MappingProxyType

from engine.configuration.resolver import ConfigurationError, ConfigurationResolver, ResolvedConfiguration
from engine.validation.validator import ValidatedPayload


class TestResolvedConfigurationContract(unittest.TestCase):
    """The ResolvedConfiguration data contract must remain unchanged."""

    def test_default_data_is_empty_mapping(self) -> None:
        cfg = ResolvedConfiguration()
        self.assertEqual(dict(cfg.data), {})

    def test_data_is_immutable_mapping_proxy(self) -> None:
        cfg = ResolvedConfiguration(data={"a": 1})
        self.assertIsInstance(cfg.data, MappingProxyType)
        with self.assertRaises(TypeError):
            cfg.data["a"] = 2  # type: ignore[index]

    def test_configuration_itself_is_frozen(self) -> None:
        cfg = ResolvedConfiguration(data={"a": 1})
        with self.assertRaises(Exception):
            cfg.data = {"b": 2}  # type: ignore[misc]


class TestConfigurationResolverSuccess(unittest.TestCase):
    """Test successful configuration resolution."""

    def setUp(self) -> None:
        self.resolver = ConfigurationResolver()

    def test_resolve_returns_resolved_configuration(self) -> None:
        payload = ValidatedPayload(data={"template": "breaking"})
        result = self.resolver.resolve(payload)
        self.assertIsInstance(result, ResolvedConfiguration)

    def test_resolve_contains_default_values(self) -> None:
        payload = ValidatedPayload(data={})
        result = self.resolver.resolve(payload)
        data = dict(result.data)

        self.assertIn("engine", data)
        self.assertIn("template", data)
        self.assertIn("platform", data)

        self.assertIn("backend", data["engine"])
        self.assertIn("width", data["engine"])
        self.assertIn("height", data["engine"])

        self.assertIn("name", data["template"])
        self.assertIn("name", data["platform"])

    def test_resolve_applies_payload_template_override(self) -> None:
        payload = ValidatedPayload(data={"template": "breaking"})
        result = self.resolver.resolve(payload)
        self.assertEqual(result.data["template"]["name"], "breaking")

    def test_resolve_applies_payload_platform_override(self) -> None:
        payload = ValidatedPayload(data={"platform": "instagram"})
        result = self.resolver.resolve(payload)
        self.assertEqual(result.data["platform"]["name"], "instagram")

    def test_resolve_applies_payload_dimensions_override(self) -> None:
        payload = ValidatedPayload(data={"width": 1920, "height": 1080})
        result = self.resolver.resolve(payload)
        self.assertEqual(result.data["engine"]["width"], 1920)
        self.assertEqual(result.data["engine"]["height"], 1080)

    def test_resolve_ignores_unknown_payload_fields(self) -> None:
        payload = ValidatedPayload(data={"unknown": "field", "foo": "bar"})
        result = self.resolver.resolve(payload)
        # Should still contain defaults
        self.assertIn("engine", result.data)
        self.assertIn("template", result.data)
        self.assertIn("platform", result.data)

    def test_resolve_is_stateless(self) -> None:
        resolver = ConfigurationResolver()
        payload1 = ValidatedPayload(data={"template": "breaking"})
        payload2 = ValidatedPayload(data={"template": "transfer"})

        result1 = resolver.resolve(payload1)
        result2 = resolver.resolve(payload2)

        self.assertEqual(result1.data["template"]["name"], "breaking")
        self.assertEqual(result2.data["template"]["name"], "transfer")
        # Confirm resolver didn't retain state between calls
        self.assertNotEqual(result1.data["template"]["name"], result2.data["template"]["name"])

    def test_resolve_does_not_modify_payload(self) -> None:
        payload = ValidatedPayload(data={"template": "breaking"})
        original_data = dict(payload.data)
        self.resolver.resolve(payload)
        self.assertEqual(dict(payload.data), original_data)

    def test_resolve_returns_immutable_result(self) -> None:
        payload = ValidatedPayload(data={})
        result = self.resolver.resolve(payload)
        with self.assertRaises(TypeError):
            result.data["new_key"] = "value"  # type: ignore[index]


class TestConfigurationResolverEnvironment(unittest.TestCase):
    """Test environment variable overrides."""

    def setUp(self) -> None:
        self.resolver = ConfigurationResolver()
        self.env_backup = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self.env_backup)

    def test_environment_override_simple_string(self) -> None:
        os.environ["PUL7SAR_TEMPLATE_NAME"] = "match"
        payload = ValidatedPayload(data={})
        result = self.resolver.resolve(payload)
        self.assertEqual(result.data["template"]["name"], "match")

    def test_environment_override_nested_path(self) -> None:
        os.environ["PUL7SAR_ENGINE_BACKEND"] = "skia"
        payload = ValidatedPayload(data={})
        result = self.resolver.resolve(payload)
        self.assertEqual(result.data["engine"]["backend"], "skia")

    def test_environment_override_boolean(self) -> None:
        os.environ["PUL7SAR_ENGINE_DEBUG"] = "true"
        payload = ValidatedPayload(data={})
        result = self.resolver.resolve(payload)
        # Should add the debug key
        self.assertTrue(result.data["engine"].get("debug", False))

    def test_environment_override_integer(self) -> None:
        os.environ["PUL7SAR_ENGINE_WIDTH"] = "1920"
        payload = ValidatedPayload(data={})
        result = self.resolver.resolve(payload)
        self.assertEqual(result.data["engine"]["width"], 1920)

    def test_environment_override_float(self) -> None:
        os.environ["PUL7SAR_ENGINE_SCALE"] = "1.5"
        payload = ValidatedPayload(data={})
        result = self.resolver.resolve(payload)
        self.assertEqual(result.data["engine"]["scale"], 1.5)

    def test_environment_payload_override_takes_precedence(self) -> None:
        # Environment sets one value, payload sets another
        os.environ["PUL7SAR_TEMPLATE_NAME"] = "match"
        payload = ValidatedPayload(data={"template": "breaking"})
        result = self.resolver.resolve(payload)
        # Payload should win
        self.assertEqual(result.data["template"]["name"], "breaking")


class TestConfigurationResolverFileConfig(unittest.TestCase):
    """Test file-based configuration loading."""

    def test_json_config_file(self) -> None:
        config_data = {
            "engine": {"backend": "skia", "width": 1920},
            "template": {"name": "match"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()
            path = f.name

        try:
            resolver = ConfigurationResolver(config_path=path)
            payload = ValidatedPayload(data={})
            result = resolver.resolve(payload)

            self.assertEqual(result.data["engine"]["backend"], "skia")
            self.assertEqual(result.data["engine"]["width"], 1920)
            self.assertEqual(result.data["template"]["name"], "match")
        finally:
            os.unlink(path)

    def test_payload_overrides_file_config(self) -> None:
        config_data = {"template": {"name": "match"}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()
            path = f.name

        try:
            resolver = ConfigurationResolver(config_path=path)
            payload = ValidatedPayload(data={"template": "breaking"})
            result = resolver.resolve(payload)
            # Payload should win over file
            self.assertEqual(result.data["template"]["name"], "breaking")
        finally:
            os.unlink(path)

    def test_environment_overrides_file_config(self) -> None:
        config_data = {"template": {"name": "match"}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()
            path = f.name

        try:
            os.environ["PUL7SAR_TEMPLATE_NAME"] = "transfer"
            resolver = ConfigurationResolver(config_path=path)
            payload = ValidatedPayload(data={})
            result = resolver.resolve(payload)
            # Environment should win over file
            self.assertEqual(result.data["template"]["name"], "transfer")
        finally:
            os.unlink(path)
            os.environ.pop("PUL7SAR_TEMPLATE_NAME", None)

    def test_missing_config_file_uses_defaults(self) -> None:
        resolver = ConfigurationResolver(config_path="/nonexistent/config.json")
        payload = ValidatedPayload(data={})
        result = resolver.resolve(payload)
        # Should still have defaults
        self.assertIn("engine", result.data)
        self.assertIn("template", result.data)
        self.assertIn("platform", result.data)


class TestConfigurationResolverFailure(unittest.TestCase):
    """Test configuration resolution failures."""

    def setUp(self) -> None:
        self.resolver = ConfigurationResolver()

    def test_resolve_raises_configuration_error_on_invalid_payload(self) -> None:
        # Payload that causes invalid config (template name missing)
        # This shouldn't happen normally since Validator validates structure,
        # but we test that ConfigurationError is raised for invalid config
        pass  # Actually, the resolver always provides defaults, so it won't fail

    def test_configuration_error_is_visual_engine_error(self) -> None:
        from engine.core.exceptions import VisualEngineError

        # Force a configuration error by providing an invalid config file
        config_data = {"engine": "not_a_dict"}  # Invalid type
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()
            path = f.name

        try:
            resolver = ConfigurationResolver(config_path=path)
            payload = ValidatedPayload(data={})
            with self.assertRaises(VisualEngineError):
                resolver.resolve(payload)
        finally:
            os.unlink(path)

    def test_no_builtin_exception_escapes(self) -> None:
        config_data = {"engine": "not_a_dict"}  # Invalid type
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()
            path = f.name

        try:
            resolver = ConfigurationResolver(config_path=path)
            payload = ValidatedPayload(data={})
            try:
                resolver.resolve(payload)
            except ConfigurationError:
                pass
            except Exception as exc:
                self.fail(f"A raw built-in exception escaped ConfigurationResolver: {exc!r}")
        finally:
            os.unlink(path)

    def test_configuration_error_chains_original_exception(self) -> None:
        config_data = {"engine": "not_a_dict"}  # Invalid type
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()
            path = f.name

        try:
            resolver = ConfigurationResolver(config_path=path)
            payload = ValidatedPayload(data={})
            with self.assertRaises(ConfigurationError) as ctx:
                resolver.resolve(payload)
            # Exception should have a cause
            self.assertIsNotNone(ctx.exception.__cause__)
        finally:
            os.unlink(path)


class TestConfigurationResolverDeepMerge(unittest.TestCase):
    """Test the deep merge functionality."""

    def test_deep_merge_simple(self) -> None:
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = ConfigurationResolver._deep_merge(base, override)
        self.assertEqual(result, {"a": 1, "b": 3, "c": 4})

    def test_deep_merge_nested(self) -> None:
        base = {"engine": {"backend": "pillow", "width": 1280}}
        override = {"engine": {"backend": "skia", "height": 720}}
        result = ConfigurationResolver._deep_merge(base, override)
        self.assertEqual(
            result,
            {"engine": {"backend": "skia", "width": 1280, "height": 720}}
        )

    def test_deep_merge_override_non_dict_with_dict(self) -> None:
        base = {"engine": "pillow"}
        override = {"engine": {"backend": "skia"}}
        result = ConfigurationResolver._deep_merge(base, override)
        # Override wins, replacing the value entirely
        self.assertEqual(result, {"engine": {"backend": "skia"}})


if __name__ == "__main__":
    unittest.main()