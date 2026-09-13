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
    _UNIFIED = "Render one single continuous full-bleed editorial scene in one physical world and one camera view; keep the entire canvas visually unified with no separate photo regions, montage structure, or panelized storytelling."
    _NO_SPLIT = "Use one uninterrupted photographic frame with continuous perspective and lighting across the whole canvas; do not divide the image with seams, borders, boxes, windows, or repeated frames."
    _NO_BRAND_TEXT = "Render a clean unbranded photographic base scene with no legible words, letters, numerals, platform names, sponsor writing, logos, wordmarks, watermarks, signatures, or pseudo-text anywhere in the generated image. Keep banners, screens, advertising boards, and kit sponsor areas visually neutral so all exact branding and typography can be added later by deterministic post-composition."
    _NO_RESERVED_MARKINGS = "Keep the reserved playing-surface context plain, grass-colored and completely unmarked so deterministic geometry can be applied after generation."
    _NON_IDENTIFYING_VENUE = "No specific identifiable real venue is permitted; treat any specific real venue identity without verified reference as forbidden. Use a deliberately non-identifying sports venue atmosphere with generic architecture and no distinctive landmark, signage, club-specific decoration, or other visual cue that could imply a particular real stadium or arena."
    _NO_REAL_PERSON = "No specific real-person depiction is permitted; keep the generated scene free of identifiable real people or celebrity likenesses and use crowd scale, silhouettes, or distant anonymous figures only when needed for atmosphere."
    _CONTEXTUAL_TURF_ONLY = "Keep any visible football turf incidental, subordinate and non-structural; the environmental story focal point must dominate and turf must never become the primary subject."
    _OBLIQUE_NOT_BROADCAST = "Use an asymmetric oblique environmental camera and avoid centered high-wide broadcast framing of the playing surface."
    _NO_TACTICAL_GEOMETRY = "Keep any incidental turf free of prominent tactical or regulation geometry such as a centre circle, halfway line, penalty boxes, or diagram-like markings."
    _NO_PARTIAL_UNVERIFIED_GEOMETRY = (
        "Keep regulation football structures entirely outside the frame, fully occluded, or visually indeterminate when exact sport geometry is not a verified story dependency. "
        "Do not introduce isolated goal frames or nets, penalty-area or goal-area lines, corner arcs or flags, centre circles, halfway lines, or other partial pitch geometry merely as stadium decoration; any visible regulation geometry must be physically coherent and story-authorized."
    )

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
        "no invented result": "Show the event approaching rather than already decided; create pre-event anticipation only and keep the sporting outcome completely unresolved.",
        "no sensational harm": "Use restrained factual visual drama and avoid graphic, sensational, or exploitative treatment of injury or harm.",
        "no collage or multi-panel layout": _UNIFIED,
        "no split-screen, grid, diptych, triptych, or contact-sheet framing": _NO_SPLIT,
        "no split-screen, grid, diptych, triptych or contact-sheet framing": _NO_SPLIT,
        "no image-within-image composition": "Keep all visual information inside the same coherent physical scene rather than placing secondary pictures or framed scenes inside the main image.",
        "no malformed football pitch geometry": "Render regulation association-football pitch geometry with straight perspective-consistent touchlines and goal lines, exactly one halfway line, exactly one circular centre circle centered on the halfway line, a correctly placed centre mark, two coherent penalty areas and goal areas aligned with the two goals, and physically plausible corner arcs.",
        "no duplicate, missing, warped, or invented field markings": "Keep every visible football marking structurally consistent with one real regulation pitch; do not duplicate the halfway line or centre circle, do not invent extra boxes or transverse lines, and keep all markings continuous under perspective.",
        "no football pitch markings in the reserved surface plane": _NO_RESERVED_MARKINGS,
        "no football pitch markings in the reserved surface context": _NO_RESERVED_MARKINGS,
        "no centre circle, halfway line, penalty boxes, goal-area markings or painted touchlines": "Show no painted football markings in the reserved surface region: no centre circle, halfway line, penalty or goal areas, touchlines, goal lines, arcs or decorative field diagrams.",
        "no full football pitch as the main visual subject": _CONTEXTUAL_TURF_ONLY,
        "no centered broadcast-style pitch composition": _OBLIQUE_NOT_BROADCAST,
        "no tactical diagram or prominent centre-circle/halfway-line geometry": _NO_TACTICAL_GEOMETRY,
        "no isolated or partial goal frame or goal net": _NO_PARTIAL_UNVERIFIED_GEOMETRY,
        "no penalty-area or goal-area lines": _NO_PARTIAL_UNVERIFIED_GEOMETRY,
        "no corner arc or corner flag": _NO_PARTIAL_UNVERIFIED_GEOMETRY,
        "no partial regulation football geometry whose physical placement cannot be verified": _NO_PARTIAL_UNVERIFIED_GEOMETRY,
        "no generated branding, wordmarks, readable text, or pseudo-text": _NO_BRAND_TEXT,
        "no generated branding, wordmarks, readable text, numerals or pseudo-text": _NO_BRAND_TEXT,
        "no specific identifiable real venue": _NON_IDENTIFYING_VENUE,
        "no specific real-person depiction": _NO_REAL_PERSON,
        "no fabricated identity": _NO_REAL_PERSON,
    }

    def compile(self, constraints: tuple[str, ...], *, supports_native_negative: bool) -> CompiledProviderConstraints:
        normalized = tuple(item.strip() for item in constraints if item and item.strip())
        if supports_native_negative:
            return CompiledProviderConstraints(ConstraintPromptMode.NATIVE_NEGATIVE, (), normalized, ())
        positive: list[str] = []
        untranslated: list[str] = []
        for item in normalized:
            instruction = self._REFRAMES.get(item.casefold())
            if instruction is None:
                untranslated.append(item)
            elif instruction not in positive:
                positive.append(instruction)
        return CompiledProviderConstraints(ConstraintPromptMode.POSITIVE_REFRAME, tuple(positive), (), tuple(untranslated))

    def assert_complete(self, compiled: CompiledProviderConstraints) -> None:
        if not compiled.complete:
            raise ValueError("provider constraint translation incomplete: " + ", ".join(compiled.untranslated_constraints))
