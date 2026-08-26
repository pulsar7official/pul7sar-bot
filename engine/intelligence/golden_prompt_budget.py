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
    "Create one single continuous full-bleed editorial image: a premium European football season-opening scene at dusk in a deliberately non-identifying generic stadium. "
    "Story-specific visual concept archetype: generative_event_atmosphere. Story-specific non-identifying sports atmosphere. Must not imply a specific real venue; include no specific real-person depiction. "
    "Use believable floodlights, cinematic air, natural turf texture, distant crowd, one anonymous silhouette, generic architecture and no distinctive landmark. "
    "Keep one stable camera perspective, realistic scale, strong depth and calm editorial negative space. Use at most a restrained partial sport-surface context; do not make a full pitch the visual subject. "
    "Keep the reserved surface region plain and unmarked: no field/court/rink lines. The exact surface will be replaced by deterministic code after generation. "
    "Keep the base fully unbranded, including platform names. Never use collage, montage, split-screen, grid, diptych, triptych, contact-sheet, framed-window, or image-within-image composition. "
    "Exact regulation football geometry belongs to the later code compositor; the stadium atmosphere is the visual hero."
)


class GoldenPromptBudget:
    """Compact only the explicitly identified current Golden v5 benchmark.

    ``GenerationPackageCompiler`` intentionally does not propagate arbitrary
    benchmark labels from scene metadata into generic provider-neutral output.
    Therefore the benchmark identity is supplied explicitly by the trusted
    Golden builder instead of smuggling benchmark-only state into the generic
    compiler. Exact prohibitions remain in ``negative_constraints`` and
    ``factual_constraints`` and are compiled by the existing provider policy.
    """

    def compact(self, package: GenerationPackage, *, benchmark_id: str) -> GenerationPackage:
        if not isinstance(package, GenerationPackage):
            raise TypeError("package must be GenerationPackage")
        if benchmark_id != GOLDEN_BENCHMARK_ID:
            raise ValueError("golden prompt budget may only compact the current Golden Hybrid v5 benchmark")
        if package.metadata.get("generated_branding_allowed") is not False:
            raise ValueError("Golden prompt compaction requires generated branding to remain forbidden")
        if package.metadata.get("hybrid_base_scene_contract") is not True:
            raise ValueError("Golden prompt compaction requires the hybrid base-scene contract")
        reserved = tuple(str(item).casefold() for item in (package.metadata.get("reserved_base_scene_content") or ()))
        geometry_reserved = any(
            "playing-surface geometry" in item or "sport surface geometry" in item
            for item in reserved
        )
        if not geometry_reserved:
            raise ValueError("Golden prompt compaction requires sport geometry to remain code-owned")
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
