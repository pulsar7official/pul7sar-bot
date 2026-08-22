# PUL7SAR Phase 18 — Implementation Log

This document is the authoritative implementation journal for Phase 18 on the `phase18/story-intelligence` branch.

## Change Sets 001–019
Previously documented foundation: Fact Lock, StoryAnalyzer, identity verification, classification, neutrality, Visual Family routing, perspective-aware result sentiment, Concept Director, sentiment resolver, Generation Authorization, platform profiles, Original Scene Specification, exact assets, layout safety, multi-platform packages, deterministic layout, dry-run manifest, entity theme, exact brand semantics, provider capability/selection/execution, post-composition, deterministic typography/final export, and base-scene visual acceptance. Production paths remain isolated.

## Change Set 020 — Zero-cost development enforcement
- Adds `engine/intelligence/cost_policy.py`.
- Current development execution accepts only proven zero-cost/local or genuinely free-tier providers without a required payment method.
- Paid/unknown-cost providers remain modelable for future expansion but are not selectable in current zero-cost mode.
- Provider selection applies cost eligibility before technical selection.
- Quality thresholds are never relaxed to satisfy zero-cost operation.

## Change Set 021 — Provider evidence adapters + quality-first candidate selection
- Adds provider-native normalization boundary and quality-first candidate ranking.
- Only BaseScene-gate-approved candidates can score above zero.
- Identity, framing and protected-region cleanliness determine candidate quality; cost does not.
- No accepted candidate -> `NO_ACCEPTABLE_SCENE`; there is no degraded fallback.
- Adds future Social/Video architecture document.
- CI `32585786963`: SUCCESS.

## Change Set 022 — Generation Session Orchestrator

### Added
- `engine/intelligence/generation_session.py`
  - provider-neutral bounded generation loop
  - provider-ID integrity
  - candidate-count enforcement
  - normalization through `ProviderAdapterRegistry`
  - accumulated global candidate selection
  - per-attempt diagnostics
  - explicit `minimum_quality_score` above basic gate pass
  - retry when a gate-passing image remains below the PUL7SAR quality floor
  - no best-bad-image fallback after attempt exhaustion
- `tests/test_phase18_generation_session.py`

### CI discoveries and fixes
The first implementation exposed two useful regression cases rather than being merged blindly:
1. The lower-level regeneration controller stopped on `ACCEPTED` even when the session-level quality floor was not reached. Ownership was corrected: gate-pass-but-below-floor retries are controlled by the Generation Session layer.
2. Diagnostics originally counted accepted candidates across all accumulated attempts while recording only current-attempt candidate count. This was corrected so diagnostics evaluate each attempt separately while global selection still ranks all candidates across the session.

The regression test now asserts that each attempt's `accepted_count` cannot leak accumulated counts from previous attempts.

### Validation
- Final CI after both fixes: `32586498538`: SUCCESS.
- Syntax: PASS.
- Phase 18 tests: PASS.
- Production isolation: PASS.

## Change Set 023 — First zero-cost local image-model evaluation profile

### Added
- `engine/intelligence/zero_cost_models.py`
- `engine/intelligence/provider_prompting.py`
- `tests/test_phase18_zero_cost_model.py`
- `docs/ZERO_COST_IMAGE_PROVIDER_EVALUATION.md`

### First candidate
`black-forest-labs/FLUX.2-klein-4B`

This is an evaluation profile only; it is not claimed to be installed or executed on the user's machine.

The profile records:
- local/no per-image API cost path
- Apache-2.0 4B weights
- text-to-image and multi-reference capability
- conservative 13 GB VRAM runtime floor based on the official model card
- current PUL7SAR platform canvases inside the declared 4-megapixel evaluation envelope
- no assumption of native negative-prompt support

### Constraint prompting
Official FLUX.2 guidance states that negative prompting is not supported. PUL7SAR therefore does not silently drop forbidden constraints. `PromptConstraintCompiler` deterministically reframes known constraints into positive desired scene instructions. Unknown constraints fail closed and block that provider package.

Examples include neutrality, no humiliation, pre-signing transfer states, no invented result and restrained injury/harm treatment.

## Change Set 024 — Local runtime capability gate

### Added
- `engine/intelligence/local_runtime.py`
  - `RuntimeKind`
  - `RuntimeHardwareSnapshot`
  - `RuntimeCompatibilityDecision`
  - `LocalRuntimeProbe`
  - `LocalModelRuntimeGate`
- `tests/test_phase18_local_runtime.py`

### Rules
- Local runtime probing is best-effort and does not make PyTorch a hard Phase 18 dependency.
- Missing PyTorch/CUDA is recorded rather than crashing the domain.
- The FLUX.2 klein 4B candidate is not automatically approved on CPU-only or unknown-VRAM hardware.
- Unknown GPU memory fails closed.
- VRAM below the declared candidate floor fails closed.
- A proven CUDA runtime meeting the declared floor can pass the compatibility gate.

### Validation
- CI `32586567250`: SUCCESS.

## Production safety through Change Set 024
- `main.py`: untouched.
- Telegram production publishing: untouched.
- Legacy image sourcing/rendering: untouched.
- Production renderer/templates: untouched.
- No paid provider connected.
- No BFL paid API selected.
- No production secret/API key added.
- No model weights or font files committed to the repository.

## Architecture after Change Set 024
`Article -> Story Intelligence -> Fact / Identity / Sentiment / Neutrality -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Theme / Assets / Layout -> Generation Package -> Zero-Cost Provider Eligibility -> Local Runtime Compatibility -> Execution Plan -> Provider Prompt Constraint Compilation -> Generation Session -> Provider Adapter -> BaseSceneVisualAcceptanceGate -> Quality-First Candidate Selection -> PostComposition -> Typography -> FinalExportGate -> Platform Export`

## Next planned work
1. Add an optional local backend contract for Diffusers/ComfyUI without making either a hard repository dependency.
2. Build an install/runtime readiness report rather than silently installing heavy model dependencies.
3. Add local output-file provenance and deterministic seed/session metadata.
4. Build evidence extraction interfaces for identity/framing/protected-region/defect probes from actual generated images.
5. Only after runtime readiness is proven should the first real local image generation be attempted.
