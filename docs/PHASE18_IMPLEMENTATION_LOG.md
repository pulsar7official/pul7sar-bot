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
- Models provider features, output limits and reference limits.
- Explicit eligibility and ordered fallback policy.
- CI `32579225091`: SUCCESS.

## Change Set 016 — Provider-neutral execution plan
- AI provider generates only the base scene.
- Official logos, crests, social icons, score typography and final copy are applied later by PUL7SAR.
- Strict stages: generate -> exact assets -> editorial text -> quality -> export.
- CI `32579444426`: SUCCESS.

## Change Set 017 — Deterministic post-generation composition + quality gate
- Exact official assets and final editorial text are post-composited outside the image model.
- Asset SHA-256 integrity support and fail-closed composition validation.
- CI `32580744885`: SUCCESS.

## Change Set 018 — Deterministic typography + final export authorization
- Deterministic headline/score/footer style and fit contracts.
- Final export authorization requires approved typography, geometry and post-composition quality.
- CI `32580980268`: SUCCESS.

## Change Set 019 — Base-scene visual acceptance gate
- Rejects weak/unsafe generated scenes before PUL7SAR branding and typography.
- Checks resolution, ratio, framing, identity confidence, protected regions, defects, forbidden visuals, crop potential and provenance.
- CI `32581392130`: SUCCESS.

## Change Set 020 — Zero-cost development enforcement
- Adds `engine/intelligence/cost_policy.py`.
- Current development execution accepts only proven zero-cost/local or genuinely free-tier providers without a required payment method.
- Paid/unknown-cost providers remain modelable for future expansion but are not selectable in current zero-cost mode.
- Provider selection applies cost eligibility before technical selection.
- Quality thresholds are not relaxed to satisfy zero-cost operation.

## Change Set 021 — Provider evidence adapters + quality-first candidate selection

### Purpose
Normalize provider-native output into PUL7SAR-owned evidence contracts, keep vendor payloads outside the domain core, and select the best *accepted* scene rather than the first technically successful generation.

### Added
- `engine/intelligence/provider_adapter.py`
  - `ProviderRawGeneration`
  - `ProviderEvidenceAdapter` protocol
  - `ProviderAdapterRegistry`
  - `AdapterMismatchError`
  - Explicit provider-ID adapter resolution; payload formats are never guessed.
  - Adapter output is rejected if it changes provider identity or output reference.

- `engine/intelligence/candidate_selection.py`
  - `CandidateOutcome`
  - `CandidateEvaluation`
  - `CandidateSelectionResult`
  - `RegenerationPolicy`
  - `QualityFirstCandidateSelector`
  - `BoundedRegenerationController`

### Quality-first ranking
Only candidates that already pass `BaseSceneVisualAcceptanceGate` can receive a non-zero quality score.

Accepted candidates are ranked using:
- verified identity confidence
- framing confidence
- cleanliness of protected overlay regions

Cost is deliberately excluded from candidate quality scoring. Cost/economics determines provider eligibility upstream; once an eligible zero-cost provider has generated candidates, visual quality decides the winner.

### No degraded fallback
If no candidate passes all acceptance gates, the explicit outcome is `NO_ACCEPTABLE_SCENE`.

Reaching the regeneration-attempt bound never authorizes a rejected image. It stops generation and preserves rejection reasons for diagnostics/review.

### Tests
- `tests/test_phase18_candidate_selection.py`
  - provider payload normalization
  - unknown adapter rejection
  - adapter provider relabel protection
  - best accepted candidate wins by quality
  - rejected candidate score remains zero
  - explicit no-acceptable-scene outcome
  - bounded retries without degraded fallback
  - immediate stop after acceptable candidate

### Validation
- CI `32585786963`: SUCCESS.

### Future architecture recorded
- `docs/FUTURE_SOCIAL_VIDEO_ARCHITECTURE.md`
  - Headless PUL7SAR Studio / API direction
  - credential security via OAuth/tokens/secrets rather than passwords in code
  - Social Intelligence source discovery
  - semantic deduplication + Story Memory
  - Video Intelligence / Motion Identity
  - Rights & Provenance gate
  - zero-cost development with future paid-provider extensibility
  - quality-first rule across all future automation

### Production safety
- `main.py`: untouched.
- Telegram publishing: untouched.
- Legacy image sourcing/rendering: untouched.
- Production renderer/templates: untouched.
- No external image provider invoked.
- No production secret/API key added.

### Architecture after Change Set 021
`Article -> Story Intelligence -> factual / identity / sentiment / neutrality gates -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Theme -> Destination Assets -> Deterministic Layout -> Generation Package -> Zero-Cost Provider Eligibility -> Execution Plan -> Provider Adapter -> Candidate Base Scenes -> BaseSceneVisualAcceptanceGate -> QualityFirstCandidateSelector -> PostCompositionPlanner -> Asset Integrity / Composition Quality -> Deterministic Typography -> FinalExportGate -> Platform Export`

### Next planned work
1. Build a provider-neutral generation-session orchestrator that coordinates bounded attempts without knowing vendor details.
2. Persist structured rejection diagnostics for each candidate/attempt.
3. Add a deterministic acceptance threshold above basic gate pass so very weak-but-technically-valid scenes can still be rejected.
4. Prepare the first $0 real-provider/local-provider evaluation behind the existing gates.
5. Produce the first end-to-end PUL7SAR visual at $0 cost before considering any paid provider.
