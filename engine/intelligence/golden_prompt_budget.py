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
    "Create one single continuous full-bleed editorial image: premium European football season-opening anticipation at dusk in a deliberately non-identifying generic stadium. "
    "Use one asymmetric editorial hierarchy around a dominant atmospheric focal anchor such as an illuminated tunnel, floodlight bank or stand entrance, with layered architecture, crowd depth, realistic scale and useful negative space. "
    "Use an oblique three-quarter environmental camera; no high-wide-central broadcast framing and no full-pitch master shot. "
    "Do not imply a specific real venue, club, match or person. Turf is optional context only and visually subordinate; do not fabricate exact pitch markings, tactical diagrams or regulation geometry. "
    "Keep the base fully unbranded, including platform names, readable text, numerals, logos and pseudo-text. "
    "Never use collage, montage, split-screen, grid, diptych, triptych, contact-sheet, framed-window or image-within-image composition."
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
