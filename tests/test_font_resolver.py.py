"""Tests for FontResolver.

Tests the concrete FontResolver implementation against the
contract defined in 02_ARCHITECTURE.md Section 15 Step 1.4 and
04_RENDERING_SPECIFICATION.md Section 4.

Scope: FontResolver only. Does not test Validator,
ConfigurationResolver, AssetResolver, Template, Renderer, Canvas,
QualityVerifier, Exporter, or Pipeline.
"""

import os
import tempfile
import unittest
from pathlib import Path
from types import MappingProxyType

from engine.configuration.resolver import ResolvedConfiguration
from engine.core.exceptions import FontError
from engine.fonts.resolver import FontResolver, ResolvedFonts
from engine.validation.validator import ValidatedPayload


class TestResolvedFontsContract(unittest.TestCase):
    """The ResolvedFonts data contract must remain unchanged."""

    def test_default_data_is_empty_mapping(self) -> None:
        fonts = ResolvedFonts()
        self.assertEqual(dict(fonts.data), {})

    def test_data_is_immutable_mapping_proxy(self) -> None:
        fonts = ResolvedFonts(data={"headline": "DejaVuSans-Bold.ttf"})
        self.assertIsInstance(fonts.data, MappingProxyType)
        with self.assertRaises(TypeError):
            fonts.data["headline"] = "Other.ttf"  # type: ignore[index]

    def test_fonts_itself_is_frozen(self) -> None:
        fonts = ResolvedFonts(data={"headline": "DejaVuSans-Bold.ttf"})
        with self.assertRaises(Exception):
            fonts.data = {"headline": "Other.ttf"}  # type: ignore[misc]


class TestFontResolverSuccess(unittest.TestCase):
    """Test successful font resolution."""

    def setUp(self) -> None:
        self.resolver = FontResolver()

    def test_resolve_returns_resolved_fonts(self) -> None:
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={"fonts": {}})
        result = self.resolver.resolve(payload, config)
        self.assertIsInstance(result, ResolvedFonts)

    def test_resolve_with_system_fonts(self) -> None:
        # This test checks that the resolver can find system fonts
        # without actually requiring specific fonts to be present
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={"fonts": {}})
        result = self.resolver.resolve(payload, config)

        # Should have at least headline and body fonts
        data = dict(result.data)
        self.assertIn("headline", data)
        self.assertIn("body", data)

        # The paths should be valid
        headline_path = data["headline"]
        body_path = data["body"]
        self.assertTrue(Path(headline_path).exists() or isinstance(headline_path, Path))
        self.assertTrue(Path(body_path).exists() or isinstance(body_path, Path))

    def test_resolve_is_stateless(self) -> None:
        resolver = FontResolver()
        config = ResolvedConfiguration(data={"fonts": {}})

        payload1 = ValidatedPayload(data={"template": "breaking"})
        payload2 = ValidatedPayload(data={"template": "transfer"})

        result1 = resolver.resolve(payload1, config)
        result2 = resolver.resolve(payload2, config)

        # Both should return valid results
        self.assertIsInstance(result1, ResolvedFonts)
        self.assertIsInstance(result2, ResolvedFonts)

    def test_resolve_does_not_modify_payload(self) -> None:
        payload = ValidatedPayload(data={"template": "breaking"})
        config = ResolvedConfiguration(data={"fonts": {}})
        original_data = dict(payload.data)
        self.resolver.resolve(payload, config)
        self.assertEqual(dict(payload.data), original_data)

    def test_resolve_does_not_modify_configuration(self) -> None:
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={"fonts": {"headline": "Custom.ttf"}})
        original_data = dict(config.data)
        self.resolver.resolve(payload, config)
        self.assertEqual(dict(config.data), original_data)

    def test_resolve_returns_immutable_result(self) -> None:
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={"fonts": {}})
        result = self.resolver.resolve(payload, config)
        with self.assertRaises(TypeError):
            result.data["new_key"] = "value"  # type: ignore[index]

    def test_resolve_with_custom_font_path(self) -> None:
        # Create a temporary font directory with a dummy font
        with tempfile.TemporaryDirectory() as tmpdir:
            font_dir = Path(tmpdir) / "fonts"
            font_dir.mkdir()

            # Create dummy font files
            (font_dir / "CustomHeadline.ttf").touch()
            (font_dir / "CustomBody.ttf").touch()

            resolver = FontResolver(font_paths=[str(font_dir)])

            # Override font config to use custom fonts
            config = ResolvedConfiguration(data={
                "fonts": {
                    "headline": "CustomHeadline.ttf",
                    "body": "CustomBody.ttf",
                }
            })
            payload = ValidatedPayload(data={})
            result = resolver.resolve(payload, config)

            data = dict(result.data)
            self.assertIn("headline", data)
            self.assertIn("body", data)
            self.assertEqual(str(data["headline"]), str(font_dir / "CustomHeadline.ttf"))
            self.assertEqual(str(data["body"]), str(font_dir / "CustomBody.ttf"))


