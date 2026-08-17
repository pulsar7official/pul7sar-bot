"""BaseTemplate — Abstract base class for all templates.

Per Phase 6 design:
    - Provides a common abstract base for concrete templates
    - Enforces the TemplateProtocol contract
    - Contains no rendering logic
    - Contains no business logic
    - To be extended by concrete template implementations

Concrete templates will override execute() to produce Layers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from engine.core.context import RenderContext
from engine.layers.layer import Layer
from engine.pipeline import TemplateProtocol


class BaseTemplate(ABC, TemplateProtocol):
    """Abstract base class for all templates.

    This class serves as the foundation for all concrete templates.
    It enforces the TemplateProtocol contract by requiring the execute()
    method to be implemented.

    Concrete template implementations must:
        1. Inherit from this class
        2. Implement execute(render_context) -> Sequence[Layer]
        3. Never render pixels directly
        4. Never access Canvas
        5. Never perform drawing

    This class contains no rendering logic, no business logic,
    and no knowledge of specific sports or content types.
    """

    @abstractmethod
    def execute(self, render_context: RenderContext) -> Sequence[Layer]:
        """Generate Layers for the given render context.

        This method is called by the Pipeline during the Template
        Execution stage. It must produce an ordered collection of
        Layer objects that describe the visual composition.

        Args:
            render_context: Immutable rendering request state.

        Returns:
            Sequence[Layer]: Ordered layers to be rendered.

        Raises:
            TemplateError: If the template cannot be executed.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement execute()"
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
