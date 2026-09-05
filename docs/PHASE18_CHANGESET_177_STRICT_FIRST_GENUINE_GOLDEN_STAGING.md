# PUL7SAR Phase 18 — Change Set 177

## Strict First Genuine Golden Staging

This change set reduces the gap between a successful Colab command and a genuinely reviewable Golden Editorial v6 Candidate 1.

### Why this was needed

`phase18_colab_one_command.py` intentionally supports an engineering-proof fallback when Qwen semantic inspection is unavailable. That fallback is useful for development, but it must not be confused with the first genuine Golden candidate.

The new strict entrypoint forces Candidate 1, forces Qwen semantic inspection, enables `--strict-semantic`, and then verifies that the exact generated PNG is the same PNG recorded by the semantically clean BASE_SCENE receipt.

### Added

- `tools/phase18_colab_first_genuine_golden.py`
  - Candidate 1 only;
  - `--semantic-inspection qwen` and `--strict-semantic` are mandatory;
  - refuses engineering-proof receipts;
  - verifies Golden Editorial v6 manifest/benchmark and context-only surface policy;
  - verifies the locked v6 composition map;
  - verifies semantic and layer-ownership approval;
  - verifies generation/semantic PNG path identity, PNG signature and SHA-256;
  - produces a staging receipt for human review only;
  - keeps Golden approval, publication readiness and Seeds 2–4 closed.

- `tests/test_phase18_first_genuine_golden.py`
  - covers clean review-only staging;
  - rejects semantic engineering fallback;
  - rejects composition-map drift;
  - rejects pitch-replacement regression;
  - rejects generation/semantic PNG path drift;
  - locks the CLI to Candidate 1 and strict semantic inspection.

### Migration repairs discovered from real CI

Story Intelligence Verification run `32987797988` ran 1,234 Phase 18 tests and exposed three concrete v6 migration issues before any GPU work:

1. `tools/phase18_build_golden_handoff.py` still instantiated `AssetBundle()` using the removed implicit-empty constructor. It now uses the explicit current contract `AssetBundle(assets=())`.
2. `tests/test_phase18_colab_engineering_fallback.py` used a stale v6 fixture without the locked focal-anchor / copy-space / brand-quiet-zone fields. The fixture now matches the current v6 contract.
3. `tests/test_phase18_colab_notebook.py` still asserted Golden Hybrid v5 wording and legacy branding-copy phrases. The test now asserts Golden Editorial v6, context-only preview behavior, the strict 8.5/9.0+ quality floor and downstream exact branding/typography/publication gates.

### Deleted

None.

### Gate preservation

No factual, identity, sentiment/neutrality, zero-cost, model-revision, BF16, resource, semantic-publication, brand, typography, or Golden-quality gate was weakened. `publication_ready=false` remains mandatory at this stage.
