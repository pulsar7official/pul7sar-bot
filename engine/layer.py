"""Layer abstraction for the PUL7SAR Visual Engine.

Defines the declarative drawing instruction (`Layer`) and its two
classification enums (`LayerKind`, `LayerZone`). A Layer describes what
should be drawn; it never draws, loads, resolves, or interprets anything
itself. The Renderer is the only component permitted to interpret Layer
objects and convert them into pixels.
"""

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class LayerKind(Enum):
    """Semantic type of a Layer's visual content.

    Every Layer has exactly one LayerKind. Values are fixed by the
    LayerKind Specification; new kinds may be added in future engine
    versions without modifying existing templates.
    """

    BACKGROUND = "background"
    IMAGE = "image"
    TEXT = "text"
    ICON = "icon"
    SHAPE = "shape"
    GRADIENT = "gradient"
    TEXTURE = "texture"
    OVERLAY = "overlay"


class LayerZone(Enum):
    """Visual stacking zone a Layer belongs to.

    Zones are rendered in a fixed order: BACKGROUND, CONTENT, BRAND,
    FOOTER. Template implementations may only produce CONTENT layers;
    BACKGROUND, BRAND, and FOOTER are produced exclusively by
    BaseTemplate through OverlayManager.
    """

    BACKGROUND = "background"
    CONTENT = "content"
    BRAND = "brand"
    FOOTER = "footer"


def _frozen_properties(value: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return an immutable, read-only view over the given mapping."""
    return MappingProxyType(dict(value))


@dataclass(frozen=True, slots=True)
class Layer:
    """One declarative, immutable drawing instruction.

    A Layer never draws itself and contains no rendering, loading, or
    business logic. It describes *what* to draw via `kind`, *where* it
    stacks via `zone` and `z_index`, and *how* via the opaque
    `properties` mapping, which the Layer itself never interprets.

    Attributes:
        kind: The semantic type of visual content (see LayerKind).
        zone: The visual stacking zone this layer belongs to (see LayerZone).
        z_index: Ordering key within the zone. Layers render in the order
            of zone, then z_index, then insertion order. The renderer
            must never reorder layers automatically.
        properties: An immutable, generic mapping of renderer-specific
            parameters. Opaque to Layer; interpreted only by the Renderer.
    """

    kind: LayerKind
    zone: LayerZone
    z_index: int
    properties: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Enforce immutability of `properties` regardless of what the
        # caller passed in (e.g. a plain, mutable dict). This is the
        # only logic Layer performs, and it exists purely to preserve
        # the immutability invariant -- it does not interpret the data.
        object.__setattr__(self, "properties", _frozen_properties(self.properties))
