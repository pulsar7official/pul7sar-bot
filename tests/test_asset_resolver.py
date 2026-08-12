"""Tests for AssetResolver.

Tests the concrete AssetResolver implementation against the
contract defined in 02_ARCHITECTURE.md Section 15 Step 1.3 and
04_RENDERING_SPECIFICATION.md Section 4.

Scope: AssetResolver only. Does not test Validator,
ConfigurationResolver, FontResolver, Template, Renderer, Canvas,
QualityVerifier, Exporter, or Pipeline.
"""

import os
import tempfile
import unittest
from pathlib import Path
from types import MappingProxyType

from engine.assets.resolver import AssetError, AssetResolver, ResolvedAssets
from engine.configuration.resolver import ResolvedConfiguration
from engine.validation.validator import ValidatedPayload


class TestResolvedAssetsContract(unittest.TestCase):
    """The ResolvedAssets data contract must remain unchanged."""

    def test_default_data_is_empty_mapping(self) -> None:
        assets = ResolvedAssets()
        self.assertEqual(dict(assets.data), {})

    def test_data_is_immutable_mapping_proxy(self) -> None:
        assets = ResolvedAssets(data={"logo": "logo.png"})
        self.assertIsInstance(assets.data, MappingProxyType)
        with self.assertRaises(TypeError):
            assets.data["logo"] = "other.png"  # type: ignore[index]

    def test_assets_itself_is_frozen(self) -> None:
        assets = ResolvedAssets(data={"logo": "logo.png"})
        with self.assertRaises(Exception):
            assets.data = {"logo": "other.png"}  # type: ignore[misc]


class TestAssetResolverSuccess(unittest.TestCase):
    """Test successful asset resolution."""

    def setUp(self) -> None:
        self.resolver = AssetResolver()
        self.config = ResolvedConfiguration(data={
            "assets": {
                "logo": "logo.png",
                "backgrounds_dir": "assets/backgrounds",
            }
        })

    def test_resolve_returns_resolved_assets(self) -> None:
        payload = ValidatedPayload(data={})
        result = self.resolver.resolve(payload, self.config)
        self.assertIsInstance(result, ResolvedAssets)

    def test_resolve_includes_logo_if_exists(self) -> None:
        # Create a temporary logo file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".png", delete=False) as f:
            f.write("fake image data")
            temp_path = f.name

        try:
            resolver = AssetResolver(asset_root=os.path.dirname(temp_path))
            config = ResolvedConfiguration(data={
                "assets": {"logo": os.path.basename(temp_path)}
            })
            payload = ValidatedPayload(data={})
            result = resolver.resolve(payload, config)

            self.assertIn("logo", result.data)
            self.assertEqual(str(result.data["logo"]), temp_path)
        finally:
            os.unlink(temp_path)

    def test_resolve_handles_missing_logo_gracefully(self) -> None:
        # No logo file exists, resolver should return None for logo
        payload = ValidatedPayload(data={})
        result = self.resolver.resolve(payload, self.config)
        # Logo is optional in Phase 2
        self.assertIsInstance(result, ResolvedAssets)

    def test_resolve_returns_empty_assets_on_no_assets_found(self) -> None:
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={})
        result = self.resolver.resolve(payload, config)
        self.assertEqual(dict(result.data), {})

    def test_resolve_is_stateless(self) -> None:
        resolver = AssetResolver()
        config = ResolvedConfiguration(data={"assets": {"logo": "logo.png"}})

        payload1 = ValidatedPayload(data={"template": "breaking"})
        payload2 = ValidatedPayload(data={"template": "transfer"})

        result1 = resolver.resolve(payload1, config)
        result2 = resolver.resolve(payload2, config)

        # Both should return valid results
        self.assertIsInstance(result1, ResolvedAssets)
        self.assertIsInstance(result2, ResolvedAssets)

    def test_resolve_does_not_modify_payload(self) -> None:
        payload = ValidatedPayload(data={"template": "breaking"})
        config = ResolvedConfiguration(data={"assets": {}})
        original_data = dict(payload.data)
        self.resolver.resolve(payload, config)
        self.assertEqual(dict(payload.data), original_data)

    def test_resolve_does_not_modify_configuration(self) -> None:
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={"assets": {"logo": "logo.png"}})
        original_data = dict(config.data)
        self.resolver.resolve(payload, config)
        self.assertEqual(dict(config.data), original_data)

    def test_resolve_returns_immutable_result(self) -> None:
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={})
        result = self.resolver.resolve(payload, config)
        with self.assertRaises(TypeError):
            result.data["new_key"] = "value"  # type: ignore[index]


