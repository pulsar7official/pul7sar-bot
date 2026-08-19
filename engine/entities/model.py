"""Immutable entity identity used by visual theme resolution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class EntityContext:
    """Identity context, deliberately separate from RenderContent."""

    key: Optional[str] = None
    kind: Optional[str] = None
    display_name: Optional[str] = None

    def __post_init__(self) -> None:
        for name in ("key", "kind", "display_name"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise TypeError(f"{name} must be str or None")
            if value is not None and not value.strip():
                raise ValueError(f"{name} cannot be empty or whitespace-only")
