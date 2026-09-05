"""Safe concept-direction contracts before any original image generation.

The Concept Director converts approved story intelligence into a bounded visual
concept. It does not generate pixels and cannot override Fact Lock, identity, or
editorial-neutrality decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Optional

from engine.intelligence.models import VisualIntent
from engine.intelligence.neutrality import EditorialNeutralityGate, ResultVisualTreatment


class ConceptConstraint(str, Enum):
    NO_UNVERIFIED_IDENTITY = "no_unverified_identity"
    NO_UNVERIFIED_SIGNING = "no_unverified_signing"
    NO_INVENTED_RESULT = "no_invented_result"
    NO_HUMILIATION = "no_humiliation"
    NO_MOCKERY = "no_mockery"
    NO_DEGRADING_SYMBOLISM = "no_degrading_symbolism"
    NO_EXAGGERATED_SHAME = "no_exaggerated_shame"
    NO_SENSATIONAL_HARM = "no_sensational_harm"


@dataclass(frozen=True)
class ConceptBrief:
    family: str
    objective: str
    hero_entity: Optional[str] = None
    visual_copy: Optional[str] = None
    color_strategy: Optional[str] = None
    required_constraints: frozenset[ConceptConstraint] = field(default_factory=frozenset)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.family, str) or not self.family.strip():
            raise ValueError("family must be non-empty")
        if not isinstance(self.objective, str) or not self.objective.strip():
            raise ValueError("objective must be non-empty")
        constraints = frozenset(self.required_constraints)
        if any(not isinstance(item, ConceptConstraint) for item in constraints):
            raise TypeError("required_constraints must contain ConceptConstraint values")
        object.__setattr__(self, "required_constraints", constraints)
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class ProposedConcept:
    description: str
    claimed_constraints: frozenset[ConceptConstraint] = field(default_factory=frozenset)
    result_treatment: Optional[ResultVisualTreatment] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be non-empty")
        constraints = frozenset(self.claimed_constraints)
        if any(not isinstance(item, ConceptConstraint) for item in constraints):
            raise TypeError("claimed_constraints must contain ConceptConstraint values")
        object.__setattr__(self, "claimed_constraints", constraints)
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class ConceptDirectionError(ValueError):
    pass


class ConceptDirector:
    """Build and validate bounded concept briefs; never generate an image."""

    _FAMILY_CONSTRAINTS = {
        "results": frozenset({
            ConceptConstraint.NO_HUMILIATION,
            ConceptConstraint.NO_MOCKERY,
            ConceptConstraint.NO_DEGRADING_SYMBOLISM,
            ConceptConstraint.NO_EXAGGERATED_SHAME,
        }),
        "transfers": frozenset({ConceptConstraint.NO_UNVERIFIED_SIGNING}),
        "matchday": frozenset({ConceptConstraint.NO_INVENTED_RESULT}),
        "player_stories": frozenset({ConceptConstraint.NO_UNVERIFIED_IDENTITY}),
        "serious_news": frozenset({ConceptConstraint.NO_SENSATIONAL_HARM}),
    }

    def __init__(self, neutrality_gate: Optional[EditorialNeutralityGate] = None):
        self._neutrality_gate = neutrality_gate or EditorialNeutralityGate()

    def build_brief(
        self,
        intent: VisualIntent,
        *,
        extra_constraints: Iterable[ConceptConstraint] = (),
    ) -> ConceptBrief:
        if not isinstance(intent, VisualIntent):
            raise TypeError("intent must be VisualIntent")
        constraints = set(self._FAMILY_CONSTRAINTS.get(intent.family, frozenset()))
        constraints.update(extra_constraints)
        if intent.metadata.get("requires_identity_gate"):
            constraints.add(ConceptConstraint.NO_UNVERIFIED_IDENTITY)
        return ConceptBrief(
            family=intent.family,
            objective=intent.concept,
            hero_entity=intent.hero_entity,
            visual_copy=intent.visual_copy,
            color_strategy=intent.color_strategy,
            required_constraints=frozenset(constraints),
            metadata={"sentiment": intent.sentiment.value},
        )

    def validate(self, brief: ConceptBrief, concept: ProposedConcept) -> None:
        if not isinstance(brief, ConceptBrief):
            raise TypeError("brief must be ConceptBrief")
        if not isinstance(concept, ProposedConcept):
            raise TypeError("concept must be ProposedConcept")
        missing = brief.required_constraints - concept.claimed_constraints
        if missing:
            names = ", ".join(sorted(item.value for item in missing))
            raise ConceptDirectionError("concept did not acknowledge required constraints: " + names)
        if brief.family == "results":
            if concept.result_treatment is None:
                raise ConceptDirectionError("result concepts require explicit result treatment")
            self._neutrality_gate.assert_allowed(concept.result_treatment)
