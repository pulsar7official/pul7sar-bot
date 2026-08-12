"""AssetResolver subsystem.

Per 02_ARCHITECTURE.md, Section 15, Step 1.3 and
04_RENDERING_SPECIFICATION.md, Section 4:

    AssetResolver
        Input:  ValidatedPayload, ResolvedConfiguration
        Output: ResolvedAssets (immutable)
        Raises: AssetError
        Depends only on ValidatedPayload and ResolvedConfiguration.
        Does not depend on FontResolver or Template.

This module defines:
    - ResolvedAssets: Immutable data contract (Phase 1)
    - AssetResolver: Concrete implementation (Phase 2+)

The resolver loads visual assets from the filesystem and resolves
external asset URLs. Assets include logos, backgrounds, icons,
textures, overlays, and other visual resources required for rendering.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional, Union

from engine.configuration.resolver import ResolvedConfiguration
from engine.core.exceptions import AssetError
from engine.validation.validator import ValidatedPayload


@dataclass(frozen=True)
class ResolvedAssets:
    """Immutable output of AssetResolver.

    Contains data only. Field schema is an implementation detail left
    open by the frozen specification; ``data`` holds the resolved
    assets as an immutable mapping.

    The data typically includes:
        - logo: PIL.Image or file path to logo
        - backgrounds: dict of background assets
        - icons: dict of icon assets
        - overlays: dict of overlay assets
        - textures: dict of texture assets
    """

    data: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "data", MappingProxyType(dict(self.data)))


class AssetResolver:
    """Concrete implementation of the AssetResolver contract.

    Resolves visual assets required for rendering: logos, backgrounds,
    icons, textures, overlays, and other visual resources.

    Stateless: holds no instance state, depends only on the input
    ValidatedPayload and ResolvedConfiguration. Does not validate the
    request (Validator already did that). Does not know about fonts,
    templates, rendering, or export.

    Asset resolution strategy:
        1. Determine asset paths from configuration
        2. Check if assets exist on the filesystem
        3. Load assets into memory (images, vectors, etc.)
        4. Validate asset integrity (format, size, etc.)
        5. Return resolved assets as immutable mapping

    The resolver supports:
        - Local file assets (from project directory)
        - Asset references in configuration
        - Payload-specified asset overrides
    """

    # Default asset paths (relative to project root)
    _DEFAULT_ASSET_PATHS: Mapping[str, str] = MappingProxyType({
        "logo": "logo.png",
        "logo_alt": "pulsar7.PNG",
        "backgrounds_dir": "assets/backgrounds",
        "icons_dir": "assets/icons",
        "textures_dir": "assets/textures",
        "overlays_dir": "assets/overlays",
    })

    # Supported image formats for loading
    _SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}

    def __init__(self, asset_root: Optional[str] = None) -> None:
        """Initialize the AssetResolver.

        Args:
            asset_root: Root directory for assets. If not provided,
                       uses the current working directory.
        """
        self._asset_root = Path(asset_root) if asset_root else Path.cwd()

    def resolve(
        self,
        validated_payload: ValidatedPayload,
        resolved_configuration: ResolvedConfiguration,
    ) -> ResolvedAssets:
        """Resolve assets for the validated rendering request.

        Args:
            validated_payload: The validated rendering request from Validator.
            resolved_configuration: The resolved configuration from ConfigurationResolver.

        Returns:
            ResolvedAssets: Immutable resolved assets.

        Raises:
            AssetError: If any required asset cannot be found or loaded.
                This includes missing files, unsupported formats, corrupt
                assets, and other asset-related failures.

        The AssetError may chain the original exception using
        Python exception chaining.
        """
        try:
            assets: Dict[str, Any] = {}

            # Get asset configuration
            config_data = dict(resolved_configuration.data)
            asset_config = config_data.get("assets", {})

            # Resolve logo
            logo = self._resolve_logo(validated_payload, asset_config)
            if logo is not None:
                assets["logo"] = logo

            # Resolve backgrounds if configured
            backgrounds = self._resolve_backgrounds(validated_payload, asset_config)
            if backgrounds:
                assets["backgrounds"] = backgrounds

            # Resolve icons if configured
            icons = self._resolve_icons(validated_payload, asset_config)
            if icons:
                assets["icons"] = icons

            # Resolve overlays if configured
            overlays = self._resolve_overlays(validated_payload, asset_config)
            if overlays:
                assets["overlays"] = overlays

            # Resolve textures if configured
            textures = self._resolve_textures(validated_payload, asset_config)
            if textures:
                assets["textures"] = textures

            return ResolvedAssets(data=assets)

        except AssetError:
            raise
        except Exception as exc:
            raise AssetError(
                f"Failed to resolve assets: {exc}"
            ) from exc

    def _resolve_logo(
        self,
        validated_payload: ValidatedPayload,
        asset_config: Mapping[str, Any],
    ) -> Optional[Path]:
        """Resolve the logo asset.

        Logo resolution order:
            1. Payload-specified logo path
            2. Configuration-specified logo path
            3. Default path: logo.png
            4. Alternative: pulsar7.PNG

        Args:
            validated_payload: The validated payload.
            asset_config: Asset configuration from ResolvedConfiguration.

        Returns:
            Optional[Path]: Path to the resolved logo, or None if not found.

        Raises:
            AssetError: If the logo is explicitly required but cannot be found.
        """
        payload_data = dict(validated_payload.data)
        config_data = dict(asset_config)

        # Check payload for logo override
        logo_path = payload_data.get("logo")
        if logo_path and isinstance(logo_path, str):
            resolved = self._resolve_asset_path(logo_path)
            if resolved and resolved.exists():
                return resolved
            # If payload explicitly specifies a logo, it's required
            raise AssetError(f"Logo specified in payload not found: {logo_path}")

        # Check configuration
        logo_path = config_data.get("logo")
        if logo_path and isinstance(logo_path, str):
            resolved = self._resolve_asset_path(logo_path)
            if resolved and resolved.exists():
                return resolved

        # Check default paths
        for default_path in self._DEFAULT_ASSET_PATHS.values():
            if "logo" in default_path:
                resolved = self._resolve_asset_path(default_path)
                if resolved and resolved.exists():
                    return resolved

        # Logo is optional in Phase 2 (for backward compatibility)
        # In Phase 3+, this will become required
        return None

    def _resolve_backgrounds(
        self,
        validated_payload: ValidatedPayload,
        asset_config: Mapping[str, Any],
    ) -> Dict[str, Path]:
        """Resolve background assets.

        Args:
            validated_payload: The validated payload.
            asset_config: Asset configuration from ResolvedConfiguration.

        Returns:
            Dict[str, Path]: Mapping of background names to paths.
        """
        backgrounds: Dict[str, Path] = {}
        config_data = dict(asset_config)

        # Get backgrounds directory from config
        bg_dir = config_data.get("backgrounds_dir")
        if not bg_dir:
            bg_dir = self._DEFAULT_ASSET_PATHS["backgrounds_dir"]

        resolved_dir = self._resolve_asset_path(bg_dir)
        if resolved_dir and resolved_dir.exists() and resolved_dir.is_dir():
            for file_path in resolved_dir.iterdir():
                if file_path.suffix.lower() in self._SUPPORTED_FORMATS:
                    name = file_path.stem
                    backgrounds[name] = file_path

        return backgrounds

    def _resolve_icons(
        self,
        validated_payload: ValidatedPayload,
        asset_config: Mapping[str, Any],
    ) -> Dict[str, Path]:
        """Resolve icon assets.

        Args:
            validated_payload: The validated payload.
            asset_config: Asset configuration from ResolvedConfiguration.

        Returns:
            Dict[str, Path]: Mapping of icon names to paths.
        """
        icons: Dict[str, Path] = {}
        config_data = dict(asset_config)

        # Get icons directory from config
        icons_dir = config_data.get("icons_dir")
        if not icons_dir:
            icons_dir = self._DEFAULT_ASSET_PATHS["icons_dir"]

        resolved_dir = self._resolve_asset_path(icons_dir)
        if resolved_dir and resolved_dir.exists() and resolved_dir.is_dir():
            for file_path in resolved_dir.iterdir():
                if file_path.suffix.lower() in self._SUPPORTED_FORMATS:
                    name = file_path.stem
                    icons[name] = file_path

        return icons

    def _resolve_overlays(
        self,
        validated_payload: ValidatedPayload,
        asset_config: Mapping[str, Any],
    ) -> Dict[str, Path]:
        """Resolve overlay assets.

        Args:
            validated_payload: The validated payload.
            asset_config: Asset configuration from ResolvedConfiguration.

        Returns:
            Dict[str, Path]: Mapping of overlay names to paths.
        """
        overlays: Dict[str, Path] = {}
        config_data = dict(asset_config)

        # Get overlays directory from config
        overlays_dir = config_data.get("overlays_dir")
        if not overlays_dir:
            overlays_dir = self._DEFAULT_ASSET_PATHS["overlays_dir"]

        resolved_dir = self._resolve_asset_path(overlays_dir)
        if resolved_dir and resolved_dir.exists() and resolved_dir.is_dir():
            for file_path in resolved_dir.iterdir():
                if file_path.suffix.lower() in self._SUPPORTED_FORMATS:
                    name = file_path.stem
                    overlays[name] = file_path

        return overlays

    def _resolve_textures(
        self,
        validated_payload: ValidatedPayload,
        asset_config: Mapping[str, Any],
    ) -> Dict[str, Path]:
        """Resolve texture assets.

        Args:
            validated_payload: The validated payload.
            asset_config: Asset configuration from ResolvedConfiguration.

        Returns:
            Dict[str, Path]: Mapping of texture names to paths.
        """
        textures: Dict[str, Path] = {}
        config_data = dict(asset_config)

        # Get textures directory from config
        textures_dir = config_data.get("textures_dir")
        if not textures_dir:
            textures_dir = self._DEFAULT_ASSET_PATHS["textures_dir"]

        resolved_dir = self._resolve_asset_path(textures_dir)
        if resolved_dir and resolved_dir.exists() and resolved_dir.is_dir():
            for file_path in resolved_dir.iterdir():
                if file_path.suffix.lower() in self._SUPPORTED_FORMATS:
                    name = file_path.stem
                    textures[name] = file_path

        return textures

    def _resolve_asset_path(self, path: str) -> Optional[Path]:
        """Resolve an asset path relative to the asset root.

        Args:
            path: Asset path (absolute or relative).

        Returns:
            Optional[Path]: Resolved path, or None if resolution fails.
        """
        if not path:
            return None

        # If absolute path, use as-is
        abs_path = Path(path)
        if abs_path.is_absolute():
            return abs_path

        # Resolve relative to asset root
        resolved = self._asset_root / path

        # Also check if the file exists in the current working directory
        # (for backward compatibility with main.py)
        if not resolved.exists():
            cwd_path = Path.cwd() / path
            if cwd_path.exists():
                return cwd_path

        return resolved

    def load_image(self, path: Union[str, Path]) -> Any:
        """Load an image from a path.

        This method is a convenience for loading images. It does not
        load the image at resolve() time to keep asset resolution
        lightweight. The actual image loading is deferred to the
        renderer.

        Args:
            path: Path to the image file.

        Returns:
            Any: The loaded image (implementation-dependent).

        Raises:
            AssetError: If the image cannot be loaded.
        """
        # This is a placeholder. In Phase 3+, this will use PIL
        # to load images. For now, we just return the path.
        # The renderer will handle actual image loading.
        return str(path)


def asset_exists(path: Union[str, Path]) -> bool:
    """Check if an asset exists on the filesystem.

    Args:
        path: Path to the asset.

    Returns:
        bool: True if the asset exists, False otherwise.
    """
    return Path(path).exists()