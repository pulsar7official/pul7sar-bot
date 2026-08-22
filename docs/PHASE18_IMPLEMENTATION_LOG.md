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
- Added `DryRunManifest` / `DryRunManifestCompiler`.
- Manifest exposes canvas, safe area, geometry, accent, assets, facts, negative constraints and prompt per platform.
- Multi-platform compiler now creates deterministic layout automatically.
- CI `32577945352`: SUCCESS.

## Change Set 013 — Entity theme, exact brand semantics, destination social assets
- Added verified `EntityThemeResolver` with PUL7SAR-red fallback.
- Added exact wordmark vs independently tintable 7/pulse semantics.
- Added destination-specific social icon filtering.
- Team/club crests remain exact and untinted.
- CI `32578124530`: SUCCESS.

## Change Set 014 — Inspectable brand/theme manifest + end-to-end regression fixture

### Purpose
Make every pre-generation brand and theme decision visible in the dry-run manifest and exercise the complete multi-platform dry-run path on a realistic PUL7SAR transfer-story regression fixture.

### Modified
- `engine/intelligence/dry_run_manifest.py`
  - Manifest version advanced to `pul7sar-phase18-manifest-v2`.
  - Each platform entry now exposes `theme` explicitly: accent, source, entity name, verified state.
  - Each platform entry now exposes `brand_plan` explicitly: exact wordmark asset, pulse/7 asset, pulse tint, exact-wordmark preservation, exact-team-crest preservation.
  - Existing canvas, safe area, layout boxes, asset IDs, facts, negative constraints and prompt remain inspectable.

### Added
- `tests/test_phase18_end_to_end_dry_run.py`
  - Adds a synthetic editorial regression fixture shaped like a real PUL7SAR Arsenal transfer story.
  - The fixture is explicitly not treated as live-news verification.
  - Preserves an `approach`/in-progress transfer state and prohibits visual conversion into a completed signing.
  - Compiles one story across seven current platform surfaces.
  - Verifies destination-specific social icon filtering.
  - Verifies Arsenal-style verified palette evidence drives only the tintable PUL7SAR pulse/7 accent.
  - Verifies exact PUL7SAR wordmark and exact team crest preservation flags.
  - Verifies 1080x1350, 1080x1920, 1600x900 and 1280x720 platform canvases.
  - Verifies platform geometry differs rather than being resized blindly.
  - Verifies only locked FACT claims enter factual constraints.
  - Verifies `NO_UNVERIFIED_SIGNING` and explicit anti-fake-announcement constraints survive to the generation package.

### Production safety
- No live-news fact is asserted by the regression fixture.
- `main.py`: untouched.
- Telegram publishing: untouched.
- Legacy image sourcing/rendering: untouched.
- Production renderer/templates: untouched.
- No external image provider invoked.
- No API key/secret added.

### Architecture after Change Set 014
`Article -> Story Intelligence -> Fact/Identity/Sentiment/Neutrality gates -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Entity Theme -> Exact Brand/Social Asset Selection -> Deterministic Layout -> Layout-aware Generation Package -> Inspectable Dry-run Manifest -> future provider adapter`

### Next planned work
1. Verify Change Set 014 CI.
2. Add provider capability contracts: image-to-image/reference support, exact asset compositing support, supported aspect ratios/resolutions, transparent asset handling and deterministic seed support.
3. Add provider eligibility/fallback policy so a provider cannot be selected if it cannot satisfy a story/package requirement.
4. Build a provider-neutral execution plan without invoking a paid image API.
5. Only after capability/fallback tests pass should the first real original-image provider be connected behind `AuthorizedSceneGenerator`.
