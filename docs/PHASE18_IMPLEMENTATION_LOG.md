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
- Adds `engine/intelligence/local_backend_execution.py`.
- Local request compilation requires ready `$0-local` state.
- Locks provider/model/backend, prompt, constraints, dimensions, deterministic seed, request ID and reference IDs.
- Result gate rejects provider/model/backend/request/seed/dimension mutation.
- Valid result produces deterministic `LocalGenerationProvenance`.
- CI `32587484617`: SUCCESS.

## Change Set 028 — Optional local Diffusers / ComfyUI adapter shells
- Adds optional Diffusers and ComfyUI execution adapters behind the local backend contract.
- No automatic heavyweight dependency installation.
- Diffusers pipeline construction remains injectable/testable without model download in CI.
- ComfyUI execution is restricted to explicit localhost/loopback endpoints in current zero-cost local mode.
- Seed, request ID, dimensions and reference IDs stay locked through adapter execution.
- CI `32588022017`: SUCCESS.

## Change Set 029 — Provider-neutral image evidence extraction boundary
- Adds `engine/intelligence/image_evidence_extraction.py`.
- Introduces independent probe contracts for subject framing, identity, protected regions, generation defects, forbidden visuals and safe crop.
- `BaseSceneEvidenceExtractor` aggregates only typed evidence; it does not invent missing observations.
- Generated image output reference and dimensions must match local generation provenance before evidence is accepted.
- CI `32588151793`: SUCCESS.

## Change Set 030 — Zero-cost local image inspectors

### Added
- `engine/intelligence/local_vision_inspectors.py`
- `tests/test_phase18_local_vision_inspectors.py`

### Deterministic image facts
`PngFileObserver` reads exact local PNG width/height/aspect ratio using Python stdlib only. It rejects remote URLs and invalid/non-PNG outputs.

### Optional local protected-region clutter
`PillowProtectedRegionProbe` can estimate visual clutter inside deterministic logo/headline/footer/score/crest boxes when Pillow is already available locally. Pillow is optional and is not auto-installed by Phase 18.

This is deliberately treated as a pixel-clutter heuristic, not semantic object recognition.

### Fail-closed semantic probes
Until a capable free/local vision model is installed and explicitly wired:
- subject framing is not invented
- identity similarity is not invented
- semantic defect-free status is not invented
- forbidden-visual compliance is not silently assumed

Identity-required scenes therefore remain blocked when identity similarity cannot actually be measured.

### Geometry safe-crop probe
A deterministic geometry probe verifies that every approved layout box remains within the generated image canvas. It does not claim semantic crop quality.

### Capability reporting
`LocalVisionCapabilityReport` explicitly distinguishes what the current local stack can prove from semantic capabilities that remain unavailable. `publication_grade` is false unless every required capability is genuinely present.

## Production safety through Change Set 030
- `main.py`: untouched.
- Telegram production publishing: untouched.
- Legacy image sourcing/rendering: untouched.
- Production renderer/templates: untouched.
- No paid provider connected.
- No paid API selected.
- No production secret/API key added.
- No model weights or font files committed.
- No local image model executed by CI.
- Quality gates are not relaxed when semantic vision capability is unavailable.

## Architecture after Change Set 030
`Article -> Story Intelligence -> Fact / Identity / Sentiment / Neutrality -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Theme / Assets / Layout -> Generation Package -> Zero-Cost Eligibility -> Runtime / Backend Readiness -> $0 Readiness Report -> LocalBackendRequestCompiler -> Local Backend -> LocalBackendResultGate / Provenance -> Generated Image Observation -> Independent Local/Vision Evidence Probes -> BaseSceneEvidenceExtractor -> BaseSceneVisualAcceptanceGate -> Quality-First Candidate Selection -> PostComposition -> Typography -> FinalExportGate -> Platform Export`

## Next planned work
1. Verify Change Set 030 CI.
2. Add a single-command local readiness CLI/report covering runtime, backend and vision-inspection capability.
3. Evaluate free/local semantic vision options for subject framing, identity similarity and defect/forbidden-visual inspection without weakening quality.
4. Attempt the first real $0 base-scene generation only after local machine compatibility is proven.
5. Keep paid providers as future optional extensions only.
