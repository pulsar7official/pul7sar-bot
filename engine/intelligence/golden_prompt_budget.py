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
GOLDEN_SCENE_PROMPT_BUDGET_CHARS = 1500


_COMPACT_SCENE_PROMPT = (
    "Create one single continuous full-bleed editorial image: premium European football season-opening anticipation at dusk in a deliberately non-identifying generic stadium. "
    "Build one asymmetric editorial hierarchy around a single illuminated players' tunnel mouth in the lower-left to mid-left as the dominant atmospheric focal anchor; let layered stands and crowd depth recede diagonally behind it, with believable floodlights only as a secondary depth cue. "
    "Keep the right-center calm and low-detail for later headline typography and keep the upper-left restrained for later brand placement. "
    "Use an oblique three-quarter environmental camera; no high-wide-central broadcast framing and no full-pitch master shot. "
    "Do not imply a specific real venue, club, match or person. Turf is optional context only and visually subordinate. Because playing-surface geometry is not required by this story, show no goal frame or goal net, no penalty-area or goal-area lines, no corner arc or corner flag, no centre circle or halfway line, and no other partial regulation pitch geometry. "
    "Never invent isolated football geometry merely to signal a stadium. If exact sport geometry is not a verified story dependency, keep it outside the frame, fully occluded, or visually indeterminate. Do not fabricate exact pitch markings, tactical diagrams or regulation geometry. "
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
        if package.metadata.get("hybrid_surface_replacement_required") is not False:
            raise ValueError("Golden editorial v6 PREVIEW must not require deterministic pitch replacement")
        if package.metadata.get("visual_grammar_surface_visibility") != "context_only":
            raise ValueError("Golden editorial v6 PREVIEW must remain context_only")
        if package.metadata.get("sport_geometry") != "contextual_optional_not_required":
            raise ValueError("Golden editorial v6 PREVIEW must keep sport geometry contextual and optional")
        if package.metadata.get("visual_concept_selected_before_renderer") is not True:
            raise ValueError("Golden prompt compaction requires an approved pre-render visual concept")
        if len(_COMPACT_SCENE_PROMPT) > GOLDEN_SCENE_PROMPT_BUDGET_CHARS:
            raise RuntimeError("internal Golden scene prompt exceeds its locked character budget")

        lowered = _COMPACT_SCENE_PROMPT.casefold()
        for marker in (
            "single illuminated players' tunnel mouth",
            "right-center calm and low-detail",
            "upper-left restrained",
            "no full-pitch master shot",
            "show no goal frame or goal net",
            "no penalty-area or goal-area lines",
            "no corner arc or corner flag",
            "no centre circle or halfway line",
            "keep it outside the frame, fully occluded, or visually indeterminate",
            "do not fabricate exact pitch markings",
            "tactical diagrams or regulation geometry",
        ):
            if marker not in lowered:
                raise RuntimeError("Golden v6 compact prompt lost its focal or preview geometry guardrails")
        if "pul7sar" in lowered or "pulsar" in lowered:
            raise RuntimeError("platform brand leaked into compact Golden scene prompt")

        metadata = dict(package.metadata)
        metadata.update({
            "benchmark": benchmark_id,
            "generated_sport_geometry_allowed": False,
            "partial_sport_geometry_allowed": False,
            "sport_geometry_integrity_policy": "exact_verified_or_visually_indeterminate",
            "partial_sport_geometry_hallucination_is_hard_failure": True,
            "golden_prompt_contract": GOLDEN_PROMPT_BUDGET_CONTRACT,
            "golden_prompt_compacted": True,
            "golden_scene_prompt_budget_chars": GOLDEN_SCENE_PROMPT_BUDGET_CHARS,
            "golden_scene_prompt_chars": len(_COMPACT_SCENE_PROMPT),
            "golden_prompt_policy_boundaries_preserved": True,
            "golden_focal_anchor": "illuminated_tunnel_lower_left",
            "golden_copy_negative_space": "right_center",
            "golden_brand_quiet_zone": "upper_left",
        })
        return replace(package, scene_prompt=_COMPACT_SCENE_PROMPT, metadata=metadata)