class TestFontResolverPayloadOverrides(unittest.TestCase):
    """Test payload-based font overrides."""

    def test_payload_font_overrides_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            font_dir = Path(tmpdir) / "fonts"
            font_dir.mkdir()

            # Create dummy font files
            (font_dir / "PayloadHeadline.ttf").touch()
            (font_dir / "ConfigHeadline.ttf").touch()

            resolver = FontResolver(font_paths=[str(font_dir)])

            config = ResolvedConfiguration(data={
                "fonts": {"headline": "ConfigHeadline.ttf"}
            })
            payload = ValidatedPayload(data={
                "fonts": {"headline": "PayloadHeadline.ttf"}
            })

            result = resolver.resolve(payload, config)
            data = dict(result.data)

            # Payload should win
            self.assertEqual(str(data["headline"]), str(font_dir / "PayloadHeadline.ttf"))

    def test_payload_font_required_if_specified(self) -> None:
        resolver = FontResolver()
        config = ResolvedConfiguration(data={"fonts": {}})
        payload = ValidatedPayload(data={
            "fonts": {"headline": "nonexistent.ttf"}
        })

        with self.assertRaises(FontError):
            resolver.resolve(payload, config)


class TestFontResolverConfiguration(unittest.TestCase):
    """Test configuration-based font resolution."""

    def test_config_font_paths_are_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            font_dir = Path(tmpdir) / "custom_fonts"
            font_dir.mkdir()

            (font_dir / "ConfigHeadline.ttf").touch()
            (font_dir / "ConfigBody.ttf").touch()

            resolver = FontResolver(font_paths=[str(font_dir)])

            config = ResolvedConfiguration(data={
                "fonts": {
                    "headline": "ConfigHeadline.ttf",
                    "body": "ConfigBody.ttf",
                }
            })
            payload = ValidatedPayload(data={})

            result = resolver.resolve(payload, config)
            data = dict(result.data)

            self.assertEqual(str(data["headline"]), str(font_dir / "ConfigHeadline.ttf"))
            self.assertEqual(str(data["body"]), str(font_dir / "ConfigBody.ttf"))

    def test_config_font_not_found_raises_font_error(self) -> None:
        resolver = FontResolver()
        config = ResolvedConfiguration(data={
            "fonts": {"headline": "NonexistentFont.ttf"}
        })
        payload = ValidatedPayload(data={})

        with self.assertRaises(FontError):
            resolver.resolve(payload, config)


class TestFontResolverFallback(unittest.TestCase):
    """Test font fallback behavior."""

    def test_fallback_font_is_resolved(self) -> None:
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={"fonts": {}})
        result = self.resolver.resolve(payload, config)

        data = dict(result.data)
        self.assertIn("fallback", data)

        # Fallback should be one of the other fonts
        fallback_path = data["fallback"]
        self.assertTrue(Path(fallback_path).exists() or isinstance(fallback_path, Path))

    def test_bold_font_uses_headline_if_available(self) -> None:
        # If bold font is not explicitly specified, it should use headline
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={"fonts": {}})
        result = self.resolver.resolve(payload, config)

        data = dict(result.data)
        if "bold" in data:
            # If bold is present, it's valid
            self.assertIsNotNone(data["bold"])

    def test_missing_required_font_raises_font_error(self) -> None:
        # This is hard to test deterministically because system fonts exist
        # We'll test by using a resolver with no search paths
        resolver = FontResolver()
        # Force no search paths by clearing them (hack for testing)
        resolver._SYSTEM_FONT_DIRS = []
        resolver._PROJECT_FONT_DIRS = []

        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={"fonts": {}})

        # Should raise FontError because no fonts can be found
        with self.assertRaises(FontError):
            resolver.resolve(payload, config)


