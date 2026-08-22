# PUL7SAR Phase 18 — Implementation Log

This document is the authoritative implementation journal for Phase 18 on the `phase18/story-intelligence` branch.

## Change Sets 001–024
Previously documented foundation: Fact Lock, StoryAnalyzer, identity verification, classification, neutrality, Visual Family routing, perspective-aware result sentiment, Concept Director, sentiment resolver, Generation Authorization, platform profiles, Original Scene Specification, exact assets, layout safety, multi-platform packages, deterministic layout, dry-run manifest, entity theme, exact brand semantics, provider capability/selection/execution, post-composition, deterministic typography/final export, base-scene visual acceptance, zero-cost policy, provider adapters, candidate selection, generation-session orchestration, first zero-cost local model profile, prompt-constraint reframing, and local runtime compatibility. Production paths remain isolated.

## Change Set 025 — Local backend readiness + generation provenance
- Adds optional Diffusers/ComfyUI backend contracts without installing either dependency.
- Requires proven model-runtime compatibility and an available local backend before generation is considered ready.
- ComfyUI requires an explicit local endpoint.
- Diffusers can be represented without becoming a hard repository dependency.
- Adds deterministic local generation provenance: provider, model, backend, seed, request ID and output dimensions.
- Initial contract-name mismatch was caught by CI and fixed against the canonical `RuntimeHardwareSnapshot` / `LocalModelCandidate` APIs.
- CI after fix `32587132967`: SUCCESS.

## Change Set 026 — Machine-readable $0 local readiness report
- Adds `engine/intelligence/local_readiness_report.py`.
- Reports ready/blocked state, provider/model/backend, runtime kind, GPU name, proven VRAM, blockers and warnings.
- Explicit execution mode is `$0-local`.
- Blocked runtime/backend states remain blocked rather than triggering silent installation or paid fallback.
- CI `32587249246`: SUCCESS.

## Change Set 027 — Exact local backend execution boundary

### Added
- `engine/intelligence/local_backend_execution.py`
  - `LocalBackendGenerationRequest`
  - `LocalBackendGenerationResult`
  - `LocalImageBackend` protocol
  - `LocalBackendRequestCompiler`
  - `LocalBackendResultGate`
- `tests/test_phase18_local_backend_execution.py`

### Request compilation
A local generation request can only be compiled from a readiness report with `ready=True` and `$0-local` cost mode.

The request locks:
- provider ID
- model ID
- backend ID
- final base-scene prompt
- translated/native negative constraints
- width/height
- deterministic seed
- request ID
- verified reference asset IDs
- platform/layout metadata

For models without native negative prompts, all PUL7SAR forbidden constraints must translate completely through `PromptConstraintCompiler`; unknown constraints still fail closed.

The request explicitly instructs the backend to generate only the clean base scene. PUL7SAR branding, official crests, social icons, score typography, final headline and footer text remain outside the image model.

### Result integrity
`LocalBackendResultGate` rejects any backend result that changes:
- provider ID
- model ID
- backend identity
- request ID
- deterministic seed
- approved dimensions

Validated output becomes `LocalGenerationProvenance` for downstream quality evidence and reproducibility.

### Current CI
Change Set 027 workflow was queued after commit `15c83d5ade3716b84bbece4d5e68211e6e42b488`; success is not claimed until GitHub Actions completes.

## Production safety through Change Set 027
- `main.py`: untouched.
- Telegram production publishing: untouched.
- Legacy image sourcing/rendering: untouched.
- Production renderer/templates: untouched.
- No paid provider connected.
- No paid API selected.
- No production secret/API key added.
- No model weights or font files committed.
- No local image backend invoked yet.

## Architecture after Change Set 027
`Article -> Story Intelligence -> Fact / Identity / Sentiment / Neutrality -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Theme / Assets / Layout -> Generation Package -> Zero-Cost Eligibility -> Runtime / Backend Readiness -> $0 Readiness Report -> LocalBackendRequestCompiler -> Local Backend -> LocalBackendResultGate / Provenance -> Generation Session -> BaseSceneVisualAcceptanceGate -> Quality-First Candidate Selection -> PostComposition -> Typography -> FinalExportGate -> Platform Export`

## Next planned work
1. Verify Change Set 027 CI.
2. Add concrete optional Diffusers and ComfyUI adapter shells behind `LocalImageBackend` without automatic dependency installation.
3. Add generated-image evidence extraction interfaces for dimensions, identity, framing, protected-region occupancy and defects.
4. Build a single-command local readiness CLI/report for the user's own machine.
5. Attempt the first real $0 base-scene generation only after the local machine proves compatible.
