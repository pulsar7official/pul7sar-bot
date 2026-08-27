"""Canonical Phase 18 visual benchmark cases for PUL7SAR review readiness."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.story_visual_editorial import EditorialEvent


class BenchmarkReviewKind(str, Enum):
    HUMAN_VISUAL = "human_visual"
    STRUCTURAL = "structural"


@dataclass(frozen=True)
class VisualBenchmarkCase:
    benchmark_id: str
    event: EditorialEvent
    goal: str
    must_show: tuple[str, ...]
    must_avoid: tuple[str, ...]
    review_kind: BenchmarkReviewKind = BenchmarkReviewKind.HUMAN_VISUAL


PHASE18_VISUAL_BENCHMARKS = (
    VisualBenchmarkCase(
        "transfer-signature-v1", EditorialEvent.TRANSFER_CONFIRMED,
        "premium transfer visual with verified hero subject, destination-club context and concise copy",
        ("one dominant verified subject", "verified club-linked contextual accent", "adaptive hybrid PUL7SAR brand placement", "negative space for concise headline"),
        ("full-pitch requirement", "dense infographic statistics", "legacy repository logo", "generated exact crest or readable brand text"),
    ),
    VisualBenchmarkCase(
        "result-statement-v1", EditorialEvent.RESULT,
        "high-impact result statement that celebrates the winner without degrading the loser",
        ("exact deterministic score", "balanced exact club identity", "winner-led hierarchy", "respectful treatment of losing side"),
        ("humiliation imagery", "mockery or shame symbolism", "generated score typography", "dense supporting paragraph"),
    ),
    VisualBenchmarkCase(
        "verified-subject-news-v1", EditorialEvent.INJURY,
        "restrained verified-subject news visual suitable for injury/statement coverage",
        ("verified source subject asset", "restrained editorial atmosphere", "concise factual headline"),
        ("fabricated injury pose", "invented emotional expression presented as fact", "fantasy spectacle", "unverified identity"),
    ),
    VisualBenchmarkCase(
        "tactical-intelligence-v1", EditorialEvent.TACTICS,
        "deterministic tactical visual where exact geometry and data are the hero",
        ("deterministic sport geometry", "exact verified tactical data", "clean technical hierarchy"),
        ("AI-generated exact pitch markings", "decorative full stadium as primary subject", "invented formation data"),
        BenchmarkReviewKind.STRUCTURAL,
    ),
    VisualBenchmarkCase(
        "record-data-editorial-v1", EditorialEvent.RECORD,
        "data-led editorial visual where the verified record is exact and visually dominant without generated numeric invention",
        ("exact deterministic record value", "verified data anchor", "clear data hierarchy", "supportive non-identifying atmosphere only when useful"),
        ("AI-generated exact numbers", "invented statistics", "decorative numbers unrelated to the story", "generated pseudo-text competing with exact data"),
        BenchmarkReviewKind.STRUCTURAL,
    ),
    VisualBenchmarkCase(
        "event-preview-context-v1", EditorialEvent.PREVIEW,
        "story-first match/event anticipation using contextual atmosphere without forcing a full pitch or unverifiable regulation geometry",
        ("single coherent event atmosphere", "story-led focal hierarchy", "usable headline negative space", "sport geometry either exact verified or visually indeterminate"),
        ("mandatory full-pitch master shot", "centered broadcast framing by default", "isolated or partial unverifiable goal geometry", "invented result or match state"),
    ),
    VisualBenchmarkCase(
        "football-editorial-atmosphere-v1", EditorialEvent.GENERAL,
        "premium football news visual that carries PUL7SAR atmosphere without forcing a person, pitch or infographic",
        (
            "single dominant editorial headline hierarchy",
            "dark premium sports depth",
            "verified contextual accent",
            "optional stadium light or tactical texture only when supportive",
            "adaptive PUL7SAR signature separated from the headline",
        ),
        (
            "legacy repository logo",
            "dense paragraph copy",
            "mandatory full football pitch",
            "decorative statistics unrelated to the story",
            "visual clutter competing with the headline",
        ),
    ),
)


def benchmark_for(event: EditorialEvent) -> VisualBenchmarkCase:
    for case in PHASE18_VISUAL_BENCHMARKS:
        if case.event is event:
            return case
    raise KeyError(f"no Phase 18 visual benchmark registered for {event.value}")
