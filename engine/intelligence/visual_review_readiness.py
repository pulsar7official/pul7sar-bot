"""Structural readiness gate before a PUL7SAR visual is shown for human review.

This gate does not pretend to judge pixels. It guarantees that a candidate study
was prepared from the right story family, copy budget, brand semantics and
benchmark before asking a human to spend time reviewing the actual image.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.brand_master_contract import APPROVED_PUL7SAR_BRAND_MASTER
from engine.intelligence.brand_master_geometry import BrandMasterGeometryState
from engine.intelligence.editorial_scene_copy_gate import EditorialSceneCopyGate
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualDecision
from engine.intelligence.visual_benchmark_suite import BenchmarkReviewKind, VisualBenchmarkCase, benchmark_for


class VisualReviewReadiness(str, Enum):
    BLOCKED = "blocked"
    STRUCTURAL_READY = "structural_ready"
    HUMAN_VISUAL_READY = "human_visual_ready"
    PUBLICATION_GEOMETRY_BLOCKED = "publication_geometry_blocked"


@dataclass(frozen=True)
class VisualReviewReadinessDecision:
    status: VisualReviewReadiness
    benchmark_id: str
    human_review_allowed: bool
    publication_geometry_ready: bool
    failures: tuple[str, ...]
    warnings: tuple[str, ...]
    contract: str = "pul7sar-visual-review-readiness-v1"


class VisualReviewReadinessGate:
    def __init__(self) -> None:
        self._copy = EditorialSceneCopyGate()

    def evaluate(
        self,
        decision: StoryToVisualDecision,
        *,
        headline: str,
        supporting_copy: str | None = None,
        brand_geometry: BrandMasterGeometryState | None = None,
    ) -> VisualReviewReadinessDecision:
        if not isinstance(decision, StoryToVisualDecision):
            raise TypeError("decision must be StoryToVisualDecision")
        APPROVED_PUL7SAR_BRAND_MASTER.assert_safe()
        scene = decision.sports_editorial_scene
        benchmark = benchmark_for(decision.plan.event)
        failures: list[str] = []
        warnings: list[str] = []

        copy = self._copy.evaluate(scene, headline=headline, supporting_copy=supporting_copy)
        failures.extend(copy.failures)
        if scene.metadata.get("contract") != "pul7sar-sports-editorial-scene-v2":
            failures.append("sports editorial scene contract is not current v2")
        if scene.brand_identity_id != APPROVED_PUL7SAR_BRAND_MASTER.identity_id:
            failures.append("sports editorial scene uses wrong brand identity")
        if scene.metadata.get("premium_editorial_not_data_card") is not True:
            failures.append("premium editorial policy is missing")
        if "legacy repository logo as canonical identity" not in scene.forbidden:
            failures.append("legacy logo rejection is missing")
        if "dense infographic copy" not in scene.forbidden:
            failures.append("dense infographic rejection is missing")
        if not self._benchmark_matches(scene.family.value, benchmark):
            failures.append("story scene family does not match canonical visual benchmark")

        geometry_ready = bool(brand_geometry and brand_geometry.ready)
        if not geometry_ready:
            warnings.append("exact two-part PUL7SAR master geometry is not registered; visual study may proceed but publication remains blocked")

        if failures:
            status = VisualReviewReadiness.BLOCKED
            human = False
        elif benchmark.review_kind is BenchmarkReviewKind.STRUCTURAL:
            status = VisualReviewReadiness.STRUCTURAL_READY
            human = False
        elif geometry_ready:
            status = VisualReviewReadiness.HUMAN_VISUAL_READY
            human = True
        else:
            status = VisualReviewReadiness.PUBLICATION_GEOMETRY_BLOCKED
            human = True

        return VisualReviewReadinessDecision(
            status=status,
            benchmark_id=benchmark.benchmark_id,
            human_review_allowed=human,
            publication_geometry_ready=geometry_ready,
            failures=tuple(failures),
            warnings=tuple(warnings),
        )

    @staticmethod
    def _benchmark_matches(scene_family: str, benchmark: VisualBenchmarkCase) -> bool:
        expected = {
            "transfer-signature-v1": "transfer_signature",
            "result-statement-v1": "result_statement",
            "verified-subject-news-v1": "verified_subject_news",
            "tactical-intelligence-v1": "tactical_board",
            "football-editorial-atmosphere-v1": "event_editorial",
        }
        return expected.get(benchmark.benchmark_id) == scene_family
