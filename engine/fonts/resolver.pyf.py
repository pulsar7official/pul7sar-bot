"""FontResolver subsystem.

Per 02_ARCHITECTURE.md, Section 15, Step 1.4 and
04_RENDERING_SPECIFICATION.md, Section 4:

    FontResolver
        Input:  ValidatedPayload, ResolvedConfiguration
        Output: ResolvedFonts (immutable)
        Raises: FontError
        Depends only on ValidatedPayload and ResolvedConfiguration.
        Does not depend on AssetResolver or Template.

This module defines:
    - ResolvedFonts: Immutable data contract (Phase 1)
    - FontResolver: Concrete implementation (Phase 3+)

The resolver loads font files from the filesystem and resolves
font references. Fonts include headline fonts, body fonts, Arabic
fonts, and bold variants required for rendering.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Optional, Union

from engine.configuration.resolver import ResolvedConfiguration
from engine.core.exceptions import FontError
from engine.validation.validator import ValidatedPayload


@dataclass(frozen=True)
class ResolvedFonts:
    """Immutable output of FontResolver.

    Contains data only. Field schema is an implementation detail left
    open by the frozen specification; ``data`` holds the resolved
    fonts as an immutable mapping.

    The data typically includes:
        - headline: path to headline font
        - body: path to body font
        - arabic: path to Arabic font
        - bold: path to bold font
        - fallback: path to fallback font
    """

    data: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "data", MappingProxyType(dict(self.data)))


class FontResolver:
    """Concrete implementation of the FontResolver contract.

    Resolves fonts required for rendering: headline, body, Arabic,
    bold, and fallback fonts.

    Stateless: holds no instance state, depends only on the input
    ValidatedPayload and ResolvedConfiguration. Does not validate the
    request (Validator already did that). Does not know about assets,
    templates, rendering, or export.

    Font resolution strategy:
        1. Determine font paths from configuration
        2. Check if fonts exist on the filesystem
        3. Validate font files are readable
        4. Return resolved fonts as immutable mapping

    The resolver supports:
        - System fonts (from common system directories)
        - Project fonts (from fonts/ directory)
        - Payload-specified font overrides
        - Configuration-specified font paths
        - Fallback fonts when primary fonts are unavailable
    """

    # Common system font directories (Linux/Unix)
    _SYSTEM_FONT_DIRS: List[str] = [
        "/usr/share/fonts/truetype",
        "/usr/share/fonts",
        "/usr/local/share/fonts",
        "/usr/lib/fonts",
        "/System/Library/Fonts",  # macOS
        "/Library/Fonts",          # macOS
        "C:/Windows/Fonts",        # Windows (might not exist in Ubuntu)
    ]

    # Default font file names to search for
    _DEFAULT_FONT_NAMES: Mapping[str, List[str]] = MappingProxyType({
        "headline": [
            "DejaVuSans-Bold.ttf",
            "DejaVuSans.ttf",
            "LiberationSans-Bold.ttf",
            "LiberationSans-Regular.ttf",
            "NotoSans-Bold.ttf",
            "NotoSans-Regular.ttf",
            "Arial.ttf",
        ],
        "body": [
            "DejaVuSans.ttf",
            "LiberationSans-Regular.ttf",
            "NotoSans-Regular.ttf",
            "Arial.ttf",
        ],
        "arabic": [
            "NotoSansArabic-Bold.ttf",
            "NotoSansArabic-Regular.ttf",
            "NotoNaskhArabic-Regular.ttf",
            "NotoNaskhArabic-Bold.ttf",
            "Arabic-Regular.ttf",
        ],
        "bold": [
            "DejaVuSans-Bold.ttf",
            "LiberationSans-Bold.ttf",
            "NotoSans-Bold.ttf",
            "Arial-Bold.ttf",
        ],
    })

    # Default font directory names (relative to project root)
    _PROJECT_FONT_DIRS: List[str] = [
        "fonts",
        "assets/fonts",
        "pul7sar_visual_engine/fonts",
    ]

    def __init__(self, font_paths: Optional[List[str]] = None) -> None:
        """Initialize the FontResolver.

        Args:
            font_paths: Optional list of additional font directories to search.
                        These will be searched before system directories.
        """
        self._additional_font_paths = font_paths or []
        self._project_root = Path.cwd()

    def resolve(
        self,
        validated_payload: ValidatedPayload,
        resolved_configuration: ResolvedConfiguration,
    ) -> ResolvedFonts:
        """Resolve fonts for the validated rendering request.

        Args:
            validated_payload: The validated rendering request from Validator.
            resolved_configuration: The resolved configuration from ConfigurationResolver.

        Returns:
            ResolvedFonts: Immutable resolved fonts.

        Raises:
            FontError: If any required font cannot be found or loaded.
                This includes missing files, unreadable fonts, corrupt
                font files, and other font-related failures.

        The FontError may chain the original exception using
        Python exception chaining.
        """
        try:
            fonts: Dict[str, Any] = {}

            # Get font configuration
            config_data = dict(resolved_configuration.data)
            font_config = config_data.get("fonts", {})

            # Build search paths
            search_paths = self._build_search_paths(font_config)

            # Resolve specific fonts
            fonts = self._resolve_fonts(validated_payload, font_config, search_paths)

            # Validate required fonts are resolved
            self._validate_resolved_fonts(fonts)

            return ResolvedFonts(data=fonts)

        except FontError:
            raise
        except Exception as exc:
            raise FontError(
                f"Failed to resolve fonts: {exc}"
            ) from exc

    def _build_search_paths(self, font_config: Mapping[str, Any]) -> List[Path]:
        """Build the list of font search paths.

        Search order:
            1. Additional font paths (constructor argument)
            2. Project font directories
            3. System font directories

        Args:
            font_config: Font configuration from ResolvedConfiguration.

        Returns:
            List[Path]: List of search paths.
        """
        paths: List[Path] = []

        # Additional paths from constructor
        for path in self._additional_font_paths:
            resolved = Path(path)
            if resolved.exists():
                paths.append(resolved)

        # Project font directories
        project_dirs = font_config.get("project_dirs", [])
        if project_dirs:
            if isinstance(project_dirs, list):
                for dir_path in project_dirs:
                    resolved = self._project_root / dir_path
                    if resolved.exists() and resolved.is_dir():
                        paths.append(resolved)
            elif isinstance(project_dirs, str):
                resolved = self._project_root / project_dirs
                if resolved.exists() and resolved.is_dir():
                    paths.append(resolved)

        # Default project font directories
        for dir_name in self._PROJECT_FONT_DIRS:
            resolved = self._project_root / dir_name
            if resolved.exists() and resolved.is_dir():
                paths.append(resolved)

        # System font directories
        system_dirs = font_config.get("system_dirs", [])
        if system_dirs:
            if isinstance(system_dirs, list):
                for dir_path in system_dirs:
                    resolved = Path(dir_path)
                    if resolved.exists() and resolved.is_dir():
                        paths.append(resolved)
            elif isinstance(system_dirs, str):
                resolved = Path(system_dirs)
                if resolved.exists() and resolved.is_dir():
                    paths.append(resolved)

        for dir_path in self._SYSTEM_FONT_DIRS:
            resolved = Path(dir_path)
            if resolved.exists() and resolved.is_dir():
                paths.append(resolved)

        return paths

    def _resolve_fonts(
        self,
        validated_payload: ValidatedPayload,
        font_config: Mapping[str, Any],
        search_paths: List[Path],
    ) -> Dict[str, Path]:
        """Resolve all required fonts.

        Args:
            validated_payload: The validated payload.
            font_config: Font configuration from ResolvedConfiguration.
            search_paths: List of search paths.

        Returns:
            Dict[str, Path]: Mapping of font names to resolved paths.

        Raises:
            FontError: If a required font cannot be resolved.
        """
        resolved: Dict[str, Path] = {}
        payload_data = dict(validated_payload.data)

        # Check payload for font overrides
        payload_fonts = payload_data.get("fonts", {})
        if not isinstance(payload_fonts, dict):
            payload_fonts = {}

        # Font types to resolve
        font_types = ["headline", "body", "arabic", "bold", "fallback"]

        for font_type in font_types:
            # Check payload override first
            payload_font = payload_fonts.get(font_type)
            if payload_font and isinstance(payload_font, str):
                resolved_path = self._find_font_file(payload_font, search_paths)
                if resolved_path:
                    resolved[font_type] = resolved_path
                    continue
                # If payload explicitly specifies a font, it's required
                raise FontError(
                    f"Font '{font_type}' specified in payload not found: {payload_font}"
                )

            # Check configuration
            config_font = font_config.get(font_type)
            if config_font and isinstance(config_font, str):
                resolved_path = self._find_font_file(config_font, search_paths)
                if resolved_path:
                    resolved[font_type] = resolved_path
                    continue

            # Search by file name
            default_names = self._DEFAULT_FONT_NAMES.get(font_type, [])
            for name in default_names:
                resolved_path = self._find_font_file(name, search_paths)
                if resolved_path:
                    resolved[font_type] = resolved_path
                    break

            # If still not resolved and font type is required, try fallback
            if font_type not in resolved:
                # For non-critical fonts, try to reuse another font
                if font_type == "bold" and "headline" in resolved:
                    resolved["bold"] = resolved["headline"]
                elif font_type == "fallback":
                    # Use the first available font
                    for other_type in ["headline", "body", "bold"]:
                        if other_type in resolved:
                            resolved["fallback"] = resolved[other_type]
                            break
                elif font_type not in ["fallback", "bold"]:
                    # Required font types must be resolved
                    raise FontError(
                        f"Required font '{font_type}' could not be resolved"
                    )

        return resolved

    def _find_font_file(self, font_name: str, search_paths: List[Path]) -> Optional[Path]:
        """Find a font file in the search paths.

        Args:
            font_name: Name of the font file to find.
            search_paths: List of search paths.

        Returns:
            Optional[Path]: Path to the font file, or None if not found.
        """
        for search_path in search_paths:
            # Try exact match
            candidate = search_path / font_name
            if candidate.exists() and candidate.is_file():
                return candidate

            # Try with /fonts subdirectory
            candidate = search_path / "fonts" / font_name
            if candidate.exists() and candidate.is_file():
                return candidate

            # Try with /truetype subdirectory
            candidate = search_path / "truetype" / font_name
            if candidate.exists() and candidate.is_file():
                return candidate

        return None

    def _validate_resolved_fonts(self, fonts: Dict[str, Path]) -> None:
        """Validate resolved fonts.

        Checks that required font types have been resolved and that
        the files are readable.

        Args:
            fonts: Dictionary of resolved font paths.

        Raises:
            FontError: If validation fails.
        """
        # Check required font types
        required_types = ["headline", "body"]
        for required in required_types:
            if required not in fonts:
                raise FontError(
                    f"Required font '{required}' was not resolved"
                )

        # Check that all resolved paths exist and are readable
        for font_type, font_path in fonts.items():
            if not font_path.exists():
                raise FontError(
                    f"Resolved font '{font_type}' file does not exist: {font_path}"
                )
            if not font_path.is_file():
                raise FontError(
                    f"Resolved font '{font_type}' is not a file: {font_path}"
                )
            if not os.access(font_path, os.R_OK):
                raise FontError(
                    f"Resolved font '{font_type}' is not readable: {font_path}"
                )

    def resolve_font_path(self, font_name: str) -> Optional[Path]:
        """Resolve a single font by name.

        This is a convenience method for resolving individual fonts
        without requiring a full payload/configuration.

        Args:
            font_name: Name of the font file to resolve.

        Returns:
            Optional[Path]: Path to the font file, or None if not found.
        """
        # Build search paths with default configuration
        search_paths = self._build_search_paths({})
        return self._find_font_file(font_name, search_paths)