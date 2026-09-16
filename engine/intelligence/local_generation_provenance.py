"""Deterministic provenance for zero-cost local PUL7SAR generations."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True)
class LocalGenerationProvenance:
    provider_id: str
    model_id: str
    backend: str
    seed: int
    request_id: str
    width: int
    height: int
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("provider_id", "model_id", "backend", "request_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if not isinstance(self.seed, int) or isinstance(self.seed, bool) or self.seed < 0:
            raise ValueError("seed must be a non-negative integer")
        for name in ("width", "height"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def as_provider_metadata(self) -> dict[str, Any]:
        return {
            "provider": self.provider_id,
            "model": self.model_id,
            "backend": self.backend,
            "seed": self.seed,
            "request_id": self.request_id,
            "width": self.width,
            "height": self.height,
            **dict(self.metadata),
        }
