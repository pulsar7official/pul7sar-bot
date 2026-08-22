"""Provider-neutral generation-session orchestration for PUL7SAR.

This module coordinates bounded zero-cost generation attempts. It never lowers
quality thresholds, never selects a rejected scene, and never depends on a
provider-native payload shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from engine.intelligence.candidate_selection import (
    BoundedRegenerationController,
    CandidateOutcome,
    CandidateSelectionResult,
    QualityFirstCandidateSelector,
    RegenerationPolicy,
)
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.provider_adapter import ProviderAdapterRegistry, ProviderRawGeneration


class GenerationAttemptProvider(Protocol):
    """Minimal provider boundary used by the session orchestrator."""

    provider_id: str

    def generate_attempt(
        self,
        package: GenerationPackage,
        *,
        attempt_number: int,
        candidate_count: int,
    ) -> tuple[ProviderRawGeneration, ...]: ...


@dataclass(frozen=True)
class AttemptDiagnostic:
    attempt_number: int
    candidate_count: int
    accepted_count: int
    rejection_reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.attempt_number <= 0:
            raise ValueError("attempt_number must be positive")
        if self.candidate_count < 0 or self.accepted_count < 0:
            raise ValueError("candidate counts must be non-negative")
        if self.accepted_count > self.candidate_count:
            raise ValueError("accepted_count cannot exceed candidate_count")
        object.__setattr__(self, "rejection_reasons", tuple(self.rejection_reasons))


@dataclass(frozen=True)
class GenerationSessionResult:
    outcome: CandidateOutcome
    selection: CandidateSelectionResult
    attempts_used: int
    diagnostics: tuple[AttemptDiagnostic, ...]
    provider_id: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.attempts_used <= 0:
            raise ValueError("attempts_used must be positive")
        if not isinstance(self.provider_id, str) or not self.provider_id.strip():
            raise ValueError("provider_id must be non-empty")
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class GenerationSessionOrchestrator:
    """Generate, normalize, evaluate, retry, and select without degraded fallback."""

    def __init__(
        self,
        *,
        adapters: ProviderAdapterRegistry,
        selector: QualityFirstCandidateSelector | None = None,
        regeneration: BoundedRegenerationController | None = None,
        minimum_quality_score: float = 0.90,
    ) -> None:
        if not 0.0 <= minimum_quality_score <= 1.0:
            raise ValueError("minimum_quality_score must be between 0 and 1")
        self._adapters = adapters
        self._selector = selector or QualityFirstCandidateSelector()
        self._regeneration = regeneration or BoundedRegenerationController(RegenerationPolicy())
        self.minimum_quality_score = minimum_quality_score

    def run(
        self,
        package: GenerationPackage,
        provider: GenerationAttemptProvider,
    ) -> GenerationSessionResult:
        provider_id = getattr(provider, "provider_id", None)
        if not isinstance(provider_id, str) or not provider_id.strip():
            raise ValueError("provider provider_id must be non-empty")

        diagnostics: list[AttemptDiagnostic] = []
        all_evidence = []
        attempts_used = 0

        while attempts_used < self._regeneration.policy.max_attempts:
            attempts_used += 1
            raw_candidates = tuple(
                provider.generate_attempt(
                    package,
                    attempt_number=attempts_used,
                    candidate_count=self._regeneration.policy.candidates_per_attempt,
                )
            )
            if len(raw_candidates) > self._regeneration.policy.candidates_per_attempt:
                raise ValueError("provider returned more candidates than requested")
            for raw in raw_candidates:
                if raw.provider_id != provider_id:
                    raise ValueError("provider returned raw generation for a different provider_id")
                all_evidence.append(self._adapters.normalize(raw, package))

            selection = self._selector.select(
                package,
                tuple(all_evidence),
                attempts_used=attempts_used,
            )
            accepted = [item for item in selection.evaluations if item.decision.accepted]
            diagnostics.append(
                AttemptDiagnostic(
                    attempt_number=attempts_used,
                    candidate_count=len(raw_candidates),
                    accepted_count=len(accepted),
                    rejection_reasons=selection.rejection_reasons,
                )
            )

            if selection.outcome is CandidateOutcome.ACCEPTED:
                assert selection.selected is not None
                if selection.selected.quality_score >= self.minimum_quality_score:
                    return GenerationSessionResult(
                        CandidateOutcome.ACCEPTED,
                        selection,
                        attempts_used,
                        tuple(diagnostics),
                        provider_id,
                        metadata={"minimum_quality_score": self.minimum_quality_score},
                    )

            if not self._regeneration.may_retry(attempts_used=attempts_used, selection=selection):
                break

        final_selection = self._selector.select(
            package,
            tuple(all_evidence),
            attempts_used=attempts_used,
        )
        reasons = list(final_selection.rejection_reasons)
        if final_selection.selected is not None and final_selection.selected.quality_score < self.minimum_quality_score:
            reasons.append(
                f"best accepted candidate quality {final_selection.selected.quality_score:.6f} is below minimum {self.minimum_quality_score:.6f}"
            )
        if final_selection.outcome is CandidateOutcome.ACCEPTED:
            final_selection = CandidateSelectionResult(
                CandidateOutcome.NO_ACCEPTABLE_SCENE,
                None,
                final_selection.evaluations,
                attempts_used,
                tuple(dict.fromkeys(reasons)),
            )
        return GenerationSessionResult(
            CandidateOutcome.NO_ACCEPTABLE_SCENE,
            final_selection,
            attempts_used,
            tuple(diagnostics),
            provider_id,
            metadata={"minimum_quality_score": self.minimum_quality_score},
        )
