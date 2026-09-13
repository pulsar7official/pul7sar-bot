# PUL7SAR Phase 18 — Implementation Log 124

This log records work on `phase18/story-intelligence` only. `main` is not modified.

## Branch state and prior verification

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence`
- Branch was reviewed as diverged from `main`; no merge or write to `main` was performed.
- PR #1 remained open, Draft, unmerged, with `main` as base.
- Prior run `32741694496` / 1820 completed successfully before Change Set 123.

## Change Set 123 result observed

Run `32741891562` / 1830 failed during full Phase 18 discovery after 857 tests began.

Important distinction:

- syntax passed;
- all new first-PNG semantic-preflight tests from Change Set 123 passed;
- the failure was two pre-existing embedded-brand loader tests;
- both failed with `PUL7SAR_EMBEDDED_BRAND_BASE64_INVALID` while strictly decoding the repository-carried Base64 study bundle.

No GPU generation was attempted or claimed.

## Change Set 124 — SHA-Locked Brand Bundle Transport Recovery

### Modified

#### `engine/intelligence/brand_embedded_master.py`

Added a transport-decoding helper that attempts strict Base64 first. If textual transport characters make strict decoding fail, permissive Base64 decoding may recover the candidate bytes, but those bytes remain unusable unless they match the already pinned bundle SHA-256 exactly.

The immutable bundle SHA remains:

`49ed35398dbb3a62460ff4ee52b7eea7b0db295b165271cef1126484d3d15d62`

All existing member SHA-256 checks remain mandatory.

This repairs textual transport robustness without accepting a different binary archive.

#### `tests/test_phase18_brand_embedded_master.py`

Added a regression test proving transport-noise recovery produces the original bytes and that the production bundle SHA lock remains unchanged.

Existing tests still load the real repository asset and verify all three separated layers.

### Added

- `docs/PHASE18_CHANGESET_124_SHA_LOCKED_BRAND_BUNDLE_TRANSPORT_RECOVERY.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_124.md`

### Deleted

Nothing.

## Invariants preserved

Unchanged:

- `main`, `main.py`, Telegram and production publishing;
- exact embedded-brand bundle SHA and member SHAs;
- study-only/non-publication status of the embedded reference master;
- Fact Lock, source consensus and story-state integrity;
- identity verification;
- sentiment and winner/loser neutrality;
- `$0-local`;
- FLUX.2 Klein 4B;
- native BF16;
- seeds/canvases;
- generated brand/text/score/crest/exact-geometry exclusions;
- Base semantic/layer ownership;
- Qwen semantic and HYBRID_SURFACE checks;
- SemanticPublicationGate;
- Golden visual quality thresholds (`8.5` minimum / `9.0+` elite);
- exact publication brand and typography integrity requirements.

No Fake PNG, paid provider, hosted-GPU fallback, binary checksum relaxation, publication shortcut or semantic bypass was introduced.

## Current CI status

- Run 1830 failure is understood and recorded above.
- Change Set 124 repair/tests are committed on `phase18/story-intelligence`.
- A new CI run must complete successfully before this repair is described as verified.

## Current genuine Golden Visual state

No compatible CUDA/BF16 host is attached to the current execution environment. Therefore Golden Hybrid v5 FLUX.2 Klein Candidate 1 remains not generated under the latest architecture, and no result is fabricated.

## Remaining work

1. Observe the CI run for Change Set 124 and fix any remaining regression without weakening gates.
2. On a compatible CUDA/BF16 host, run the now-semantic-preflight-locked Candidate 1 path only.
3. Review the genuine Base PNG before spending GPU on Seeds 2–4.
4. Preserve provenance, Base semantic/layer ownership, deterministic football geometry, receipt-backed Hybrid QA, Qwen HYBRID_SURFACE and SHA-bound Golden review.
5. Keep final publication blocked until the exact user-approved PUL7SAR brand geometry/logo/font assets are SHA-locked and pass their independent integrity gates.

## Change summary

- Modified: `engine/intelligence/brand_embedded_master.py`
- Modified: `tests/test_phase18_brand_embedded_master.py`
- Added: `docs/PHASE18_CHANGESET_124_SHA_LOCKED_BRAND_BUNDLE_TRANSPORT_RECOVERY.md`
- Added: `docs/PHASE18_IMPLEMENTATION_LOG_124.md`
- Deleted: none
- `main`: untouched
