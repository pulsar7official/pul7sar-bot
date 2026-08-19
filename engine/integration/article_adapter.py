"""Bridge production article data to the Visual Engine request contract."""

from __future__ import annotations

from typing import Optional

from PIL import Image

from engine.pipeline.pipeline import Pipeline


def render_article_with_engine(
    article: dict,
    *,
    engine: Pipeline,
    selected_image: Optional[Image.Image] = None,
) -> bytes:
    """Render an article without mutating caller-owned data."""
    if not isinstance(article, dict):
        raise TypeError(f"article must be dict, got {type(article).__name__}")

    headline = article.get("title", "")
    summary = article.get("summary", "")

    raw_request = {
        "template": "news",
        "platform": "telegram",
        "content": {
            "headline": headline,
            "summary": summary,
            "image": selected_image,
        },
    }

    result = engine.execute(raw_request)

    if not isinstance(result, bytes):
        raise TypeError(
            f"Visual Engine expected bytes, got {type(result).__name__}"
        )
    if not result:
        raise ValueError("Visual Engine returned empty image bytes")
    return result
