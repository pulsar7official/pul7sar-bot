"""TemplateResolver — Resolves template classes from requests.

Per Phase 6 design:
    - Converts ValidatedPayload + ResolvedConfiguration to a concrete Template
    - Uses TemplateRegistry to retrieve template classes
    - Instantiates the template class and returns the instance
    - Selection priority:
        1. Template specified in ValidatedPayload
        2. Default template from ResolvedConfiguration
        3. Fallback template (if configured)
    - Does NOT execute templates
    - Does NOT read RenderContext
    - Does NOT produce Layers
    - Does NOT perform rendering
"""

from __future__ import annotations

from typing import Type

from engine.configuration.resolver import ResolvedConfiguration
from engine.core.exceptions import TemplateError
from engine.pipeline import TemplateProtocol
from engine.templates.registry import TemplateRegistry
from engine.validation.validator import ValidatedPayload


class TemplateResolver:
    """Resolves template instances from validated requests.

    Responsibilities:
        - Given ValidatedPayload and ResolvedConfiguration, determine
          which template to use
        - Retrieve the template class from TemplateRegistry
        - Instantiate the template class
        - Return the template instance

    Does NOT:
        - Execute templates
        - Read RenderContext
        - Produce Layers
        - Perform rendering
        - Hold per-request state

    Selection priority (highest to lowest):
        1. "template" field in ValidatedPayload.data
        2. "template.name" in ResolvedConfiguration.data["template"]
        3. "template" in ResolvedConfiguration.data (backward compatibility)
        4. Fallback: "default" (if registered)
    """

    # Default template name when no other selection works
    DEFAULT_TEMPLATE_NAME = "default"

    def __init__(
        self,
        registry: TemplateRegistry,
        default_template: str = DEFAULT_TEMPLATE_NAME,
    ) -> None:
        """Initialize the TemplateResolver.

        Args:
            registry: TemplateRegistry instance for retrieving templates.
            default_template: Default template name to use when no selection
                can be made from payload or configuration.
        """
        self._registry = registry
        self._default_template = default_template

    def resolve(
        self,
        validated_payload: ValidatedPayload,
        resolved_configuration: ResolvedConfiguration,
    ) -> TemplateProtocol:
        """Resolve a template instance from the request.

        Args:
            validated_payload: ValidatedPayload from Validator.
            resolved_configuration: ResolvedConfiguration from ConfigurationResolver.

        Returns:
            TemplateProtocol: An instance of the resolved template class.

        Raises:
            TemplateError: If no template can be resolved (name not found
                in registry and no fallback available), or if the template
                class cannot be instantiated.
        """
        # Try payload
        template_name = self._get_payload_template(validated_payload)
        if template_name:
            template_class = self._registry.get(template_name)
            return self._instantiate_template(template_class)

        # Try configuration
        template_name = self._get_configuration_template(resolved_configuration)
        if template_name:
            template_class = self._registry.get(template_name)
            return self._instantiate_template(template_class)

        # Try default
        if self._registry.has(self._default_template):
            template_class = self._registry.get(self._default_template)
            return self._instantiate_template(template_class)

        # No template found
        registered_names = self._registry.names
        if registered_names:
            raise TemplateError(
                f"No template resolved. Available templates: {', '.join(registered_names)}"
            )
        raise TemplateError(
            "No template resolved and no templates are registered in the registry"
        )

    def _get_payload_template(self, payload: ValidatedPayload) -> str | None:
        """Extract template name from ValidatedPayload.

        Args:
            payload: ValidatedPayload instance.

        Returns:
            str | None: Template name if found, None otherwise.
        """
        data = dict(payload.data)
        template = data.get("template")
        if template and isinstance(template, str):
            return template
        return None

    def _get_configuration_template(self, config: ResolvedConfiguration) -> str | None:
        """Extract template name from ResolvedConfiguration.

        Supports multiple possible paths:
            - config.data["template"]["name"]
            - config.data["template"] (if it's a string)

        Args:
            config: ResolvedConfiguration instance.

        Returns:
            str | None: Template name if found, None otherwise.
        """
        data = dict(config.data)

        # Try nested: template.name
        template_config = data.get("template")
        if isinstance(template_config, dict):
            name = template_config.get("name")
            if name and isinstance(name, str):
                return name

        # Try flat: template
        if isinstance(template_config, str):
            return template_config

        return None

    def _instantiate_template(self, template_class: Type[TemplateProtocol]) -> TemplateProtocol:
        """Instantiate a template class.

        Args:
            template_class: The template class to instantiate.

        Returns:
            TemplateProtocol: An instance of the template class.

        Raises:
            TemplateError: If the template class cannot be instantiated.
        """
        try:
            return template_class()
        except Exception as exc:
            raise TemplateError(
                f"Failed to instantiate template class {template_class.__name__}: {exc}"
            ) from exc