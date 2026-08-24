"""Verified-subject composition for injury, statement and related reporting.

The verified visual asset is the hero. PUL7SAR may art-direct crop, light and
surrounding atmosphere, but it may not fabricate an injury pose, expression or
identity. The brand is intentionally quieter and side-positioned to protect the
portrait-led editorial hierarchy.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.adaptive_brand_placement import AdaptiveBrandPlacement, AdaptiveBrandPlacementResolver, BrandZone
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.result_statement_composition import NormalizedBox
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


@dataclass(frozen=True)
class VerifiedSubjectNewsComposition:
    subject_box: NormalizedBox
    headline_box: NormalizedBox
    context_box: NormalizedBox
    brand: AdaptiveBrandPlacement
    verified_subject_required: bool = True
    identity_reference_is_not_publishable_subject: bool = True
    fabricated_pose_allowed: bool = False
    fabricated_expression_allowed: bool = False
    fantasy_medical_scene_allowed: bool = False
    brand_must_not_overlap_face: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-verified-subject-news-composition-v1"

    def __post_init__(self) -> None:
        if not self.verified_subject_required:
            raise ValueError("VERIFIED_SUBJECT_NEWS_REQUIRES_VERIFIED_SUBJECT")
        if not self.identity_reference_is_not_publishable_subject:
            raise ValueError("IDENTITY_REFERENCE_MAY_NOT_BE_PROMOTED_TO_PUBLISHABLE_SUBJECT")
        if self.fabricated_pose_allowed or self.fabricated_expression_allowed:
            raise ValueError("VERIFIED_SUBJECT_NEWS_MAY_NOT_FABRICATE_POSE_OR_EXPRESSION")
        if self.fantasy_medical_scene_allowed:
            raise ValueError("INJURY_NEWS_MAY_NOT_USE_FANTASY_MEDICAL_SCENE")
        if not self.brand_must_not_overlap_face:
            raise ValueError("BRAND_MAY_NOT_OVERLAP_VERIFIED_FACE")
        if self.publication_ready:
            raise ValueError("COMPOSITION_CONTRACT_ALONE_CANNOT_AUTHORIZE_PUBLICATION")


class VerifiedSubjectNewsComposer:
    def __init__(self, brand_resolver: AdaptiveBrandPlacementResolver | None = None) -> None:
        self._brand = brand_resolver or AdaptiveBrandPlacementResolver()

    def plan(self, profile: PlatformImageProfile) -> VerifiedSubjectNewsComposition:
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        brand = self._brand.resolve(family=EditorialSceneFamily.VERIFIED_SUBJECT_NEWS, profile=profile)
        if brand.zone is not BrandZone.LOWER_RIGHT:
            raise ValueError("CANONICAL_VERIFIED_SUBJECT_BENCHMARK_EXPECTS_SIDE_SIGNATURE")

        portrait = profile.height >= profile.width
        if portrait:
            subject = NormalizedBox(0.06, 0.19, 0.57, 0.67)
            headline = NormalizedBox(0.55, 0.18, 0.37, 0.23)
            context = NormalizedBox(0.58, 0.44, 0.31, 0.12)
        else:
            subject = NormalizedBox(0.05, 0.12, 0.47, 0.78)
            headline = NormalizedBox(0.55, 0.17, 0.38, 0.28)
            context = NormalizedBox(0.58, 0.49, 0.30, 0.13)

        return VerifiedSubjectNewsComposition(
            subject_box=subject,
            headline_box=headline,
            context_box=context,
            brand=brand,
        )
