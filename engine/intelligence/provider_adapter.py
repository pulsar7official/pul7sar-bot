"""Provider-neutral adapter boundary for generated base-scene evidence.

Vendor-specific payloads must be normalized here. No downstream PUL7SAR domain
module may depend on a provider's native response shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from engine.intelligence.base_scene_quality import BaseSceneEvidence
from engine.intelligence.generation_package import GenerationPackage


@dataclass(frozen=True)
class ProviderRawGeneration:
    provider_id: str
    output_ref: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.provider_id, str) or not self.provider_id.strip():
            raise ValueError("provider_id must be non-empty")
        if not isinstance(self.output_ref, str) or not self.output_ref.strip():
            raise ValueError("output_ref must be non-empty")
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


class ProviderEvidenceAdapter(Protocol):
    """Translate provider-native output into trusted PUL7SAR evidence contracts."""

    provider_id: str

    def normalize(
        self,
        raw: ProviderRawGeneration,
        package: GenerationPackage,
    ) -> BaseSceneEvidence: ...


class AdapterMismatchError(ValueError):
    pass


class ProviderAdapterRegistry:
    """Resolve adapters explicitly by provider id; never guess payload format."""

    def __init__(self, adapters: tuple[ProviderEvidenceAdapter, ...] = ()) -> None:
        self._adapters: dict[str, ProviderEvidenceAdapter] = {}
        for adapter in adapters:
            self.register(adapter)

    def register(self, adapter: ProviderEvidenceAdapter) -> None:
        provider_id = getattr(adapter, "provider_id", None)
        if not isinstance(provider_id, str) or not provider_id.strip():
            raise ValueError("adapter provider_id must be non-empty")
        if provider_id in self._adapters:
            raise ValueError(f"duplicate provider adapter: {provider_id}")
        self._adapters[provider_id] = adapter

    def normalize(self, raw: ProviderRawGeneration, package: GenerationPackage) -> BaseSceneEvidence:
        adapter = self._adapters.get(raw.provider_id)
        if adapter is None:
            raise AdapterMismatchError(f"no evidence adapter registered for provider: {raw.provider_id}")
        evidence = adapter.normalize(raw, package)
        if evidence.provider_id != raw.provider_id:
            raise AdapterMismatchError("adapter returned evidence for a different provider")
        if evidence.output_ref != raw.output_ref:
            raise AdapterMismatchError("adapter changed the provider output reference")
        return evidence
