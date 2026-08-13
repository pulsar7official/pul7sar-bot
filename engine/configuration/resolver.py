"""ConfigurationResolver subsystem.

Per 02_ARCHITECTURE.md, Section 15, Step 1.2 and
04_RENDERING_SPECIFICATION.md, Section 4:

    ConfigurationResolver
        Input:  ValidatedPayload
        Output: ResolvedConfiguration (immutable)
        Raises: ConfigurationError
        Depends only on ValidatedPayload.
        Never validates the raw request.

This module defines:
    - ResolvedConfiguration: Immutable data contract (Phase 1)
    - ConfigurationResolver: Concrete implementation (Phase 1+)

The resolver reads configuration from environment variables (for
production compatibility) and optional config files (for future
flexibility). The configuration schema is intentionally left open
by the frozen specification; this implementation provides a minimal
set of keys required for rendering while remaining extensible.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from engine.core.exceptions import ConfigurationError
from engine.validation.validator import ValidatedPayload


@dataclass(frozen=True)
class ResolvedConfiguration:
    """Immutable output of ConfigurationResolver.

    Contains data only. Field schema is an implementation detail left
    open by the frozen specification; ``data`` holds the resolved
    configuration as an immutable mapping.
    """

    data: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "data", MappingProxyType(dict(self.data)))


class ConfigurationResolver:
    """Concrete implementation of the ConfigurationResolver contract.

    Resolves engine, template, and platform configuration for a
    validated rendering request.

    Stateless: holds no instance state, depends only on the input
    ValidatedPayload. Does not validate the request (Validator already
    did that). Does not know about assets, fonts, templates, rendering,
    or export.

    Configuration sources (in order of precedence):
        1. Environment variables (PUL7SAR_*)
        2. Optional config file (config/config.yaml or similar)
        3. Default values

    The resolved configuration includes:
        - engine: rendering backend, quality settings, dimensions
        - template: template name, styling overrides
        - platform: target platform, output format, dimensions
    """

    # Default configuration values
    _DEFAULTS: Mapping[str, Any] = MappingProxyType({
        "engine": {
            "backend": "pillow",
            "quality": 95,
            "width": 1280,
            "height": 720,
            "background_color": [15, 23, 42],
        },
        "template": {
            "name": "default",
            "font_family": "DejaVuSans",
            "font_size_headline": 48,
            "font_size_body": 28,
        },
        "platform": {
            "name": "telegram",
            "format": "JPEG",
            "max_file_size": 10 * 1024 * 1024,  # 10MB
        },
    })

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize the ConfigurationResolver.

        Args:
            config_path: Optional path to a configuration file (JSON or YAML).
                        If not provided, uses environment variables and defaults.
        """
        self._config_path = config_path
        self._file_config: Mapping[str, Any] = MappingProxyType({})

        if config_path and os.path.exists(config_path):
            self._file_config = self._load_config_file(config_path)

    def resolve(self, validated_payload: ValidatedPayload) -> ResolvedConfiguration:
        """Resolve configuration for the validated rendering request.

        Args:
            validated_payload: The validated rendering request from Validator.

        Returns:
            ResolvedConfiguration: Immutable resolved configuration.

        Raises:
            ConfigurationError: If configuration cannot be resolved.
                This includes missing required configuration, invalid values,
                or any other configuration-related failure.

        The ConfigurationError may chain the original exception using
        Python exception chaining.
        """
        try:
            # Start with defaults
            config = dict(self._DEFAULTS)

            # Override with file config if available
            config = self._deep_merge(config, dict(self._file_config))

            # Override with environment variables
            config = self._apply_environment_overrides(config)

            # Apply payload-specific overrides if present
            config = self._apply_payload_overrides(config, validated_payload)

            # Validate the resolved configuration
            self._validate_config(config)

            return ResolvedConfiguration(data=config)

        except ConfigurationError:
            raise
        except Exception as exc:
            raise ConfigurationError(
                f"Failed to resolve configuration: {exc}"
            ) from exc

    def _load_config_file(self, path: str) -> Mapping[str, Any]:
        """Load configuration from a file.

        Supports JSON and YAML (if PyYAML is installed).

        Args:
            path: Path to configuration file.

        Returns:
            Mapping[str, Any]: Loaded configuration.

        Raises:
            ConfigurationError: If the file cannot be read or parsed.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Try JSON first
            try:
                data = json.loads(content)
                return MappingProxyType(data)
            except json.JSONDecodeError:
                pass

            # Try YAML if available
            try:
                import yaml
                data = yaml.safe_load(content)
                if data is None:
                    data = {}
                return MappingProxyType(data)
            except ImportError:
                raise ConfigurationError(
                    f"Config file {path} is not valid JSON and PyYAML is not installed"
                )
            except yaml.YAMLError as exc:
                raise ConfigurationError(
                    f"Config file {path} is not valid YAML: {exc}"
                ) from exc

        except OSError as exc:
            raise ConfigurationError(
                f"Cannot read config file {path}: {exc}"
            ) from exc

    def _apply_environment_overrides(self, config: dict) -> dict:
        """Apply environment variable overrides to the configuration.

        Environment variables are prefixed with PUL7SAR_ and use
        underscore-delimited paths, e.g.:
            PUL7SAR_ENGINE_BACKEND=skia
            PUL7SAR_TEMPLATE_NAME=breaking
            PUL7SAR_PLATFORM_NAME=instagram

        Args:
            config: Current configuration dict.

        Returns:
            dict: Updated configuration with environment overrides.
        """
        result = dict(config)

        for key, value in os.environ.items():
            if not key.startswith("PUL7SAR_"):
                continue

            # Remove prefix and split into path parts
            path = key[8:].lower().split("_")
            if not path or not path[0]:
                continue

            # Convert value from string to appropriate type
            typed_value = self._parse_env_value(value)

            # Navigate/create nested structure
            current = result
            for part in path[:-1]:
                if part not in current:
                    current[part] = {}
                if not isinstance(current[part], dict):
                    # Can't override a non-dict with a nested path
                    continue
                current = current[part]

            # Set the final value
            if len(path) == 1:
                # Top-level key - handle specially to not override dicts
                current[path[0]] = typed_value
            else:
                current[path[-1]] = typed_value

        return result

    def _parse_env_value(self, value: str) -> Any:
        """Parse an environment variable value into a Python type.

        Supports:
            - booleans: true/false, yes/no, on/off, 1/0
            - integers: 123, -456
            - floats: 123.45, -456.78
            - JSON: [1, 2, 3], {"key": "value"}
            - strings (default)

        Args:
            value: Raw environment variable string.

        Returns:
            Any: Parsed value.
        """
        # Boolean
        lower = value.lower()
        if lower in ("true", "yes", "on", "1"):
            return True
        if lower in ("false", "no", "off", "0"):
            return False

        # Integer
        try:
            return int(value)
        except ValueError:
            pass

        # Float
        try:
            return float(value)
        except ValueError:
            pass

        # JSON (array or object)
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass

        # String (default)
        return value

    def _apply_payload_overrides(self, config: dict, payload: ValidatedPayload) -> dict:
        """Apply payload-specific configuration overrides.

        The validated payload may contain fields that influence
        configuration, such as:
            - template: template name to use
            - platform: target platform
            - dimensions: custom dimensions

        Args:
            config: Current configuration dict.
            payload: ValidatedPayload from Validator.

        Returns:
            dict: Updated configuration with payload overrides.
        """
        result = dict(config)

        data = dict(payload.data)

        # Template override
        if "template" in data and data["template"]:
            if "template" not in result:
                result["template"] = {}
            if isinstance(result["template"], dict):
                result["template"]["name"] = data["template"]

        # Platform override
        if "platform" in data and data["platform"]:
            if "platform" not in result:
                result["platform"] = {}
            if isinstance(result["platform"], dict):
                result["platform"]["name"] = data["platform"]

        # Dimensions override
        if "width" in data and "height" in data:
            if "engine" not in result:
                result["engine"] = {}
            if isinstance(result["engine"], dict):
                result["engine"]["width"] = data["width"]
                result["engine"]["height"] = data["height"]

        return result

    def _validate_config(self, config: dict) -> None:
        """Validate the resolved configuration.

        Checks that required keys exist and have valid values.

        Args:
            config: Resolved configuration dict.

        Raises:
            ConfigurationError: If validation fails.
        """
        # Engine config
        engine = config.get("engine")
        if not isinstance(engine, dict):
            raise ConfigurationError(
                "engine configuration must be a dictionary"
            )

        if "width" not in engine:
            raise ConfigurationError("engine.width is required")
        if not isinstance(engine["width"], (int, float)) or engine["width"] <= 0:
            raise ConfigurationError(
                f"engine.width must be a positive number, got {engine['width']!r}"
            )

        if "height" not in engine:
            raise ConfigurationError("engine.height is required")
        if not isinstance(engine["height"], (int, float)) or engine["height"] <= 0:
            raise ConfigurationError(
                f"engine.height must be a positive number, got {engine['height']!r}"
            )

        # Template config
        template = config.get("template")
        if not isinstance(template, dict):
            raise ConfigurationError(
                "template configuration must be a dictionary"
            )

        if "name" not in template:
            raise ConfigurationError("template.name is required")
        if not isinstance(template["name"], str) or not template["name"]:
            raise ConfigurationError(
                f"template.name must be a non-empty string, got {template['name']!r}"
            )

        # Platform config
        platform = config.get("platform")
        if not isinstance(platform, dict):
            raise ConfigurationError(
                "platform configuration must be a dictionary"
            )

        if "name" not in platform:
            raise ConfigurationError("platform.name is required")
        if not isinstance(platform["name"], str) or not platform["name"]:
            raise ConfigurationError(
                f"platform.name must be a non-empty string, got {platform['name']!r}"
            )

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """Deep merge two dictionaries.

        Args:
            base: Base dictionary (will be preserved).
            override: Override dictionary (takes precedence).

        Returns:
            dict: Merged dictionary.
        """
        result = dict(base)
        for key, value in override.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = ConfigurationResolver._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
