# PUL7SAR Phase 18 — Dominant Entity Branding + Visual Inspection Gate

## Purpose
This change set corrects the Dynamic Brand rule for multi-entity sports stories and strengthens the post-generation QA boundary.

## 1. Story-dominant entity is not the same as primary subject
A story may contain two clubs while one side has an objectively stronger event role.

Examples:
- confirmed transfer: the destination/acquiring club owns the contextual 7 + pulse color,
- completed match: the verified winner owns the contextual 7 + pulse color,
- trophy: the verified champion owns it,
- qualification: the qualified side owns it,
- elimination: the eliminating side owns it only when explicitly verified,
- draw / preview / rumour: no objective dominant entity, so use default PUL7SAR red.

## 2. No prose guessing
`StoryDominantEntityResolver` does not infer winners from a news sentence. It accepts explicit verified fact slots and normalized statuses.

Added explicit schema slots:
- `winner_entity`
- `champion_entity`
- `qualified_entity`
- `eliminating_entity`

These slots remain Fact-Lock territory upstream.

## 3. Dynamic Brand flow

`Fact Lock`
→ `EventFactSchema`
→ `StoryDominantEntityResolver`
→ `EntityPaletteEvidence`
→ `DynamicBrandResolver`
→ deterministic `7 + pulse` accent

If palette evidence is missing or below threshold, the system falls back to `#E10600` rather than guessing.

The Dynamic Brand decision now preserves:
- accent color,
- dominant entity,
- whether the state is contextual,
- the objective dominance reason (`result_winner`, `transfer_destination`, etc.).

## 4. Execution-plan visibility
`VisualExecutionPlan` now carries:
- `dominant_entity`
- `story_dominance_reason`
- `dynamic_brand_accent_hex`
- `dynamic_brand_reason`

This makes the brand choice auditable instead of opaque.

## 5. Hybrid visual inspection capability gate
A successful PNG and deterministic pitch receipt are not treated as automatic visual QA.

`HybridVisualInspectionPolicy` evaluates actual local capability for:
- PNG observation,
- protected-region clutter inspection,
- semantic subject framing,
- semantic defect detection,
- forbidden visual / text / fake-logo detection,
- identity similarity when identity is required.

If semantic capability is incomplete, the system may still allow an engineering proof when deterministic evidence exists, but `publication_visual_gate_ready` remains false.

## 6. One-command Colab flow
`tools/phase18_colab_one_command.py` now reports visual-inspection readiness after deterministic football composition. It never equates generation success with publication readiness.

## 7. Tests
Added:
- `tests/test_phase18_story_dominant_entity.py`
- `tests/test_phase18_hybrid_visual_inspection_policy.py`

Expanded:
- `tests/test_phase18_editorial_planning_service.py`

Key regression cases include:
- transfer destination beats origin for brand color,
- match winner beats the other club even in a two-club story,
- draw returns to PUL7SAR red,
- transfer rumour never treats interested club as a completed winner,
- eliminated subject never receives winner branding,
- missing semantic visual inspection blocks automatic QA.

## Production isolation
All changes remain on `phase18/story-intelligence`; production `main.py` is intentionally untouched.
