# PUL7SAR Phase 18 — Change Set 162

## Golden Prompt Compatibility Fix

### Purpose

Restore two exact non-identifying Golden Hybrid v5 prompt markers required by the established CPU verification contract without weakening the new compact prompt budget introduced in Change Set 161.

The prior compact prompt preserved all semantic safety intent but changed two phrases that existing Golden handoff regression tests intentionally treat as fail-closed textual markers:

- `story-specific non-identifying sports atmosphere`
- `must not imply a specific real venue`

The Story Intelligence workflow therefore failed despite all companion visual-study workflows succeeding.

### Changes

1. `engine/intelligence/golden_prompt_budget.py`
   - keeps the compact Golden scene prompt below the locked 1,200-character scene budget;
   - restores both exact non-identifying markers;
   - preserves the existing unified-scene, no-collage, reserved-surface, deterministic-geometry, unbranded-base and platform-name exclusion markers;
   - keeps all negative and factual constraints outside the compact scene text unchanged.

2. `tests/test_phase18_golden_prompt_budget.py`
   - promotes the two restored phrases into the explicit `required_v5_markers` regression set so future compaction cannot silently remove them.

### Safety / gate preservation

No change was made to factual integrity, identity verification, sentiment/neutrality, `$0-local`, pinned model revisions, BF16, runtime/VRAM gates, seed/canvas/SHA locks, generated text/branding/exact-fact/entity-mark/sport-geometry prohibitions, Qwen semantic inspection, deterministic football geometry, provenance replay, Golden quality thresholds, exact brand/typography integrity, or SemanticPublicationGate.

No PNG, visual score, or GPU result is fabricated by this change set.
