"""TemplateRegistry — Registry for template classes.

Per Phase 6 design:
    - Register template classes by name
    - Retrieve template classes by name
    - Prevent duplicate registration
    - Raise TemplateError for missing templates
"""

from __future__ import annotations

from typing import Dict, Type

from engine.core.exceptions import TemplateError
from engine.pipeline import TemplateProtocol


class TemplateRegistry:
    """Registry for template classes.

    Responsibilities:
        - Register template classes with a name
        - Retrieve template classes by name
        - Prevent duplicate registration
        - Raise TemplateError for missing templates

    This registry is stateless after construction (all state is
    contained in the registry itself, but it holds no per-request state).
    It can be reused across multiple rendering requests.

    The registry does NOT:
        - Select templates based on payload
        - Execute templates
        - Read RenderContext
        - Perform rendering
        - Resolve configuration
    """

    def __init__(self) -> None:
        """Initialize an empty template registry."""
        self._templates: Dict[str, Type[TemplateProtocol]] = {}

    def register(
        self,
        name: str,
        template_class: Type[TemplateProtocol],
    ) -> None:
        """Register a template class with a name.

        Args:
            name: Unique name for the template.
            template_class: The template class (must implement TemplateProtocol).

        Raises:
            TemplateError: If a template with the same name is already
                registered, or if the template_class is invalid.
        """
        if not name or not isinstance(name, str):
            raise TemplateError(
                f"Template name must be a non-empty string, got {name!r}"
            )

        if not isinstance(template_class, type):
            raise TemplateError(
                f"template_class must be a class, got {type(template_class)!r}"
            )

        # Verify that the class is a subclass of TemplateProtocol
        if not issubclass(template_class, TemplateProtocol):
            raise TemplateError(
                f"Template class {template_class.__name__} must implement "
                "TemplateProtocol (must have an execute() method returning "
                "Sequence[Layer])"
            )

        if name in self._templates:
            existing = self._templates[name]
            if existing is template_class:
                # Same class registered twice with same name - not an error
                return
            raise TemplateError(
                f"Template '{name}' is already registered with class "
                f"{existing.__name__}. Cannot register {template_class.__name__}"
            )

        self._templates[name] = template_class

    def get(self, name: str) -> Type[TemplateProtocol]:
        """Retrieve a registered template class by name.

        Args:
            name: Name of the template to retrieve.

        Returns:
            Type[TemplateProtocol]: The registered template class.

        Raises:
            TemplateError: If no template is registered with the given name.
        """
        if name not in self._templates:
            raise TemplateError(
                f"Template '{name}' is not registered"
            )

        return self._templates[name]

    def has(self, name: str) -> bool:
        """Check if a template is registered.

        Args:
            name: Name of the template to check.

        Returns:
            bool: True if registered, False otherwise.
        """
        return name in self._templates

    @property
    def names(self) -> tuple[str, ...]:
        """Get all registered template names.

        Returns:
            tuple[str, ...]: Tuple of registered template names.
        """
        return tuple(self._templates.keys())

    def clear(self) -> None:
        """Clear all registered templates.

        This is primarily for testing purposes.
        """
        self._templates.clear()