"""
Canvas abstraction for the PUL7SAR Visual Engine.

Canvas is the backend-independent drawing surface used exclusively by the
Renderer. It exposes a minimal set of primitive drawing operations and
contains no rendering logic, no business logic, and no knowledge of
templates, sports, or branding. Concrete implementations (Pillow, Skia,
Cairo, SVG, GPU backends, etc.) are provided elsewhere as backend adapters
and injected into the rendering pipeline; this module must never import
or reference any such backend.

Backend implementations are expected to raise ``RenderingError`` (see the
engine's exception hierarchy) whenever a drawing operation cannot be
completed, and must never let backend-specific exceptions escape across
the Canvas boundary. This module does not itself raise or import that
exception, since doing so would be behavior, not abstraction.
"""

from abc import ABC, abstractmethod
from typing import Any, Mapping


class Canvas(ABC):
    """
    Backend-independent drawing surface.

    Canvas exposes only primitive drawing operations. It does not know
    templates, does not know sports, does not know branding rules, and
    does not contain business or rendering logic. The Renderer is the
    only subsystem permitted to issue operations against a Canvas.

    Each operation accepts a generic, opaque ``properties`` mapping of
    renderer-specific parameters. Canvas does not interpret the meaning
    of these properties beyond passing them to the concrete backend.
    """

    @abstractmethod
    def draw_image(self, properties: Mapping[str, Any]) -> None:
        """Draw raster or vector imagery onto the canvas."""
        raise NotImplementedError

    @abstractmethod
    def draw_text(self, properties: Mapping[str, Any]) -> None:
        """Draw textual content onto the canvas."""
        raise NotImplementedError

    @abstractmethod
    def draw_shape(self, properties: Mapping[str, Any]) -> None:
        """Draw a geometric primitive onto the canvas."""
        raise NotImplementedError

    @abstractmethod
    def draw_gradient(self, properties: Mapping[str, Any]) -> None:
        """Draw a color transition onto the canvas."""
        raise NotImplementedError

    @abstractmethod
    def draw_texture(self, properties: Mapping[str, Any]) -> None:
        """Draw a reusable surface effect onto the canvas."""
        raise NotImplementedError

    @abstractmethod
    def draw_overlay(self, properties: Mapping[str, Any]) -> None:
        """Draw a reusable visual effect onto the canvas."""
        raise NotImplementedError
    @abstractmethod
    def get_result(self) -> Any:
        """Return the rendered image produced by the current rendering pass."""
        raise NotImplementedError
