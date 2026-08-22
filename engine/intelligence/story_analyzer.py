"""Deterministic article -> StoryBrief adapter for Phase 18.

This adapter is intentionally conservative. It does not perform web research,
LLM extraction, entity disambiguation, or sentiment inference from prose. It
normalizes explicit article fields into the canonical StoryBrief contract and
preserves uncertainty instead of inventing missing meaning.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Optional

from engine.intelligence.models import Sentiment, StoryBrief


class StoryAnalysisError(ValueError):
    """Raised when an article cannot be safely normalized into StoryBrief."""


class StoryAnalyzer:
    """Normalize explicit article metadata into a StoryBrief.

    Future analyzers may enrich the article before this adapter is called. This
    class itself remains deterministic so tests can distinguish extraction from
    verification and editorial inference.
    """

    _SENTIMENT_ALIASES = {
        "positive": Sentiment.POSITIVE,
        "celebratory": Sentiment.POSITIVE,
        "negative": Sentiment.NEGATIVE,
        "disappointing": Sentiment.NEGATIVE,
        "tense": Sentiment.TENSE,
        "controversial": Sentiment.TENSE,
        "neutral": Sentiment.NEUTRAL,
        "anticipatory": Sentiment.ANTICIPATORY,
        "anticipated": Sentiment.ANTICIPATORY,
        "serious": Sentiment.SERIOUS,
        "tragic": Sentiment.SERIOUS,
    }

    def analyze(
        self,
        article: Mapping[str, Any],
        *,
        overrides: Optional[Mapping[str, Any]] = None,
    ) -> StoryBrief:
        if not isinstance(article, Mapping):
            raise TypeError("article must be a mapping")
        if overrides is not None and not isinstance(overrides, Mapping):
            raise TypeError("overrides must be a mapping or None")

        data = dict(article)
        if overrides:
            data.update(dict(overrides))

        headline = self._required_text(
            data.get("headline", data.get("title")), "headline"
        )
        summary = data.get("summary", data.get("description", ""))
        if summary is None:
            summary = ""
        if not isinstance(summary, str):
            raise StoryAnalysisError("summary must be a string")

        secondary_entities = data.get("secondary_entities", ())
        if secondary_entities is None:
            secondary_entities = ()
        if isinstance(secondary_entities, str):
            raise StoryAnalysisError("secondary_entities must be a sequence, not str")
        try:
            secondary_entities = tuple(secondary_entities)
        except TypeError as exc:
            raise StoryAnalysisError("secondary_entities must be iterable") from exc
        for entity in secondary_entities:
            if not isinstance(entity, str) or not entity.strip():
                raise StoryAnalysisError(
                    "secondary_entities must contain non-empty strings"
                )

        raw_metadata = data.get("metadata", {})
        if raw_metadata is None:
            raw_metadata = {}
        if not isinstance(raw_metadata, Mapping):
            raise StoryAnalysisError("metadata must be a mapping")
        metadata = dict(raw_metadata)

        # Preserve useful source tracing without interpreting it as a fact.
        for source_key in ("link", "source", "published"):
            if source_key in data and source_key not in metadata:
                metadata[source_key] = data[source_key]

        return StoryBrief(
            headline=headline,
            summary=summary.strip(),
            sport=self._optional_text(data.get("sport"), "sport"),
            story_type=self._optional_text(data.get("story_type"), "story_type"),
            primary_entity=self._optional_text(
                data.get("primary_entity"), "primary_entity"
            ),
            secondary_entities=tuple(entity.strip() for entity in secondary_entities),
            sentiment=self._sentiment(data.get("sentiment")),
            event_status=self._optional_text(data.get("event_status"), "event_status"),
            location=self._optional_text(data.get("location"), "location"),
            metadata=metadata,
        )

    @staticmethod
    def _required_text(value: Any, field_name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise StoryAnalysisError(f"{field_name} must be a non-empty string")
        return value.strip()

    @staticmethod
    def _optional_text(value: Any, field_name: str) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise StoryAnalysisError(
                f"{field_name} must be a non-empty string or None"
            )
        return value.strip()

    def _sentiment(self, value: Any) -> Sentiment:
        if value is None:
            return Sentiment.NEUTRAL
        if isinstance(value, Sentiment):
            return value
        if not isinstance(value, str) or not value.strip():
            raise StoryAnalysisError("sentiment must be Sentiment, string, or None")
        key = value.strip().casefold()
        sentiment = self._SENTIMENT_ALIASES.get(key)
        if sentiment is None:
            raise StoryAnalysisError(f"unsupported sentiment: {value!r}")
        return sentiment
