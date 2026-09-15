# PUL7SAR Phase 18 — Change Set 069: Golden v4 Smoke Compatibility

## Trigger
The active Golden benchmark had already advanced to `pul7sar-golden-batch-v4` to address two real visual failures observed in Colab: malformed football-pitch geometry and an incorrect AI-generated `PUL7SAR` wordmark. The batch builder and verifier were v4-aware, but the durable Golden smoke coordinator still accepted only v1/v2 and its regression test still expected the v2 request ID.

That mismatch would block the one-command / durable-queue first-PNG path before GPU execution, despite the v4 handoff itself being valid.

## Changes

### `engine/intelligence/golden_smoke.py`
- Extends supported Golden manifest versions through v4 while preserving v1/v2 historical compatibility.
- Applies cumulative fail-closed policy checks:
  - v2+: `single_continuous_scene`;
  - v3+: `association_football_regulation_pitch`;
  - v4: `generated_branding_allowed=false` and `brand_composition_policy=exact_assets_only_after_generation`.
- Replays matching SHA-protected prompt locks before candidate 1 may enter the durable queue:
  - unified single-scene markers;
  - regulation-pitch geometry markers;
  - generated-brand exclusion markers.
- Keeps `$0-local`, request/seed/model/SHA identity, bounded retries and terminal-failure behavior unchanged.

### `tests/test_phase18_golden_smoke.py`
- Updates the active request ID expectation to `golden-general-season-opener-v4-001`.
- Adds fail-closed regression coverage for:
  - composition-grammar drift;
  - sport-geometry drift;
  - generated-branding permission drift;
  - post-generation brand-policy drift.
- Retains SHA, zero-cost, durable-job identity and terminal-failure coverage.

## Safety / invariants
Unchanged:
- `main` and `main.py`;
- Telegram production publishing and the legacy image path;
- factual, identity, sentiment and neutrality locks;
- zero-cost provider/model restrictions;
- SemanticPublicationGate;
- Golden 8.5 / elite 9.0 thresholds;
- BF16 requirement and exact canvas/seed/model identity.

No file is deleted and no PNG is fabricated.

## Remaining blocker
A genuine v4 Candidate 1 still requires compatible CUDA execution (the established Colab Tesla T4 path is suitable with sequential CPU offload). Until that GPU run occurs, v4 visual success is not claimed.

The next genuine PNG must be judged simultaneously for: one continuous scene, regulation football-pitch geometry, zero generated PUL7SAR branding/text, and premium editorial quality.
