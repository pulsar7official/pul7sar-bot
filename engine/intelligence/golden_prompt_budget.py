"""Golden editorial prompt compaction without weakening exact-layer policy.

This module is deliberately benchmark-specific. The generic story-to-visual
compiler remains provider-neutral and expressive, while the current Golden
FLUX.2 Klein candidate receives a shorter scene description better suited to a
4B image model. Negative constraints, factual constraints, layout ownership,
VisualGrammar and VisualConcept metadata are preserved byte-for-byte at the
package-contract level.

Golden v6 differs from v5 in one important ownership rule: a generic PREVIEW does
not reserve football-pitch geometry. Brand, typography and exact factual content
remain deterministic, but sport-surface geometry is contextual/optional.
"""
from __future__ import annotations

from dataclasses import replace

from engine.intelligence.generation_package import GenerationPackage


GOLDEN_PROMPT_BUDGET_CONTRACT = "pul7sar-golden-prompt-budget-v2"
GOLDEN_BENCHMARK_ID = "golden-visual-season-opener-editorial-v6"
GOLDEN_SCENE_PROMPT_BUDGET_CHARS = 1200


_COMPACT_SCENE_PROMPT = (
    "Create one single continuous full-bleed editorial image: a premium European football season-opening environment at dusk in a deliberately non-identifying generic stadium world. "
    "Story-specific visual concept archetype: generative_event_atmosphere. Story-specific non-identifying sports atmosphere. Must not imply a specific real venue; include no specific real-person depiction. "
    "Build an asymmetric editorial hierarchy around one atmospheric focal anchor such as an illuminated tunnel opening, floodlight bank or luminous stand entrance, with coherent architecture, foreground depth and restrained supporter atmosphere. "
    "Use an oblique environmental wide-to-medium-wide viewpoint, stable natural perspective and useful negative space. Turf may appear only as a minor contextual glimpse and must never become the visual subject. "
    "No high-wide-central broadcast framing, no full-pitch master shot, no tactical diagram and no prominent centre-circle or halfway-line geometry. "
    "Keep the base fully unbranded, including platform names. Never use collage, montage, split-screen, grid, diptych, triptych, contact-sheet, framed-window, or image-within-image composition. "
    "The visual hero is anticipation, light, depth and place rather than playing-surface geometry."
)


class GoldenPromptBudget:
    """Compact only the explicitly identified current Golden editorial benchmark."""

    def compact(self, package: GenerationPackage, *, benchmark_id: str) -> GenerationPackage:
        if not isinstance(package, GenerationPackage):
            raise TypeError("package must be GenerationPackage")
        if benchmark_id != GOLDEN_BENCHMARK_ID:
            raise ValueError("golden prompt budget may only compact the current Golden editorial v6 benchmark")
        if package.metadata.get("generated_branding_allowed") is not False:
            raise ValueError("Golden prompt compaction requires generated branding to remain forbidden")
        if package.metadata.get("hybrid_base_scene_contract") is not True:
            raise ValueError("Golden prompt compaction requires the hybrid base-scene contract")
        if package.metadata.get("generated_sport_geometry_allowed") is not False:
            raise ValueError("Golden prompt compaction requires generated exact sport geometry to remain forbidden")
        if package.metadata.get("hybrid_surface_replacement_required") is not False:
            raise ValueError("Golden editorial v6 PREVIEW must not require deterministic pitch replacement")
        if package.metadata.get("visual_grammar_surface_visibility") != "context_only":
            raise ValueError("Golden editorial v6 PREVIEW must remain context_only")
        if package.metadata.get("visual_concept_selected_before_renderer") is not True:
            raise ValueError("Golden prompt compaction requires an approved pre-render visual concept")
        if len(_COMPACT_SCENE_PROMPT) > GOLDEN_SCENE_PROMPT_BUDGET_CHARS:
            raise RuntimeError("internal Golden scene prompt exceeds its locked character budget")
        lowered = _COMPACT_SCENE_PROMPT.casefold()
        if "pul7sar" in lowered or "pulsar" in lowered:
            raise RuntimeError("platform brand leaked into compact Golden scene prompt")

        metadata = dict(package.metadata)
        metadata.update({
            "benchmark": benchmark_id,
            "golden_prompt_contract": GOLDEN_PROMPT_BUDGET_CONTRACT,
            "golden_prompt_compacted": True,
            "golden_scene_prompt_budget_chars": GOLDEN_SCENE_PROMPT_BUDGET_CHARS,
            "golden_scene_prompt_chars": len(_COMPACT_SCENE_PROMPT),
            "golden_prompt_policy_boundaries_preserved": True,
        })
        return replace(package, scene_prompt=_COMPACT_SCENE_PROMPT, metadata=metadata)
