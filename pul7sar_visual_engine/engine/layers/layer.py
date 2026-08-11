"""Layer -- one declarative drawing instruction.

Per 02_ARCHITECTURE.md, Section 11 (Layer System Specification) and
04_RENDERING_SPECIFICATION.md, Section 7:

    - A Layer never draws itself; it only describes drawing.
    - Contains exactly: kind, zone, z_index, properties.
    - Immutable after creation.
    - Contains no rendering logic, no business logic.
    - Must be serializable.

Layer ordering (zone order, then z_index, then insertion order) is a
Renderer-side responsibility (Architecture Section 11, "Layer
Ordering") and is implemented in Phase 2 alongside Renderer -- Layer
itself does not order or compare against other Layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Dict, Mapping

from engine.layers.enums import LayerKind, LayerZone


@dataclass(frozen=True)
class Layer:
    """One declarative, immutable drawing instruction.

    ``properties`` is a generic immutable mapping of renderer-specific
    parameters. Layer itself never interprets ``properties``
    (Architecture Section 11, "Layer Structure").
    """

    kind: LayerKind
    zone: LayerZone
    z_index: int
    properties: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.kind, LayerKind):
            raise TypeError(
                f"Layer.kind must be a LayerKind, got {type(self.kind)!r}"
            )
        if not isinstance(self.zone, LayerZone):
            raise TypeError(
                f"Layer.zone must be a LayerZone, got {type(self.zone)!r}"
            )
        if not isinstance(self.z_index, int) or isinstance(self.z_index, bool):
            raise TypeError(
                f"Layer.z_index must be an int, got {type(self.z_index)!r}"
            )
        object.__setattr__(
            self, "properties", MappingProxyType(dict(self.properties))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this Layer to a plain, JSON-compatible dict."""
        return {
            "kind": self.kind.value,
            "zone": self.zone.value,
            "z_index": self.z_index,
            "properties": dict(self.properties),
        }
