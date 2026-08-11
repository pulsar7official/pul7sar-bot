"""Data contract owned by AssetResolver.

Per 02_ARCHITECTURE.md, Section 15, Step 1.3 and
04_RENDERING_SPECIFICATION.md, Section 4:

    AssetResolver
        Input:  ValidatedPayload, ResolvedConfiguration
        Output: ResolvedAssets (immutable)
        Raises: AssetError
        Depends only on ValidatedPayload and ResolvedConfiguration.
        Does not depend on FontResolver or Template.

This module currently defines only the ResolvedAssets data contract
(Phase 1). The AssetResolver class itself is implemented in Phase 2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True)
class ResolvedAssets:
    """Immutable output of AssetResolver.

    Contains data only. Field schema is an implementation detail left
    open by the frozen specification; ``data`` holds the resolved
    assets as an immutable mapping.
    """

    data: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "data", MappingProxyType(dict(self.data)))
