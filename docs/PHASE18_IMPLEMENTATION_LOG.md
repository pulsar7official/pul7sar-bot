# PUL7SAR Phase 18 — Implementation Log

This document is the authoritative implementation journal for Phase 18 on the `phase18/story-intelligence` branch.

## Change Sets 001–009
Previously documented foundation: Fact Lock, StoryAnalyzer, identity verification, classification, neutrality, Visual Family routing, perspective-aware result sentiment, Concept Director, sentiment resolver, Generation Authorization, platform profiles, Original Scene Specification, exact assets, layout safety, multi-platform batch generation packages. All production paths remain isolated.

## Change Set 010 — Deterministic platform layout planner
- Deterministic protected geometry for hero/logo/crest/score/headline/footer.
- Separate portrait, vertical and landscape art direction.
- CI `32577397716`: SUCCESS.

## Change Set 011 — Layout-aware Generation Package
- Generation package carries exact geometry and accent color.
- CI `32577621033`: SUCCESS.

## Change Set 012 — Cross-platform dry-run manifest
- Inspectable canvas/safe-area/layout/assets/facts/negative constraints per platform.
- CI `32577945352`: SUCCESS.

## Change Set 013 — Entity theme, exact brand semantics, destination social assets
- Verified palette resolver with PUL7SAR-red fallback.
- Exact wordmark vs tintable 7/pulse semantics.
- Destination-only social icon filtering.
- CI `32578124530`: SUCCESS.

## Change Set 014 — Inspectable brand/theme manifest + end-to-end regression fixture
- Manifest v2 exposes verified theme and brand plan.
- Seven-platform synthetic transfer-story regression fixture.
- CI `32578343142`: SUCCESS.

## Change Set 015 — Provider capability and eligibility layer

### Added
- `engine/intelligence/provider_capabilities.py`
  - Models text-to-image, reference images, identity reference, multiple references, transparent PNG input, exact asset compositing, negative instructions, deterministic seed and post-compositing.
  - Validates maximum resolution, supported aspect ratios and maximum reference-image count.
  - `ProviderEligibilityGate` rejects any provider that cannot satisfy explicit package requirements.

- `engine/intelligence/provider_selection.py`
  - Adds explicit ordered fallback selection.
  - Never ranks providers silently by price, popularity or vendor name.
  - If no provider qualifies, selection remains empty rather than degrading the visual contract.

- `tests/test_phase18_provider_eligibility.py`
  - Covers feature, resolution, aspect ratio, reference count, explicit fallback, no-provider and duplicate-ID behavior.

### Validation
- CI `32579225091`: SUCCESS.

## Change Set 016 — Provider-neutral execution plan

### Core architectural decision
The image model is responsible for the **original photographic/editorial base scene**, not for reproducing PUL7SAR branding, official team crests, social icons, score typography or final headline text.

Those official/deterministic elements are applied **after** scene generation by the PUL7SAR composition layer. This avoids asking an image model to reproduce assets it is structurally bad at reproducing exactly.

### Added
- `engine/intelligence/provider_execution.py`
  - Adds `ExecutionStage`, `ExecutionStep`, `ProviderExecutionPlan`, and `ProviderExecutionPlanner`.
  - Produces strict stages:
    1. `GENERATE_BASE_SCENE`
    2. `APPLY_EXACT_ASSETS`
    3. `APPLY_EDITORIAL_TEXT`
    4. `QUALITY_VERIFY`
    5. `EXPORT`
  - Sends verified identity-reference assets to the image provider only when required.
  - Keeps PUL7SAR logo, PUL7SAR 7/pulse, team crests, competition marks and social icons out of provider generation and reserves them for deterministic post-compositing.
  - Derives provider requirements from actual generation-stage needs.
  - Negative constraints require provider negative-instruction support.
  - Multiple identity references require multiple-reference support.
  - Exact-asset compositing and transparent-PNG support are intentionally **not** required from the image provider when those assets are post-composited by PUL7SAR.
  - Refuses to compile an execution plan when provider selection found no eligible provider.

- `tests/test_phase18_provider_execution.py`
  - Verifies exact official assets never become generated references.
  - Verifies identity reference is passed to the provider stage.
  - Verifies provider capability requirements do not unnecessarily include exact-asset compositing or transparent PNG handling.
  - Verifies negative-constraint capability, multiple references and strict stage ordering.
  - Verifies no eligible provider blocks execution planning.

### Modified
- `engine/intelligence/__init__.py`
  - Exports provider execution-planning APIs.

### Production safety
- `main.py`: untouched.
- Telegram publishing: untouched.
- Legacy image sourcing/rendering: untouched.
- Production renderer/templates: untouched.
- No external image provider invoked.
- No secret/API key added.

### Architecture after Change Set 016
`Article -> Story Intelligence -> Fact/Identity/Sentiment/Neutrality gates -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Theme -> Exact Destination Assets -> Deterministic Layout -> Generation Package -> Provider Eligibility/Selection -> Provider Execution Plan -> AI Base Scene -> Deterministic Asset/Text Composition -> Quality Verification -> Platform Export`

### Next planned work
1. Verify Change Set 016 CI.
2. Add a renderer/compositor contract for applying exact assets into deterministic layout boxes.
3. Add text-rendering contracts for headline, score and compact destination footer outside the image model.
4. Add post-composition quality-verification contracts for asset checksum/identity, geometry, legibility and safe-area compliance.
5. Only after these deterministic post-generation stages are stable should a real image provider adapter be connected.
