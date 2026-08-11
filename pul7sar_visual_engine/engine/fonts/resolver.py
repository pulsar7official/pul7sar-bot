"""Data contract owned by FontResolver.

Per 02_ARCHITECTURE.md, Section 15, Step 1.4 and
04_RENDERING_SPECIFICATION.md, Section 4:

    FontResolver
        Input:  ValidatedPayload, ResolvedConfiguration
        Output: ResolvedFonts (immutable)
        Raises: FontError
        Depends only on ValidatedPayload and ResolvedConfiguration.
        Does not depend on AssetResolver or Template.

This module currently defines only the ResolvedFonts data contract
(Phase 1). The FontResolver class itself is implemented in Phase 2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True)
class ResolvedFonts:
    """Immutable output of FontResolver.

    Contains data only. Field schema is an implementation detail left
    open by the frozen specification; ``data`` holds the resolved
    fonts as an immutable mapping.
    """

    data: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "data", MappingProxyType(dict(self.data)))
