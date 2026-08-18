"""Article-to-Visual-Engine integration adapter.

Phase 13 intentionally keeps this boundary minimal. The current Visual Engine
does not yet consume article headline, summary, or image content; those belong
to the production visual-content contract in a later phase.
"""

from __future__ import annotations

from typing import Mapping, Any

from engine.pipeline.pipeline import Pipeline


def render_article_with_engine(
    article: dict,
    *,
    engine: Pipeline,
) -> bytes:
    """Render an article through the current Visual Engine contract.

    The input article is deliberately not mutated. Phase 13 only proves the
    production integration path; the DefaultTemplate remains infrastructure-only.
    """
    if not isinstance(article, dict):
        raise TypeError(f"article must be a dict, got {type(article).__name__}")

    raw_request: Mapping[str, Any] = {
        "template": "default",
        "platform": "telegram",
    }

    result = engine.execute(raw_request)

    if not isinstance(result, bytes):
        raise TypeError(
            f"Visual Engine expected to return bytes, got {type(result).__name__}"
        )
    if not result:
        raise ValueError("Visual Engine returned empty image bytes")

    return result
