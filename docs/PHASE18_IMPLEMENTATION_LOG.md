# PUL7SAR Phase 18 — Implementation Log

This document is the authoritative implementation journal for Phase 18 on the `phase18/story-intelligence` branch.

## Change Sets 001–009
Previously documented foundation: Fact Lock, StoryAnalyzer, identity verification, classification, neutrality, Visual Family routing, perspective-aware result sentiment, Concept Director, sentiment resolver, Generation Authorization, platform profiles, Original Scene Specification, exact assets, layout safety, multi-platform batch generation packages. All production paths remain isolated.

## Change Set 010 — Deterministic platform layout planner
- Added deterministic protected boxes for hero, logo, crest, score, headline, and compact social footer.
- Added separate portrait, vertical, and landscape art direction.
- Added default PUL7SAR red and validated entity accent support.
- CI `32577397716`: SUCCESS.

## Change Set 011 — Layout-aware Generation Package
- `GenerationPackage` now carries layout boxes and accent color.
- Generation package rejects platform/canvas mismatch.
- Exact geometry reaches the provider-neutral package.
- Initial integration test error was corrected to canonical asset roles.
- Corrected CI run `32577621033`: SUCCESS.

## Change Set 012 — Cross-platform dry-run manifest

### Added
- `engine/intelligence/dry_run_manifest.py`
  - Adds `DryRunManifest` and `DryRunManifestCompiler`.
  - Produces one inspectable manifest for a story across multiple destination surfaces.
  - Carries per platform: canvas, aspect ratio, safe area, layout geometry, accent, exact asset IDs, factual constraints, negative constraints, prompt, and metadata.
  - Rejects empty manifests and duplicate platform packages.

- `tests/test_phase18_dry_run_manifest.py`
  - Verifies vertical and landscape canvases preserve distinct geometry.
  - Verifies accent, assets, facts, and negative constraints remain visible in the manifest.

### Modified
- `engine/intelligence/batch_scene.py`
  - Multi-platform compilation now plans deterministic layout automatically for every destination.
  - Each `PlatformScenePackage` now retains its `PlannedLayout`.

- `engine/intelligence/__init__.py`
  - Exports dry-run manifest APIs.

### Validation
- CI run `32577945352`: SUCCESS.

## Change Set 013 — Entity theme, exact brand semantics, destination social assets

### Core visual rules encoded
- General stories use PUL7SAR red when no verified entity palette is available.
- A club/entity accent is accepted only from explicit palette evidence with a confidence threshold.
- The exact PUL7SAR wordmark never changes color or shape through the theme resolver.
- Only the PUL7SAR 7/pulse asset may receive the resolved entity accent when its asset treatment is explicitly `TINTABLE_ACCENT`.
- Team/club crests remain exact and untinted.
- A platform package receives only its own destination social icon; unrelated platform icons are removed from that package.

### Added
- `engine/intelligence/entity_theme.py`
  - Adds `EntityPaletteEvidence`, `EntityTheme`, and `EntityThemeResolver`.
  - Never guesses colors from a club name.
  - Low-confidence/missing evidence falls back to `#E10600`.

- `engine/intelligence/social_assets.py`
  - Adds `DestinationSocialAssetSelector`.
  - Maps Instagram Feed/Story to Instagram icon, X to X icon, Facebook to Facebook icon, Threads to Threads icon, TikTok to TikTok icon, and Telegram to Telegram icon.
  - Rejects duplicate social icons for the same destination.

- `engine/intelligence/brand_semantics.py`
  - Adds `BrandPlacementPlan` and `BrandPlacementPlanner`.
  - Separates exact PUL7SAR logo from independently tintable pulse/7 semantics.
  - Keeps team crests exact.

- `tests/test_phase18_brand_theme_social.py`
  - Verifies PUL7SAR-red fallback.
  - Verifies high-confidence verified club palette controls only the tintable PUL7SAR accent.
  - Verifies low-confidence palette falls back safely.
  - Verifies destination-specific social icon filtering.
  - Verifies duplicate destination icons are rejected.

### Modified
- `engine/intelligence/batch_scene.py`
  - Integrates theme resolution before layout planning.
  - Filters social assets independently for each destination.
  - Produces and retains a `BrandPlacementPlan` and `EntityTheme` per platform package.
  - Passes the resolved accent into deterministic layout.

- `engine/intelligence/__init__.py`
  - Exports entity-theme, brand-placement, and social-asset selection APIs.

### Deleted
- Nothing.

### Production safety
- `main.py`: untouched.
- Telegram publishing: untouched.
- Legacy image sourcing/rendering: untouched.
- Existing production renderer/templates: untouched.
- No external image provider invoked.
- No production secret/API key added.

### Current architecture
`Article -> Story Intelligence -> Fact/Identity/Sentiment/Neutrality gates -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Entity Theme -> Exact Brand/Social Asset Selection -> Deterministic Layout -> Layout-aware Generation Package -> Dry-run Manifest -> future provider adapter`

### Next planned work
1. Verify Change Set 013 CI.
2. Extend the manifest to expose brand plan and destination social asset decisions explicitly.
3. Build one realistic end-to-end dry-run fixture representing an actual PUL7SAR news story.
4. Add provider capability evaluation/fallback contracts.
5. Only then select/connect the first real original-image provider behind `AuthorizedSceneGenerator`.
