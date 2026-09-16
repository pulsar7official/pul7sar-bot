# Phase 18 Change Set 097 — Feathered Pitch Integration

## Purpose
Change Sets 095–096 removed the opaque tactical-board pitch replacement and synthetic mowing bands from the default Golden Hybrid path. The remaining deterministic colour-normalisation layer still ended at the exact pitch quadrilateral boundary, which could produce a visible hard cut even at low opacity.

Change Set 097 keeps the existing texture-preserving approach but feathers the colour-normalisation mask inward. Exact regulation markings remain deterministic and sharp; only the low-opacity turf tint is softened at the pitch boundary.

## Added
- `DEFAULT_SURFACE_FEATHER_PX = 18` in `football_hybrid_composer.py`.
- `surface_feather_px` in `FootballPitchRenderStyle` and `FootballHybridCompositionReceipt`.
- Regression coverage proving that the tint stays fully transparent outside the pitch, is weaker close to the boundary, and reaches the intended opacity in the pitch interior.
- Integrity regression coverage that rejects a hard-edge `surface_feather_px=0` receipt for the Golden hybrid path.

## Modified
- `engine/intelligence/football_pitch_renderer.py`
  - Builds a deterministic grayscale pitch mask.
  - Applies Gaussian blur to the mask.
  - Multiplies the blurred mask by the original hard polygon mask, creating an inward-only feather.
  - Prevents green tint from bleeding into stands or surrounding scene pixels.
  - Keeps regulation markings on their exact projective geometry after the surface blend.
- `engine/intelligence/football_hybrid_composer.py`
  - Default Golden surface feather is 18 px.
  - Persists the feather value in the composition receipt.
  - Existing texture preservation, low-opacity tint, stripe-free default and deterministic markings remain unchanged.
- `engine/intelligence/hybrid_artifact_integrity.py`
  - Requires a feather value in the safe range 8..48 px for a Golden football receipt.
  - Existing SHA replay, texture-preserving mode, source-texture preservation and safe opacity requirements remain mandatory.
- `tests/test_phase18_football_hybrid_composer.py`
  - Verifies the default receipt carries a non-zero feather.
  - Verifies inward-only feather behavior at pixel level.
- `tests/test_phase18_hybrid_artifact_integrity.py`
  - Verifies hard-edge receipts are rejected.

## Deleted
- Nothing.

## Gates and invariants preserved
- `main` / `main.py`: untouched.
- Fact Lock, identity verification, sentiment and neutrality: unchanged.
- `$0-local`: unchanged.
- FLUX.2 Klein 4B, BF16, seeds/canvases, generation steps/guidance: unchanged.
- Base semantic layer-ownership gate remains mandatory before deterministic pitch composition.
- SemanticPublicationGate remains mandatory for publication.
- Golden quality thresholds remain 8.5 minimum / 9.0+ elite with hard blockers overriding score.
- Generated PUL7SAR branding remains forbidden.
- Exact PUL7SAR logo bytes/checksum remain unresolved; final publication composition stays blocked.
- No paid provider, secret, model weights, font files, fake PNG or fabricated benchmark was added.

## Remaining work
1. Confirm full Phase 18 CPU CI on the Change Set 097 head.
2. Run Golden Hybrid v5 Candidate 1 only on a compatible CUDA/BF16 host.
3. Inspect whether the combination of preserved turf, stripe-free default, low-opacity tint and inward feather reads as one photographic field rather than a composited panel.
4. If the candidate still fails, tune only evidence-backed placement, feather radius, tint opacity or line styling; do not relax factual, identity, semantic-publication or Golden-quality gates.
5. SHA-lock the user-approved PUL7SAR logo before final publication composition.
