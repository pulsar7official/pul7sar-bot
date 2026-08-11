"""Data contract owned by ConfigurationResolver.

Per 02_ARCHITECTURE.md, Section 15, Step 1.2 and
04_RENDERING_SPECIFICATION.md, Section 4:

    ConfigurationResolver
        Input:  ValidatedPayload
        Output: ResolvedConfiguration (immutable)
        Raises: ConfigurationError
        Depends only on ValidatedPayload. Never validates the raw
        request.

This module currently defines only the ResolvedConfiguration data
contract (Phase 1). The ConfigurationResolver class itself is
implemented in Phase 2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


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
