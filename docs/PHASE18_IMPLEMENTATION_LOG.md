# PUL7SAR Phase 18 — Implementation Log

This document is the authoritative implementation journal for Phase 18 on the `phase18/story-intelligence` branch.

## Change Sets 001–009
Previously documented foundation: Fact Lock, StoryAnalyzer, identity verification, classification, neutrality, Visual Family routing, perspective-aware result sentiment, Concept Director, sentiment resolver, Generation Authorization, platform profiles, Original Scene Specification, exact assets, layout safety, multi-platform batch generation packages. All production paths remain isolated.

## Change Set 010 — Deterministic platform layout planner

### Added
- `engine/intelligence/layout_planner.py`
  - Adds `DeterministicLayoutPlanner`, `LayoutRequirements`, `LayoutOrientation`, and `PlannedLayout`.
  - Computes actual protected boxes for hero, PUL7SAR logo, club crest, score, headline, and compact social footer.
  - Uses a distinct composition strategy for portrait, vertical, and landscape canvases.
  - Every generated box is immediately validated by `PlatformLayoutSafetyGate`.
  - General stories default to the current PUL7SAR red placeholder `#E10600`.
  - Entity-led stories may supply a validated `#RRGGBB` accent for the approved tintable 7/pulse asset only.

- `tests/test_phase18_layout_planner.py`
  - Verifies Instagram Story vertical layout, Instagram Feed portrait layout, and X landscape layout.
  - Verifies score/crest result layout.
  - Verifies adaptive entity accent normalization.
  - Verifies invalid colors are rejected.
  - Verifies one story is art-directed differently between vertical and landscape surfaces.

### Validation
- CI run `32577397716`: SUCCESS.
- Syntax: PASS.
- Phase 18 tests: PASS.
- Production isolation: PASS.

## Change Set 011 — Layout-aware Generation Package

### Purpose
Move deterministic geometry from a planning-only object into the actual provider-neutral generation package, so future image providers receive explicit protected layout coordinates rather than vague placement prose.

### Modified
- `engine/intelligence/generation_package.py`
  - `GenerationPackage` now carries `layout_boxes` and `accent_hex`.
  - `GenerationPackageCompiler.compile()` accepts an optional `PlannedLayout`.
  - Rejects platform or canvas mismatches between the scene specification and planned layout.
  - Serializes each protected element into exact `x / y / width / height` geometry.
  - Adds the approved accent color to the package.
  - Adds an explicit prompt instruction to follow deterministic layout geometry for protected editorial elements.
  - Retains exact-asset, English club/team naming, compact social-footer, factual, and negative-constraint rules.

### Added
- `tests/test_phase18_generation_layout.py`
  - Verifies Story layout geometry reaches the package.
  - Verifies hero/logo/headline/footer coordinates are included.
  - Verifies entity accent reaches both structured data and scene instructions.
  - Verifies result packages can carry score and crest boxes.
  - Verifies a layout for X cannot be attached to an Instagram package.

### Deleted
- Nothing.

### Production safety
- `main.py`: untouched.
- Telegram publishing: untouched.
- Legacy image sourcing/rendering: untouched.
- Existing production renderer/templates: untouched.
- No external image provider invoked.
- No production secret/API key added.

### Architecture after Change Set 011
`Article -> Story Intelligence -> Fact/Identity/Sentiment/Neutrality gates -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Deterministic Layout Planner -> Exact Assets -> Layout-aware Generation Package -> future provider adapter`

### Next planned work
1. Add an inspectable cross-platform dry-run manifest for one story.
2. Add destination-platform social-icon selection instead of passing unrelated social icons.
3. Add brand-placement semantics separating exact wordmark from tintable 7/pulse geometry.
4. Add theme/accent resolver integration from verified entity palette.
5. After the manifest is stable and reviewed, evaluate the first real original-image provider behind the existing authorization boundary.
