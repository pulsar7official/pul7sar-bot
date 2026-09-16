"""Candidate-readiness gate separating composition studies from real news visuals.

Human composition studies may use non-identity placeholders, but a real
identity-led PUL7SAR candidate must carry exact verified-subject provenance.
This gate intentionally remains separate from publication readiness: a real
candidate can be visually reviewable while exact brand geometry or later
semantic/export gates still block publication.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.sports_editorial_scene import EditorialSceneFamily, SportsEditorialScenePlan
from engine.intelligence.verified_subject_compositor import VerifiedSubjectCompositionReceipt


class CandidateReadiness(str, Enum):
    COMPOSITION_STUDY_ONLY = "composition_study_only"
    REAL_CANDIDATE_READY = "real_candidate_ready"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class VisualCandidateReadinessDecision:
    status: CandidateReadiness
    real_candidate_allowed: bool
    identity_subject_required: bool
    verified_subject_provenance_accepted: bool
    blockers: tuple[str, ...]
    contract: str = "pul7sar-visual-candidate-readiness-v1"


class VisualCandidateReadinessGate:
    _IDENTITY_LED = {
        EditorialSceneFamily.TRANSFER_SIGNATURE,
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
    }

    def evaluate(
        self,
        scene: SportsEditorialScenePlan,
        *,
        composition_study: bool,
        subject_placeholder_used: bool = False,
        verified_subject: VerifiedSubjectCompositionReceipt | None = None,
    ) -> VisualCandidateReadinessDecision:
        if not isinstance(scene, SportsEditorialScenePlan):
            raise TypeError("scene must be SportsEditorialScenePlan")
        identity_required = scene.family in self._IDENTITY_LED
        blockers: list[str] = []

        if composition_study:
            if verified_subject is not None and verified_subject.publication_ready:
                blockers.append("study cannot consume a publication-ready subject receipt")
            return VisualCandidateReadinessDecision(
                status=CandidateReadiness.BLOCKED if blockers else CandidateReadiness.COMPOSITION_STUDY_ONLY,
                real_candidate_allowed=False,
                identity_subject_required=identity_required,
                verified_subject_provenance_accepted=False,
                blockers=tuple(blockers),
            )

        if subject_placeholder_used:
            blockers.append("subject placeholder is forbidden in a real news candidate")

        provenance_ok = False
        if identity_required:
            if verified_subject is None:
                blockers.append("identity-led real candidate requires verified subject composition receipt")
            else:
                if not verified_subject.identity_verified:
                    blockers.append("verified subject receipt does not prove identity")
                if verified_subject.generator_used:
                    blockers.append("verified subject pixels may not be generator-owned")
                if verified_subject.subject_placeholder_used:
                    blockers.append("verified subject receipt contains placeholder subject")
                if not verified_subject.subject_sha256 or not verified_subject.source_reference:
                    blockers.append("verified subject provenance is incomplete")
                provenance_ok = not blockers
        else:
            if verified_subject is not None and verified_subject.subject_placeholder_used:
                blockers.append("non-required subject receipt contains placeholder")
            provenance_ok = verified_subject is None or not blockers

        return VisualCandidateReadinessDecision(
            status=CandidateReadiness.REAL_CANDIDATE_READY if not blockers else CandidateReadiness.BLOCKED,
            real_candidate_allowed=not blockers,
            identity_subject_required=identity_required,
            verified_subject_provenance_accepted=provenance_ok,
            blockers=tuple(dict.fromkeys(blockers)),
        )