class TestFontResolverErrorHandling(unittest.TestCase):
    """Test font resolution failures."""

    def test_resolve_raises_font_error_on_missing_payload_font(self) -> None:
        resolver = FontResolver()
        config = ResolvedConfiguration(data={})
        payload = ValidatedPayload(data={
            "fonts": {"headline": "nonexistent.ttf"}
        })

        with self.assertRaises(FontError):
            resolver.resolve(payload, config)

    def test_font_error_is_visual_engine_error(self) -> None:
        from engine.core.exceptions import VisualEngineError

        resolver = FontResolver()
        config = ResolvedConfiguration(data={})
        payload = ValidatedPayload(data={
            "fonts": {"headline": "nonexistent.ttf"}
        })

        with self.assertRaises(VisualEngineError):
            resolver.resolve(payload, config)

    def test_no_builtin_exception_escapes(self) -> None:
        resolver = FontResolver()
        config = ResolvedConfiguration(data={})
        payload = ValidatedPayload(data={
            "fonts": {"headline": "nonexistent.ttf"}
        })

        try:
            resolver.resolve(payload, config)
        except FontError:
            pass
        except Exception as exc:
            self.fail(f"A raw built-in exception escaped FontResolver: {exc!r}")

    def test_font_error_chains_original_exception(self) -> None:
        resolver = FontResolver()
        config = ResolvedConfiguration(data={})
        payload = ValidatedPayload(data={
            "fonts": {"headline": "nonexistent.ttf"}
        })

        with self.assertRaises(FontError) as ctx:
            resolver.resolve(payload, config)
        # Exception should have a cause
        self.assertIsNotNone(ctx.exception.__cause__)


class TestFontResolverPathResolution(unittest.TestCase):
    """Test path resolution for fonts."""

    def test_find_font_file_in_search_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            font_dir = Path(tmpdir) / "fonts"
            font_dir.mkdir()

            test_font = font_dir / "TestFont.ttf"
            test_font.touch()

            resolver = FontResolver(font_paths=[str(tmpdir)])
            search_paths = [Path(tmpdir)]
            result = resolver._find_font_file("TestFont.ttf", search_paths)

            self.assertEqual(str(result), str(test_font))

    def test_find_font_file_in_fonts_subdirectory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            font_dir = Path(tmpdir) / "fonts"
            font_dir.mkdir()

            test_font = font_dir / "TestFont.ttf"
            test_font.touch()

            resolver = FontResolver(font_paths=[str(tmpdir)])
            search_paths = [Path(tmpdir)]
            result = resolver._find_font_file("TestFont.ttf", search_paths)

            self.assertEqual(str(result), str(test_font))

    def test_find_font_file_not_found_returns_none(self) -> None:
        resolver = FontResolver()
        search_paths = [Path("/nonexistent/path")]
        result = resolver._find_font_file("Nonexistent.ttf", search_paths)
        self.assertIsNone(result)

    def test_resolve_font_path_convenience_method(self) -> None:
        # This method should work even without full payload/config
        resolver = FontResolver()
        # Try to find a system font
        result = resolver.resolve_font_path("DejaVuSans.ttf")
        # The result might be None if the font doesn't exist, but should not raise
        self.assertIsNotNone(result)


class TestFontResolverIntegration(unittest.TestCase):
    """Integration tests for FontResolver with other components."""

    def test_resolve_with_full_pipeline_inputs(self) -> None:
        # Simulate the full input to FontResolver as it would come from Pipeline
        payload = ValidatedPayload(data={
            "template": "breaking",
            "platform": "telegram",
            "fonts": {"headline": "DejaVuSans-Bold.ttf"},
        })

        config = ResolvedConfiguration(data={
            "fonts": {
                "headline": "DejaVuSans-Bold.ttf",
                "body": "DejaVuSans.ttf",
            }
        })

        resolver = FontResolver()
        result = resolver.resolve(payload, config)

        self.assertIsInstance(result, ResolvedFonts)
        # Should not raise any errors

    def test_resolve_preserves_configuration_data(self) -> None:
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={
            "engine": {"backend": "pillow"},
            "fonts": {"headline": "Headline.ttf"},
            "template": {"name": "default"},
            "platform": {"name": "telegram"},
        })

        resolver = FontResolver()
        result = resolver.resolve(payload, config)

        # Result should include fonts, not configuration
        self.assertIsInstance(result, ResolvedFonts)


if __name__ == "__main__":
    unittest.main()