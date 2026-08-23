# PUL7SAR Phase 18 — Change Set 081

## Golden v4 CPU verification alignment

Branch review found a stale integration path in `.github/workflows/phase18-intelligence.yml`: the active builders and Colab runner were already locked to Golden v4, but CPU CI still passed a v2 request ID and uploaded artifacts with v2 names. That could make a green verification run appear to certify a stale benchmark contract.

Change Set 081 updates the workflow to:

- build request `golden-general-season-opener-v4-001`,
- label the handoff and candidate-batch artifacts as v4,
- explicitly assert `pul7sar-golden-batch-v4`,
- assert `single_continuous_scene`,
- assert `association_football_regulation_pitch`,
- assert `generated_branding_allowed=false`,
- assert `brand_composition_policy=exact_assets_only_after_generation` before artifact upload.

Added `tests/test_phase18_intelligence_workflow.py` so future edits fail if the workflow regresses to v2 request/artifact names or loses the current v4 contract markers. The workflow remains CPU-only on `ubuntu-latest`, Phase-18-scoped, and contains no paid-provider secret or API endpoint.

No change was made to `main`, `main.py`, Telegram production publishing, provider/model/seed/BF16/cost policy, semantic publication gates or Golden thresholds. Files deleted: none.
