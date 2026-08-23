"""Provider prompting policy for models without native negative prompts.

PUL7SAR never silently drops a forbidden visual constraint. Providers that do
not support negative prompts may only be used when every negative constraint can
be deterministically reframed into an equivalent positive instruction.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConstraintPromptMode(str, Enum):
    NATIVE_NEGATIVE = "native_negative"
    POSITIVE_REFRAME = "positive_reframe"


@dataclass(frozen=True)
class CompiledProviderConstraints:
    mode: ConstraintPromptMode
    positive_instructions: tuple[str, ...]
    native_negative_constraints: tuple[str, ...]
    untranslated_constraints: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.untranslated_constraints


class PromptConstraintCompiler:
    """Deterministically translate known PUL7SAR constraints for FLUX-like models."""

    _REFRAMES = {
        "no humiliation": "Keep every losing or secondary side dignified and respectful; focus emotional emphasis on the winner without degrading anyone.",
        "no mockery": "Use a serious professional sports-editorial tone with respectful treatment of every person, team, and institution.",
        "no degrading symbolism": "Use neutral professional sporting symbolism and avoid visual metaphors of degradation or ridicule.",
        "no exaggerated shame": "Show disappointment only in a realistic and proportionate sporting manner.",
        "no unverified signing": "Depict only the verified negotiation, interest, or approach stage; keep the scene clearly pre-signing and non-ceremonial.",
        "no fake signing": "Depict only the verified negotiation, interest, or approach stage; keep the scene clearly pre-signing and non-ceremonial.",
        "no fake signing ceremony": "Depict only the verified negotiation, interest, or approach stage; keep the scene clearly pre-signing and non-ceremonial.",
        "no contract signature": "Keep the scene away from contracts, signing desks, signature gestures, presentation shirts, and official-announcement staging.",
        "no completed signing ceremony": "Keep the scene in an unresolved negotiation/interest context rather than a completed transfer presentation.",
        "no invented result": "Create pre-event anticipation only and keep the sporting outcome completely unresolved.",
        "no sensational harm": "Use restrained factual visual drama and avoid graphic, sensational, or exploitative treatment of injury or harm.",
        "no collage or multi-panel layout": (
            "Render one single continuous full-bleed editorial scene in one physical world and one camera view; "
            "keep the entire canvas visually unified with no separate photo regions, montage structure, or panelized storytelling."
        ),
        "no split-screen, grid, diptych, triptych, or contact-sheet framing": (
            "Use one uninterrupted photographic frame with continuous perspective and lighting across the whole canvas; "
            "do not divide the image with seams, borders, boxes, windows, or repeated frames."
        ),
        "no image-within-image composition": (
            "Keep all visual information inside the same coherent physical scene rather than placing secondary pictures or framed scenes inside the main image."
        ),
        "no malformed football pitch geometry": (
            "Render regulation association-football pitch geometry with straight perspective-consistent touchlines and goal lines, exactly one halfway line, exactly one circular centre circle centered on the halfway line, a correctly placed centre mark, two coherent penalty areas and goal areas aligned with the two goals, and physically plausible corner arcs."
        ),
        "no duplicate, missing, warped, or invented field markings": (
            "Keep every visible football marking structurally consistent with one real regulation pitch; do not duplicate the halfway line or centre circle, do not invent extra boxes or transverse lines, and keep all markings continuous under perspective."
        ),
    }

    def compile(
        self,
        constraints: tuple[str, ...],
        *,
        supports_native_negative: bool,
    ) -> CompiledProviderConstraints:
        normalized = tuple(item.strip() for item in constraints if item and item.strip())
        if supports_native_negative:
            return CompiledProviderConstraints(
                ConstraintPromptMode.NATIVE_NEGATIVE,
                (),
                normalized,
                (),
            )

        positive: list[str] = []
        untranslated: list[str] = []
        for item in normalized:
            key = item.casefold()
            instruction = self._REFRAMES.get(key)
            if instruction is None:
                untranslated.append(item)
            elif instruction not in positive:
                positive.append(instruction)
        return CompiledProviderConstraints(
            ConstraintPromptMode.POSITIVE_REFRAME,
            tuple(positive),
            (),
            tuple(untranslated),
        )

    def assert_complete(self, compiled: CompiledProviderConstraints) -> None:
        if not compiled.complete:
            raise ValueError(
                "provider constraint translation incomplete: "
                + ", ".join(compiled.untranslated_constraints)
            )
