"""Deterministic typography contracts for PUL7SAR post-composition.

Text is rendered outside the image model. This module validates style and fit
against approved layout boxes before final export. It deliberately carries font
references/metrics contracts rather than bundling or guessing font files.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class TextRole(str, Enum):
    HEADLINE = "headline"
    SCORE = "score"
    SOCIAL_FOOTER = "social_footer"


class TextAlign(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


@dataclass(frozen=True)
class FontReference:
    font_id: str
    family: str
    weight: int = 700
    sha256: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.font_id, str) or not self.font_id.strip():
            raise ValueError("font_id must be non-empty")
        if not isinstance(self.family, str) or not self.family.strip():
            raise ValueError("family must be non-empty")
        if not isinstance(self.weight, int) or isinstance(self.weight, bool) or not 100 <= self.weight <= 900:
            raise ValueError("weight must be an integer between 100 and 900")
        if self.sha256 is not None:
            digest = self.sha256.strip().lower() if isinstance(self.sha256, str) else ""
            if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
                raise ValueError("font sha256 must be a 64-character hexadecimal digest")
            object.__setattr__(self, "sha256", digest)


@dataclass(frozen=True)
class TextStyle:
    role: TextRole
    font: FontReference
    min_size_px: int
    max_size_px: int
    max_lines: int
    line_height_ratio: float = 1.08
    align: TextAlign = TextAlign.LEFT
    uppercase_latin: bool = False
    allow_ellipsis: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.role, TextRole):
            raise TypeError("role must be TextRole")
        if not isinstance(self.font, FontReference):
            raise TypeError("font must be FontReference")
        if not isinstance(self.min_size_px, int) or not isinstance(self.max_size_px, int):
            raise TypeError("font sizes must be integers")
        if self.min_size_px <= 0 or self.max_size_px < self.min_size_px:
            raise ValueError("invalid font-size bounds")
        if not isinstance(self.max_lines, int) or self.max_lines <= 0:
            raise ValueError("max_lines must be positive")
        if not isinstance(self.line_height_ratio, (int, float)) or self.line_height_ratio < 1.0:
            raise ValueError("line_height_ratio must be >= 1.0")
        if not isinstance(self.align, TextAlign):
            raise TypeError("align must be TextAlign")


@dataclass(frozen=True)
class TextBox:
    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        for name in ("x", "y"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        for name in ("width", "height"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")


@dataclass(frozen=True)
class TextLayout:
    role: TextRole
    text: str
    font_id: str
    size_px: int
    lines: tuple[str, ...]
    box: TextBox
    align: TextAlign
    truncated: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("text must be non-empty")
        if not self.lines:
            raise ValueError("lines must not be empty")
        object.__setattr__(self, "lines", tuple(self.lines))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class TypographyDecision:
    allowed: bool
    failures: tuple[str, ...] = ()


class DeterministicTypographyEngine:
    """Fit approved text without silent truncation or model-generated lettering."""

    def fit(self, text: str, box: TextBox, style: TextStyle) -> TextLayout:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be non-empty")
        if not isinstance(box, TextBox):
            raise TypeError("box must be TextBox")
        if not isinstance(style, TextStyle):
            raise TypeError("style must be TextStyle")

        normalized = " ".join(text.split())
        if style.uppercase_latin:
            normalized = self._uppercase_latin_only(normalized)

        for size in range(style.max_size_px, style.min_size_px - 1, -1):
            max_lines_by_height = int(box.height // (size * style.line_height_ratio))
            line_limit = min(style.max_lines, max_lines_by_height)
            if line_limit <= 0:
                continue
            lines = self._wrap(normalized, box.width, size, line_limit)
            if lines is not None:
                return TextLayout(
                    role=style.role,
                    text=normalized,
                    font_id=style.font.font_id,
                    size_px=size,
                    lines=lines,
                    box=box,
                    align=style.align,
                    truncated=False,
                )

        if style.allow_ellipsis:
            size = style.min_size_px
            max_lines_by_height = int(box.height // (size * style.line_height_ratio))
            line_limit = min(style.max_lines, max_lines_by_height)
            if line_limit > 0:
                lines = self._wrap_with_ellipsis(normalized, box.width, size, line_limit)
                return TextLayout(style.role, normalized, style.font.font_id, size, lines, box, style.align, True)
        raise ValueError(f"{style.role.value} text does not fit approved box without prohibited overflow")

    def validate(self, layout: TextLayout, style: TextStyle) -> TypographyDecision:
        failures: list[str] = []
        if layout.role is not style.role:
            failures.append("text role/style mismatch")
        if layout.font_id != style.font.font_id:
            failures.append("unapproved font reference")
        if not style.min_size_px <= layout.size_px <= style.max_size_px:
            failures.append("font size outside approved bounds")
        if len(layout.lines) > style.max_lines:
            failures.append("line count exceeds approved maximum")
        if layout.truncated and not style.allow_ellipsis:
            failures.append("silent truncation is prohibited")
        return TypographyDecision(not failures, tuple(failures))

    @staticmethod
    def _wrap(text: str, width: int, size: int, max_lines: int) -> tuple[str, ...] | None:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = word if not current else current + " " + word
            if DeterministicTypographyEngine._measure(candidate, size) <= width:
                current = candidate
                continue
            if not current or DeterministicTypographyEngine._measure(word, size) > width:
                return None
            lines.append(current)
            current = word
            if len(lines) >= max_lines:
                return None
        if current:
            lines.append(current)
        if len(lines) > max_lines:
            return None
        return tuple(lines)

    @staticmethod
    def _wrap_with_ellipsis(text: str, width: int, size: int, max_lines: int) -> tuple[str, ...]:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = word if not current else current + " " + word
            if DeterministicTypographyEngine._measure(candidate, size) <= width:
                current = candidate
                continue
            if current:
                lines.append(current)
            current = word
            if len(lines) == max_lines - 1:
                break
        if len(lines) < max_lines:
            remaining = current
            while remaining and DeterministicTypographyEngine._measure(remaining + "…", size) > width:
                remaining = remaining[:-1].rstrip()
            lines.append((remaining or "") + "…")
        return tuple(lines[:max_lines])

    @staticmethod
    def _measure(text: str, size: int) -> float:
        # Conservative deterministic estimate until a concrete renderer supplies
        # exact glyph metrics. Arabic and non-ASCII letters receive a slightly
        # wider coefficient than narrow Latin punctuation/spaces.
        units = 0.0
        for char in text:
            if char.isspace():
                units += 0.34
            elif char in ".,:;!|'/()[]-–—":
                units += 0.38
            elif ord(char) > 127:
                units += 0.66
            elif char in "MW@#%&":
                units += 0.78
            else:
                units += 0.56
        return units * size

    @staticmethod
    def _uppercase_latin_only(text: str) -> str:
        return "".join(char.upper() if "a" <= char <= "z" else char for char in text)


class Pul7sarTypographyPolicy:
    """Role-specific defaults; concrete font IDs are supplied by configuration."""

    @staticmethod
    def headline(font: FontReference) -> TextStyle:
        return TextStyle(TextRole.HEADLINE, font, 34, 72, 3, 1.06, TextAlign.LEFT, False, False)

    @staticmethod
    def score(font: FontReference) -> TextStyle:
        return TextStyle(TextRole.SCORE, font, 34, 68, 1, 1.0, TextAlign.CENTER, True, False)

    @staticmethod
    def social_footer(font: FontReference) -> TextStyle:
        return TextStyle(TextRole.SOCIAL_FOOTER, font, 18, 30, 1, 1.0, TextAlign.CENTER, False, False)
