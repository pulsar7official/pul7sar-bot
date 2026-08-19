"""Bridge production article data to the Visual Engine request contract."""

from __future__ import annotations

from typing import Optional, Union

from PIL import Image

from engine.entities.model import EntityContext
from engine.entities.normalizer import create_entity_context
from engine.pipeline.pipeline import Pipeline


def render_article_with_engine(
    article: dict,
    *,
    engine: Pipeline,
    selected_image: Optional[Image.Image] = None,
    entity: Optional[Union[str, EntityContext]] = None,
) -> bytes:
    """Render an article without mutating caller-owned data.

    Entity identity is explicit in Phase 15. Automatic article-text entity
    detection remains out of scope and no code imports main.py.
    """
    if not isinstance(article, dict):
        raise TypeError(f"article must be dict, got {type(article).__name__}")

    headline = article.get("title", "")
    summary = article.get("summary", "")

    entity_context: Optional[EntityContext]
    if entity is None:
        entity_context = None
    elif isinstance(entity, EntityContext):
        entity_context = entity
    elif isinstance(entity, str):
        entity_context = create_entity_context(entity, kind="club")
    else:
        raise TypeError("entity must be str, EntityContext, or None")

    raw_request = {
        "template": "news",
        "platform": "telegram",
        "content": {
            "headline": headline,
            "summary": summary,
            "image": selected_image,
        },
    }

    if entity_context is not None and entity_context.key is not None:
        raw_request["entity"] = {
            "key": entity_context.key,
            "kind": entity_context.kind,
            "display_name": entity_context.display_name,
        }

    result = engine.execute(raw_request)

    if not isinstance(result, bytes):
        raise TypeError(
            f"Visual Engine expected bytes, got {type(result).__name__}"
        )
    if not result:
        raise ValueError("Visual Engine returned empty image bytes")
    return result
