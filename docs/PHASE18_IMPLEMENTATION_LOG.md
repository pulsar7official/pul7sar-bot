# PUL7SAR Phase 18 — Implementation Log

This document is the authoritative implementation journal for Phase 18 on the `phase18/story-intelligence` branch.

## Change Sets 001–030
Foundation through local image inspection: Fact Lock, StoryAnalyzer, identity verification, classification, neutrality, Visual Family routing, Concept Director, sentiment, Generation Authorization, platform profiles, scene specification, exact assets, deterministic layout, dry-run manifest, theme/brand semantics, provider capability/selection/execution, post-composition, typography/final export, base-scene acceptance, zero-cost policy, provider adapters, candidate selection, generation-session orchestration, zero-cost local model profile, prompt-constraint reframing, runtime compatibility, local backend readiness/provenance, readiness report, execution boundary, optional Diffusers/ComfyUI shells, evidence extraction, and fail-closed local image inspectors. Production paths remain isolated.

## Change Set 031 — Unified local readiness service
- Adds `engine/intelligence/local_readiness_service.py`.
- Produces one truthful bundle for runtime/backend generation readiness and local vision capability.
- Separates `generation_ready` from `publication_ready`.
- A machine capable of generating is not automatically considered safe for publication.
- Maintains `$0-local` execution mode and exposes blockers/warnings.
- CI is tracked independently; no success is claimed in this log until observed.

## Change Set 032 — Zero-cost semantic vision verification policy

### Added
- `engine/intelligence/vision_verification_policy.py`
- `tests/test_phase18_vision_verification_policy.py`

### Publication-grade semantic capabilities
Current policy requires proven local zero-cost capability for:
- subject detection
- subject framing
- semantic generation-defect inspection
- forbidden-visual inspection
- protected-region clutter
- identity similarity when the story requires a verified person

### Quality-first rule
- Paid verification does not silently enter current development mode.
- Network-dependent verification does not silently enter `$0-local` mode.
- Missing semantic capabilities block publication readiness.
- Identity verification is conditional: identity similarity is mandatory for identity-required stories, but is not falsely required for scenes without a person identity requirement.

### Component architecture
Partial components may contribute individual capabilities, but no partial component is treated as a complete publication-grade verifier. For example, a local face-embedding component may satisfy identity similarity while PUL7SAR's deterministic geometry layer contributes protected-region inspection. Remaining semantic capabilities must still be proven by other local/free components.

### Research note
The first generation candidate remains FLUX.2 [klein] 4B because its 4B weights are Apache-2.0 and support local generation/editing/multi-reference. Semantic verification remains a separate concern; generation quality never substitutes for independent verification.

## Production safety through Change Set 032
- `main.py`: untouched.
- Telegram production publishing: untouched.
- Legacy image sourcing/rendering: untouched.
- Production renderer/templates: untouched.
- No paid provider connected.
- No paid API selected.
- No production secret/API key added.
- No model weights or font files committed.
- No local image model executed by CI.
- Missing semantic verification remains fail-closed.

## Architecture after Change Set 032
`Article -> Story Intelligence -> Fact / Identity / Sentiment / Neutrality -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Theme / Assets / Layout -> Generation Package -> Zero-Cost Eligibility -> Runtime / Backend Readiness -> Unified $0 Readiness -> LocalBackendRequestCompiler -> Local Backend -> Provenance -> Generated Image -> Independent Local/Vision Probes -> Semantic Verification Policy -> BaseSceneEvidenceExtractor -> BaseSceneVisualAcceptanceGate -> Quality-First Candidate Selection -> PostComposition -> Typography -> FinalExportGate -> Platform Export`

## Next planned work
1. Verify Change Set 031/032 CI.
2. Add concrete local subject/framing detector adapter contract.
3. Add local identity-similarity adapter contract using verified reference assets without coupling the domain to one face library.
4. Add local semantic defect/forbidden-visual verifier adapter contract.
5. Build a single-command readiness entry point for the user's own machine.
6. Attempt the first real `$0` base scene only after generation compatibility is proven; publication remains blocked until semantic verification is also proven.
