"""In-memory deterministic entity-theme registry."""

from __future__ import annotations

from typing import Dict, Iterable, Optional

from engine.themes.model import ResolvedTheme


class ThemeRegistry:
    """O(1) theme lookup after startup composition."""

    def __init__(self) -> None:
        self._themes: Dict[str, ResolvedTheme] = {}

    def register(self, key: str, theme: ResolvedTheme) -> None:
        if not isinstance(key, str) or not key.strip():
            raise TypeError("key must be a non-empty str")
        if not isinstance(theme, ResolvedTheme):
            raise TypeError("theme must be ResolvedTheme")
        self._themes[key] = theme

    def get(self, key: Optional[str]) -> Optional[ResolvedTheme]:
        if key is None:
            return None
        return self._themes.get(key)

    def has(self, key: str) -> bool:
        return key in self._themes

    @property
    def keys(self) -> tuple[str, ...]:
        return tuple(self._themes.keys())
