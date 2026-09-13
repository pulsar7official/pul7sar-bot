# PUL7SAR Phase 18 — Change Sets 085–087

## Change Set 085 — Base-scene layer leakage QA

Added `engine/intelligence/visual_layer_qa.py` and `tests/test_phase18_visual_layer_qa.py`.

This gate is intentionally narrower than the final `HybridVisualQualityGate`: it checks whether the generated base scene invaded layers it does not own before deterministic/verified composition begins. It blocks generated text, PUL7SAR/platform branding, exact numbers, club/team/competition marks, unverified identity, and generated sport geometry whenever the hybrid layer plan assigns those responsibilities to deterministic code or verified assets.

The gate consumes inspection evidence; it does not pretend to perform computer vision itself and does not replace `SemanticPublicationGate` or Golden visual-quality review.

## Change Set 086 — Complete football marking primitives and regression preflight

Strengthened `engine/intelligence/football_pitch_geometry.py` so the stable 105m × 68m football contract includes the centre mark, two penalty marks, both 9.15m penalty arcs and all four 1m corner arcs in addition to the existing lines, centre circle, penalty areas and goal areas.

Strengthened:
- `tests/test_phase18_football_pitch_geometry.py`
- `tests/test_phase18_football_pitch_projection.py`
- `engine/intelligence/__init__.py`
- `tools/phase18_colab_runner.py`

The existing projective renderer path was reviewed and confirmed to consume these primitives through `project_all_markings()` and the Pillow renderer. Colab CPU preflight now includes geometry and projection regression modules before GPU expenditure.

## Change Set 087 — Golden v4 CPU verification alignment

Branch review found `.github/workflows/phase18-intelligence.yml` still using stale Golden-v2 request/artifact names while the active builder, smoke coordinator and Colab runner were already locked to Golden v4.

The workflow now:
- builds `golden-general-season-opener-v4-001`,
- labels handoff and candidate artifacts as v4,
- explicitly asserts `pul7sar-golden-batch-v4`,
- asserts `single_continuous_scene`,
- asserts `association_football_regulation_pitch`,
- asserts `generated_branding_allowed=false`,
- asserts `brand_composition_policy=exact_assets_only_after_generation` before artifact upload.

Added `tests/test_phase18_intelligence_workflow.py` to reject stale v2 request/artifact names and preserve Phase-18-only, CPU-safe, no-secret workflow isolation.

## Documentation reconciliation

Historical change-set filenames are retained when renaming would add churn, but their contents now state canonical numbering. Duplicate provisional documentation created during the numbering collision was removed. The authoritative sequence is recorded in `docs/PHASE18_IMPLEMENTATION_LOG.md`.

## Safety

No change was made to `main`, `main.py`, Telegram production publishing, provider/model/seed/BF16/cost policy, Fact Lock, identity, sentiment, neutrality, semantic publication gates or Golden thresholds. No paid provider was connected and no PNG was fabricated.
