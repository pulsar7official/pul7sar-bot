"""Verified story-moment assets for premium photo-led editorial concepts.

A story moment is stronger than generic atmosphere: it may depict the actual
match, decisive action, celebration, arrival or verified detail that the article
is about. A MATCH_ACTION is explicitly allowed to be real match evidence without
claiming it depicts the decisive goal. Person-bearing moments require identity
references, rights and checksum provenance.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from pathlib import Path


class StoryMomentKind(str, Enum):
    MATCH_ACTION = "match_action"
    DECISIVE_ACTION = "decisive_action"
    CELEBRATION = "celebration"
    ARRIVAL = "arrival"
    PRESS_MOMENT = "press_moment"
    VERIFIED_OBJECT_DETAIL = "verified_object_detail"


class StoryMomentRights(str, Enum):
    OWNER_SUPPLIED = "owner_supplied"
    LICENSED = "licensed"
    PUBLIC_DOMAIN = "public_domain"
    CREATIVE_COMMONS = "creative_commons"


@dataclass(frozen=True)
class VerifiedStoryMomentAsset:
    asset_id: str
    path: str
    sha256: str
    source_reference: str
    moment_kind: StoryMomentKind
    rights_basis: StoryMomentRights
    contains_people: bool
    verified_identity_ids: tuple[str, ...] = ()
    event_evidence: bool = True
    publication_allowed: bool = True

    def __post_init__(self) -> None:
        for name in ("asset_id", "path", "source_reference"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        digest = self.sha256.strip().lower()
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError("sha256 must be a hexadecimal SHA-256 digest")
        if not isinstance(self.moment_kind, StoryMomentKind):
            raise TypeError("moment_kind must be StoryMomentKind")
        if not isinstance(self.rights_basis, StoryMomentRights):
            raise TypeError("rights_basis must be StoryMomentRights")
        identities = tuple(str(value).strip() for value in self.verified_identity_ids if str(value).strip())
        object.__setattr__(self, "verified_identity_ids", identities)
        object.__setattr__(self, "sha256", digest)
        if self.contains_people and not identities:
            raise ValueError("PERSON_BEARING_STORY_MOMENT_REQUIRES_VERIFIED_IDENTITIES")
        if not self.event_evidence:
            raise ValueError("STORY_MOMENT_ASSET_MUST_BE_EXPLICIT_EVENT_EVIDENCE")

    def assert_file_integrity(self) -> Path:
        source = Path(self.path)
        if not source.is_file():
            raise FileNotFoundError(self.path)
        actual = sha256(source.read_bytes()).hexdigest()
        if actual != self.sha256:
            raise ValueError("VERIFIED_STORY_MOMENT_CHECKSUM_MISMATCH")
        if not self.publication_allowed:
            raise ValueError("VERIFIED_STORY_MOMENT_NOT_AUTHORIZED_FOR_PUBLICATION")
        return source


@dataclass(frozen=True)
class StoryMomentAdmissionReceipt:
    asset_id: str
    moment_kind: str
    source_sha256: str
    source_reference: str
    contains_people: bool
    verified_identity_ids: tuple[str, ...]
    event_evidence: bool
    publication_allowed: bool
    generator_used: bool = False
    contract: str = "pul7sar-verified-story-moment-admission-v1"


class VerifiedStoryMomentGate:
    """Admit a story photo only when provenance, rights and identities are explicit."""

    def admit(self, asset: VerifiedStoryMomentAsset) -> StoryMomentAdmissionReceipt:
        if not isinstance(asset, VerifiedStoryMomentAsset):
            raise TypeError("asset must be VerifiedStoryMomentAsset")
        asset.assert_file_integrity()
        return StoryMomentAdmissionReceipt(
            asset_id=asset.asset_id,
            moment_kind=asset.moment_kind.value,
            source_sha256=asset.sha256,
            source_reference=asset.source_reference,
            contains_people=asset.contains_people,
            verified_identity_ids=asset.verified_identity_ids,
            event_evidence=asset.event_evidence,
            publication_allowed=asset.publication_allowed,
        )
