"""Deterministic entity-key normalization.

No imports from main.py.
No LLM.
No network requests.
No article-text parsing.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

from engine.entities.model import EntityContext


ENTITY_ALIASES = {
    "real_madrid": {
        "real madrid", "real madrid cf", "realmadrid", "madrid", "ريال مدريد"
    },
    "barcelona": {
        "barcelona", "fc barcelona", "barca", "barça", "برشلونة"
    },
    "liverpool": {"liverpool", "liverpool fc", "ليفربول"},
    "manchester_city": {
        "manchester city", "man city", "mancity", "مانشستر سيتي"
    },
    "manchester_united": {
        "manchester united", "man utd", "man united", "manutd", "مانشستر يونايتد"
    },
    "chelsea": {"chelsea", "chelsea fc", "تشيلسي"},
    "arsenal": {"arsenal", "arsenal fc", "آرسنال", "ارسنال"},
    "bayern_munich": {
        "bayern munich", "bayern", "fc bayern", "بايرن ميونخ"
    },
    "psg": {
        "psg", "paris saint-germain", "paris saint germain", "باريس سان جيرمان"
    },
    "juventus": {"juventus", "juve", "يوفنتوس"},
    "ac_milan": {"ac milan", "milan", "ميلان"},
    "inter_milan": {"inter milan", "inter", "إنتر", "انتر ميلان"},
}


def _canonical_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip().casefold()
    value = re.sub(r"[\s_-]+", " ", value)
    return value.strip()


def normalize_entity_key(input_key: Optional[str]) -> Optional[str]:
    """Normalize an explicit entity key/alias into a deterministic key."""
    if input_key is None:
        return None
    if not isinstance(input_key, str):
        raise TypeError("entity key must be str or None")
    if not input_key.strip():
        return None

    normalized = _canonical_text(input_key)

    for key, aliases in ENTITY_ALIASES.items():
        if normalized == _canonical_text(key):
            return key
        if normalized in {_canonical_text(alias) for alias in aliases}:
            return key

    return normalized.replace(" ", "_")


def create_entity_context(
    key: Optional[str],
    kind: Optional[str] = None,
    display_name: Optional[str] = None,
) -> EntityContext:
    """Create an immutable EntityContext from explicit identity input."""
    normalized_key = normalize_entity_key(key)
    if normalized_key is None:
        return EntityContext()

    if display_name is None:
        display_name = normalized_key.replace("_", " ").title()

    return EntityContext(
        key=normalized_key,
        kind=kind,
        display_name=display_name,
    )
