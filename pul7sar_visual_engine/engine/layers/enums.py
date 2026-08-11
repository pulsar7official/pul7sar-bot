"""Closed LayerKind and LayerZone vocabularies.

Per 02_ARCHITECTURE.md, Section 11 (Layer System Specification) and
04_RENDERING_SPECIFICATION.md, Sections 8-9.

Both vocabularies are closed: exactly eight LayerKind values and
exactly four LayerZone values. No additional values may be introduced
without updating both frozen specifications first.

Using ``enum.Enum`` is the smallest implementation that satisfies the
"closed vocabulary" contract: constructing either enum with a value
outside its member set raises ``ValueError`` automatically, which is
the mechanism the Phase 1 tests rely on for rejecting unsupported
values.
"""

from __future__ import annotations

from enum import Enum, unique


@unique
class LayerKind(Enum):
    """Semantic type of a Layer. Exactly eight values (Rendering
    Specification, Section 8)."""

    BACKGROUND = "BACKGROUND"
    IMAGE = "IMAGE"
    TEXT = "TEXT"
    ICON = "ICON"
    SHAPE = "SHAPE"
    GRADIENT = "GRADIENT"
    TEXTURE = "TEXTURE"
    OVERLAY = "OVERLAY"


@unique
class LayerZone(Enum):
    """Zone a Layer belongs to within the rendering stack. Exactly
    four values (Rendering Specification, Section 9)."""

    BACKGROUND = "BACKGROUND"
    CONTENT = "CONTENT"
    BRAND = "BRAND"
    FOOTER = "FOOTER"