class TestAssetResolverPayloadOverrides(unittest.TestCase):
    """Test payload-based asset overrides."""

    def test_payload_logo_overrides_config(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".png", delete=False) as f:
            f.write("fake image data")
            temp_path = f.name

        try:
            resolver = AssetResolver(asset_root=os.path.dirname(temp_path))
            config = ResolvedConfiguration(data={
                "assets": {"logo": "config_logo.png"}
            })
            payload = ValidatedPayload(data={
                "logo": os.path.basename(temp_path)
            })
            result = resolver.resolve(payload, config)

            # Payload should win
            self.assertEqual(str(result.data["logo"]), temp_path)
        finally:
            os.unlink(temp_path)

    def test_payload_logo_required_if_specified(self) -> None:
        resolver = AssetResolver()
        config = ResolvedConfiguration(data={"assets": {}})
        payload = ValidatedPayload(data={"logo": "nonexistent.png"})

        with self.assertRaises(AssetError):
            resolver.resolve(payload, config)


class TestAssetResolverErrorHandling(unittest.TestCase):
    """Test asset resolution failures."""

    def test_resolve_raises_asset_error_on_payload_logo_not_found(self) -> None:
        resolver = AssetResolver()
        config = ResolvedConfiguration(data={})
        payload = ValidatedPayload(data={"logo": "nonexistent.png"})

        with self.assertRaises(AssetError):
            resolver.resolve(payload, config)

    def test_asset_error_is_visual_engine_error(self) -> None:
        from engine.core.exceptions import VisualEngineError

        resolver = AssetResolver()
        config = ResolvedConfiguration(data={})
        payload = ValidatedPayload(data={"logo": "nonexistent.png"})

        with self.assertRaises(VisualEngineError):
            resolver.resolve(payload, config)

    def test_no_builtin_exception_escapes(self) -> None:
        resolver = AssetResolver()
        config = ResolvedConfiguration(data={})
        payload = ValidatedPayload(data={"logo": "nonexistent.png"})

        try:
            resolver.resolve(payload, config)
        except AssetError:
            pass
        except Exception as exc:
            self.fail(f"A raw built-in exception escaped AssetResolver: {exc!r}")

    def test_asset_error_chains_original_exception(self) -> None:
        resolver = AssetResolver()
        config = ResolvedConfiguration(data={})
        payload = ValidatedPayload(data={"logo": "nonexistent.png"})

        with self.assertRaises(AssetError) as ctx:
            resolver.resolve(payload, config)
        # Exception should have a cause
        self.assertIsNotNone(ctx.exception.__cause__)


