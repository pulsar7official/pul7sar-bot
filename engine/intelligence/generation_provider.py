"""Provider boundary for future original-scene generation.

The provider itself is intentionally abstract. The wrapper in this module
requires a valid GenerationAuthorization before any provider is invoked, making
that authorization gate an architectural requirement rather than a convention.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from engine.intelligence.concept_director import ConceptBrief, ProposedConcept
from engine.intelligence.generation_authorization import (
    GenerationAuthorization,
    GenerationAuthorizer,
)


@dataclass(frozen=True)
class OriginalSceneRequest:
    concept_brief: ConceptBrief
    proposed_concept: ProposedConcept
    output_width: int
    output_height: int
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.concept_brief, ConceptBrief):
            raise TypeError("concept_brief must be ConceptBrief")
        if not isinstance(self.proposed_concept, ProposedConcept):
            raise TypeError("proposed_concept must be ProposedConcept")
        for name in ("output_width", "output_height"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class OriginalSceneResult:
    provider: str
    asset_reference: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.provider, str) or not self.provider.strip():
            raise ValueError("provider must be non-empty")
        if not isinstance(self.asset_reference, str) or not self.asset_reference.strip():
            raise ValueError("asset_reference must be non-empty")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class OriginalSceneProvider(Protocol):
    def generate(self, request: OriginalSceneRequest) -> OriginalSceneResult: ...


class AuthorizedSceneGenerator:
    """The only Phase 18 path that should call an OriginalSceneProvider."""

    def __init__(
        self,
        provider: OriginalSceneProvider,
        *,
        authorizer: GenerationAuthorizer | None = None,
    ) -> None:
        self._provider = provider
        self._authorizer = authorizer or GenerationAuthorizer()

    def generate(
        self,
        request: OriginalSceneRequest,
        authorization: GenerationAuthorization,
    ) -> OriginalSceneResult:
        if not isinstance(request, OriginalSceneRequest):
            raise TypeError("request must be OriginalSceneRequest")
        self._authorizer.assert_authorized(authorization)
        result = self._provider.generate(request)
        if not isinstance(result, OriginalSceneResult):
            raise TypeError("provider must return OriginalSceneResult")
        return result
