"""Locale/script-aware typography policy for PUL7SAR Phase 18.

The editorial language may change per destination/source, but alignment must not
be guessed from a template. Arabic-dominant headlines use right alignment,
Latin-dominant headlines use left alignment, while scores/data remain centered.
Mixed strings use the dominant strong script and fail to a caller-supplied
neutral alignment when no script dominates.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.typography import TextAlign, TextRole


@dataclass(frozen=True)
class TypographyLocaleDecision:
    direction: str
    align: TextAlign
    arabic_count: int
    latin_count: int
    mixed: bool


class TypographyLocaleResolver:
    @staticmethod
    def _is_arabic(char: str) -> bool:
        code = ord(char)
        return (
            0x0600 <= code <= 0x06FF
            or 0x0750 <= code <= 0x077F
            or 0x08A0 <= code <= 0x08FF
            or 0xFB50 <= code <= 0xFDFF
            or 0xFE70 <= code <= 0xFEFF
        )

    def resolve(self, text: str, *, role: TextRole, neutral_align: TextAlign = TextAlign.CENTER) -> TypographyLocaleDecision:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text is required")
        if not isinstance(role, TextRole):
            raise TypeError("role must be TextRole")
        arabic = sum(1 for ch in text if self._is_arabic(ch))
        latin = sum(1 for ch in text if ch.isascii() and ch.isalpha())
        mixed = arabic > 0 and latin > 0

        if role in {TextRole.SCORE, TextRole.SOCIAL_FOOTER}:
            return TypographyLocaleDecision("neutral", TextAlign.CENTER, arabic, latin, mixed)
        if arabic > latin:
            return TypographyLocaleDecision("rtl", TextAlign.RIGHT, arabic, latin, mixed)
        if latin > arabic:
            return TypographyLocaleDecision("ltr", TextAlign.LEFT, arabic, latin, mixed)
        return TypographyLocaleDecision("neutral", neutral_align, arabic, latin, mixed)