class TestAssetResolverAssetDiscovery(unittest.TestCase):
    """Test asset discovery and loading."""

    def test_backgrounds_directory_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a backgrounds directory with some images
            bg_dir = Path(tmpdir) / "assets" / "backgrounds"
            bg_dir.mkdir(parents=True)

            # Create dummy image files
            (bg_dir / "dark.png").touch()
            (bg_dir / "stadium.jpg").touch()
            (bg_dir / "gradient.png").touch()

            resolver = AssetResolver(asset_root=tmpdir)
            config = ResolvedConfiguration(data={
                "assets": {"backgrounds_dir": "assets/backgrounds"}
            })
            payload = ValidatedPayload(data={})
            result = resolver.resolve(payload, config)

            self.assertIn("backgrounds", result.data)
            backgrounds = result.data["backgrounds"]
            self.assertEqual(len(backgrounds), 3)
            self.assertIn("dark", backgrounds)
            self.assertIn("stadium", backgrounds)
            self.assertIn("gradient", backgrounds)

    def test_icons_directory_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            icons_dir = Path(tmpdir) / "assets" / "icons"
            icons_dir.mkdir(parents=True)

            (icons_dir / "trophy.png").touch()
            (icons_dir / "whistle.png").touch()

            resolver = AssetResolver(asset_root=tmpdir)
            config = ResolvedConfiguration(data={
                "assets": {"icons_dir": "assets/icons"}
            })
            payload = ValidatedPayload(data={})
            result = resolver.resolve(payload, config)

            self.assertIn("icons", result.data)
            icons = result.data["icons"]
            self.assertEqual(len(icons), 2)
            self.assertIn("trophy", icons)
            self.assertIn("whistle", icons)

    def test_only_supported_formats_are_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            bg_dir = Path(tmpdir) / "assets" / "backgrounds"
            bg_dir.mkdir(parents=True)

            # Create files with various extensions
            (bg_dir / "image.png").touch()
            (bg_dir / "image.jpg").touch()
            (bg_dir / "image.jpeg").touch()
            (bg_dir / "image.webp").touch()
            (bg_dir / "image.gif").touch()
            (bg_dir / "image.bmp").touch()
            (bg_dir / "image.txt").touch()
            (bg_dir / "image.svg").touch()

            resolver = AssetResolver(asset_root=tmpdir)
            config = ResolvedConfiguration(data={
                "assets": {"backgrounds_dir": "assets/backgrounds"}
            })
            payload = ValidatedPayload(data={})
            result = resolver.resolve(payload, config)

            self.assertIn("backgrounds", result.data)
            backgrounds = result.data["backgrounds"]
            # Only image formats should be discovered
            self.assertEqual(len(backgrounds), 6)  # png, jpg, jpeg, webp, gif, bmp

    def test_empty_asset_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            bg_dir = Path(tmpdir) / "assets" / "backgrounds"
            bg_dir.mkdir(parents=True)

            resolver = AssetResolver(asset_root=tmpdir)
            config = ResolvedConfiguration(data={
                "assets": {"backgrounds_dir": "assets/backgrounds"}
            })
            payload = ValidatedPayload(data={})
            result = resolver.resolve(payload, config)

            self.assertIn("backgrounds", result.data)
            self.assertEqual(len(result.data["backgrounds"]), 0)

    def test_missing_asset_directory_returns_empty(self) -> None:
        resolver = AssetResolver()
        config = ResolvedConfiguration(data={
            "assets": {"backgrounds_dir": "nonexistent/directory"}
        })
        payload = ValidatedPayload(data={})
        result = resolver.resolve(payload, config)

        self.assertIn("backgrounds", result.data)
        self.assertEqual(len(result.data["backgrounds"]), 0)


class TestAssetResolverPathResolution(unittest.TestCase):
    """Test path resolution for assets."""

    def test_absolute_path_resolution(self) -> None:
        resolver = AssetResolver()
        abs_path = "/absolute/path/to/logo.png"
        resolved = resolver._resolve_asset_path(abs_path)
        self.assertEqual(str(resolved), abs_path)

    def test_relative_path_resolution(self) -> None:
        resolver = AssetResolver(asset_root="/test/root")
        resolved = resolver._resolve_asset_path("logo.png")
        self.assertEqual(str(resolved), "/test/root/logo.png")

    def test_empty_path_returns_none(self) -> None:
        resolver = AssetResolver()
        resolved = resolver._resolve_asset_path("")
        self.assertIsNone(resolved)


class TestAssetResolverIntegration(unittest.TestCase):
    """Integration tests for AssetResolver with other components."""

    def test_resolve_with_full_pipeline_inputs(self) -> None:
        # Simulate the full input to AssetResolver as it would come from Pipeline
        payload = ValidatedPayload(data={
            "template": "breaking",
            "platform": "telegram",
        })

        config = ResolvedConfiguration(data={
            "assets": {
                "logo": "logo.png",
                "backgrounds_dir": "assets/backgrounds",
            }
        })

        resolver = AssetResolver()
        result = resolver.resolve(payload, config)

        self.assertIsInstance(result, ResolvedAssets)
        # Should not raise any errors

    def test_resolve_preserves_configuration_data(self) -> None:
        payload = ValidatedPayload(data={})
        config = ResolvedConfiguration(data={
            "engine": {"backend": "pillow"},
            "assets": {"logo": "logo.png"},
            "template": {"name": "default"},
            "platform": {"name": "telegram"},
        })

        resolver = AssetResolver()
        result = resolver.resolve(payload, config)

        # Result should include assets, not configuration
        self.assertIsInstance(result, ResolvedAssets)


if __name__ == "__main__":
    unittest.main()