"""Concise PUL7SAR sports copy built from verified slots only.

The builder complements the headline grammar with a short post sentence. It does
not invent context. Upstream extraction/verification must supply the exact fact
and optional verified context; the copy layer only orders and compresses them.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.editorial_headline_grammar import EditorialHeadlineGrammar, HeadlineDecision, HeadlineInput


@dataclass(frozen=True)
class EditorialCopyInput:
    headline_input: HeadlineInput
    verified_context: str | None = None
    max_body_chars: int = 180

    def __post_init__(self) -> None:
        if self.verified_context is not None and not isinstance(self.verified_context, str):
            raise TypeError("verified_context must be str or None")
        if not isinstance(self.max_body_chars, int) or isinstance(self.max_body_chars, bool) or self.max_body_chars < 80:
            raise ValueError("max_body_chars must be an integer >= 80")


@dataclass(frozen=True)
class EditorialCopyDecision:
    headline: HeadlineDecision
    post_text: str
    visual_copy: str
    context_used: bool
    compact: bool


class EditorialCopyBuilder:
    def __init__(self) -> None:
        self._headlines = EditorialHeadlineGrammar()

    def build(self, data: EditorialCopyInput) -> EditorialCopyDecision:
        headline = self._headlines.compose(data.headline_input)
        fact = " ".join(data.headline_input.fact_phrase.strip().rstrip(".،؛").split())
        subject = " ".join(data.headline_input.subject.strip().split())
        base = f"{subject} {fact}."
        context_used = False
        context = ""
        if data.verified_context:
            normalized = " ".join(data.verified_context.strip().rstrip(".،؛").split())
            if normalized:
                candidate = f"{base} {normalized}."
                if len(candidate) <= data.max_body_chars:
                    base = candidate
                    context = normalized
                    context_used = True
        if len(base) > data.max_body_chars:
            # Do not rewrite facts into invented paraphrases. If the verified fact
            # itself is too long, keep the headline as visual copy and mark body
            # as non-compact for upstream editorial compression.
            compact = False
        else:
            compact = True
        visual_copy = headline.headline if headline.safe_for_visualization else subject
        return EditorialCopyDecision(
            headline=headline,
            post_text=base,
            visual_copy=visual_copy,
            context_used=context_used,
            compact=compact,
        )
