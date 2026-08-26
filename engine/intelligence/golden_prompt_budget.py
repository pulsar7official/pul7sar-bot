"""Golden Hybrid v5 prompt compaction without weakening exact-layer policy.

This module is deliberately benchmark-specific. The generic story-to-visual
compiler remains provider-neutral and expressive, while the first Golden
FLUX.2 Klein candidate receives a shorter scene description better suited to a
4B image model. Negative constraints, factual constraints, layout ownership,
VisualGrammar and VisualConcept metadata are preserved byte-for-byte at the
package-contract level.
"""
from __future__ import annotations

from dataclasses import replace

from engine.intelligence.generation_package import GenerationPackage


GOLDEN_PROMPT_BUDGET_CONTRACT = "pul7sar-golden-prompt-budget-v1"
GOLDEN_BENCHMARK_ID = "golden-visual-season-opener-hybrid-v5"
GOLDEN_SCENE_PROMPT_BUDGET_CHARS = 1200


_COMPACT_SCENE_PROMPT = (
    "Single-frame photographic sports editorial scene at dusk. Build one coherent, premium, low-fantasy football-stadium atmosphere in a generic, non-identifiable venue: believable floodlights, deep stands, cinematic air, natural reflective turf texture, an indistinct distant crowd and at most one distant anonymous player silhouette. "
    "Keep one stable camera perspective, realistic scale and strong foreground-to-background depth. Preserve calm negative space around the central visual area and keep the lower third visually quiet for deterministic editorial composition. "
    "Show only restrained partial turf context in the lower frame; exact regulation football geometry belongs to the later code compositor. The stadium atmosphere is the visual hero."
)


class GoldenPromptBudget:
    """Compact only the current Golden v5 scene description.

    Exact prohibitions are intentionally *not* folded into this short prose.
    They remain in ``negative_constraints`` and ``factual_constraints`` and are
    subsequently compiled by the existing provider policy. This removes prompt
    repetition without deleting a safety or factual boundary.
    """

    def compact(self, package: GenerationPackage) -> GenerationPackage:
        if not isinstance(package, GenerationPackage):
            raise TypeError("package must be GenerationPackage")
        benchmark = package.metadata.get("benchmark")
        if benchmark != GOLDEN_BENCHMARK_ID:
            raise ValueError("golden prompt budget may only compact the current Golden Hybrid v5 benchmark")
        if package.metadata.get("generated_sport_geometry_allowed") is not False:
            raise ValueError("Golden prompt compaction requires generated sport geometry to remain forbidden")
        if package.metadata.get("generated_branding_allowed") is not False:
            raise ValueError("Golden prompt compaction requires generated branding to remain forbidden")
        if package.metadata.get("visual_concept_selected_before_renderer") is not True:
            raise ValueError("Golden prompt compaction requires an approved pre-render visual concept")
        if len(_COMPACT_SCENE_PROMPT) > GOLDEN_SCENE_PROMPT_BUDGET_CHARS:
            raise RuntimeError("internal Golden scene prompt exceeds its locked character budget")
        lowered = _COMPACT_SCENE_PROMPT.casefold()
        if "pul7sar" in lowered or "pulsar" in lowered:
            raise RuntimeError("platform brand leaked into compact Golden scene prompt")

        metadata = dict(package.metadata)
        metadata.update({
            "golden_prompt_contract": GOLDEN_PROMPT_BUDGET_CONTRACT,
            "golden_prompt_compacted": True,
            "golden_scene_prompt_budget_chars": GOLDEN_SCENE_PROMPT_BUDGET_CHARS,
            "golden_scene_prompt_chars": len(_COMPACT_SCENE_PROMPT),
            "golden_prompt_policy_boundaries_preserved": True,
        })
        return replace(package, scene_prompt=_COMPACT_SCENE_PROMPT, metadata=metadata)
