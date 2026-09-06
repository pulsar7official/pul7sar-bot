"""Code-native PUL7SAR brand geometry contracts.

The final brand does not require a pre-rendered color-specific logo image. It is
built from a versioned deterministic recipe whose geometry is stable while the
7/pulse accent changes. The renderer remains fail-closed until an approved
wordmark font reference and approved pulse path are supplied.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DynamicBrandGeometryRecipe:
    recipe_id: str
    wordmark_text: str
    seven_index: int
    wordmark_font_id: Optional[str]
    pulse_path: tuple[tuple[float, float], ...]
    approved: bool
    approval_reference: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.recipe_id.strip():
            raise ValueError("recipe_id is required")
        if self.wordmark_text != "PUL7SAR":
            raise ValueError("wordmark_text must remain exactly PUL7SAR")
        if not 0 <= self.seven_index < len(self.wordmark_text) or self.wordmark_text[self.seven_index] != "7":
            raise ValueError("seven_index must point to the 7 in PUL7SAR")
        if self.wordmark_font_id is not None and not self.wordmark_font_id.strip():
            raise ValueError("wordmark_font_id must be non-empty or None")
        if len(self.pulse_path) not in {0} and len(self.pulse_path) < 4:
            raise ValueError("pulse_path must contain at least four points when supplied")
        for x, y in self.pulse_path:
            if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
                raise ValueError("pulse coordinates must be normalized 0..1")
        if self.approved:
            if self.wordmark_font_id is None:
                raise ValueError("approved brand recipe requires wordmark_font_id")
            if len(self.pulse_path) < 4:
                raise ValueError("approved brand recipe requires pulse geometry")
            if self.approval_reference is None or not self.approval_reference.strip():
                raise ValueError("approved brand recipe requires approval_reference")


class DynamicBrandGeometryRegistry:
    """Holds only explicit recipes; it never invents brand geometry."""

    def __init__(self, recipes: tuple[DynamicBrandGeometryRecipe, ...] = ()):
        self._recipes = {recipe.recipe_id: recipe for recipe in recipes}
        if len(self._recipes) != len(recipes):
            raise ValueError("brand recipe ids must be unique")

    def require_approved(self, recipe_id: str) -> DynamicBrandGeometryRecipe:
        try:
            recipe = self._recipes[recipe_id]
        except KeyError as exc:
            raise ValueError(f"unknown dynamic brand recipe: {recipe_id}") from exc
        if not recipe.approved:
            raise ValueError(f"dynamic brand recipe is not approved: {recipe_id}")
        return recipe
