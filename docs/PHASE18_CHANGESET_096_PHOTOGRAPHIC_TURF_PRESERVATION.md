# PUL7SAR Phase 18 — Change Set 096: Photographic Turf Preservation

## Scope

Branch: `phase18/story-intelligence` only. `main` remains untouched.

This change advances Golden Hybrid v5 toward the first acceptable real PNG by reducing a known visual failure mode in deterministic football composition without relaxing any factual, identity, semantic, zero-cost, publication, or Golden-quality gate.

## Branch review before change

- Repository: `pulsar7official/pul7sar-bot`.
- Target branch: `phase18/story-intelligence`.
- Branch state before edits: diverged from `main`, 717 commits ahead and 64 behind.
- Pre-change head: `d84db1d6a511cb75a4b24a0f9de089ad7798708e`.
- `main` was not merged, force-updated, or modified.
- Change Set 095 CPU CI was already green (`32659343371`).
- A genuine Candidate 1 PNG under the latest texture-preserving Hybrid v5 architecture still has not been executed.

## Why this change was necessary

Change Set 095 removed the opaque tactical-board pitch replacement and preserved photographed turf. However, the default renderer still added deterministic mowing bands with alpha 24. Those bands are exact and technically safe, but they are not necessary for geometry correctness and can still make the pitch feel designed or diagrammatic rather than photographed.

For PUL7SAR's Golden visual target, existing grass texture, lighting gradients, wear, mowing patterns, and stadium atmosphere should come from the photographed/generative base. Code should own only the exact football geometry and a restrained colour normalization needed to integrate the surface.

## Added

- Regression coverage proving synthetic mowing stripes are disabled in the default Golden composition.
- Regression coverage proving mowing stripes remain an explicit opt-in styling control rather than a hidden requirement.
- Regression coverage proving artifact integrity accepts the default stripe-free texture-preserving composition and still accepts an explicitly requested striped variant.

## Modified

### `engine/intelligence/football_hybrid_composer.py`

- `DEFAULT_STRIPE_OPACITY` changed from `24` to `0`.
- `FootballHybridCompositionReceipt.mowing_stripes_applied` now defaults to `False`.
- The default Golden composition preserves photographed grass/mowing detail instead of synthesizing ten extra mowing bands.
- `stripe_opacity` remains explicitly available in the compositor API for a future evidence-backed visual recipe, but no Golden run receives it by default.
- Exact projected touchlines, halfway line, centre circle/mark, penalty areas/marks/arcs, goal areas, and corner arcs remain deterministic.
- Surface normalization remains texture-preserving and constrained to alpha `24..96`; the legacy opaque surface remains impossible through the public API.

### `engine/intelligence/hybrid_artifact_integrity.py`

- Synthetic mowing stripes are no longer required for artifact integrity.
- Integrity still requires:
  - current texture-preserving composition mode;
  - source texture preservation;
  - deterministic geometry ownership;
  - authoritative markings;
  - safe surface-normalization opacity;
  - matching input/output SHA-256 receipts;
  - a non-identical output artifact.

### `tests/test_phase18_football_hybrid_composer.py`

- Added assertions for stripe-free default behavior.
- Added explicit opt-in stripe test.
- Existing source-texture preservation and opaque-surface rejection remain.

### `tests/test_phase18_hybrid_artifact_integrity.py`

- Default stripe-free composition must validate.
- Explicit striped composition must also validate.
- Tampering, legacy opaque surfaces, and non-texture-preserving modes remain rejected.

## Deleted

Nothing.

## Gates and invariants preserved

- `main` / `main.py`: untouched.
- Fact Lock: unchanged and fail-closed.
- Identity verification: unchanged and fail-closed.
- Sentiment and neutrality: unchanged.
- `$0-local`: unchanged.
- FLUX.2 Klein 4B: unchanged.
- BF16 requirement: unchanged; no precision downgrade added.
- Golden seeds, canvas, guidance, and four-step inference: unchanged.
- Base-scene semantic layer-ownership gate remains mandatory for the quality path.
- SemanticPublicationGate remains mandatory for publication.
- Golden thresholds remain `8.5` minimum and `9.0+` elite; hard blockers override score.
- Generated PUL7SAR branding remains forbidden in the AI base.
- Exact approved PUL7SAR logo bytes/checksum remain unresolved, so final publication composition remains blocked.
- No paid provider, API secret, model weights, font files, fake PNG, or fabricated performance result was added.

## Test state

- GitHub Actions Run `32662495872` (run 1324): **SUCCESS** on the Change Set 096 head.
- Syntax check, full discover-based Phase 18 validation, completion audit, production isolation, Golden Hybrid v5 handoff build, four-candidate batch build, batch integrity, and current-contract assertions all passed.
- CPU CI correctly produced no fake visual proof; the visual-proof upload step remained skipped.
- No GPU visual result is claimed by this change.

## Remaining work

1. On a compatible CUDA/BF16 runtime, execute Golden Hybrid v5 Candidate 1 only.
2. Inspect whether the pitch now reads as photographic turf with deterministic regulation markings rather than a graphic surface.
3. If visual integration still fails, tune only evidence-backed placement, surface normalization, or line styling; do not relax factual, identity, semantic-publication, or Golden-quality gates.
4. Resolve and SHA-lock the user-approved PUL7SAR logo asset before final publication composition.
