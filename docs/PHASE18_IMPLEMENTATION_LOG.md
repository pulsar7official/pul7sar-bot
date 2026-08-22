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
- CI Run `32588437912`: SUCCESS.

## Change Set 032 — Zero-cost semantic vision verification policy
- Adds `engine/intelligence/vision_verification_policy.py` and tests.
- Publication-grade local verification requires subject detection/framing, semantic defect inspection, forbidden-visual inspection, protected-region clutter, and identity similarity when a verified person is required.
- Paid/network-dependent verification cannot silently enter `$0-local` development mode.
- Missing capability blocks publication readiness.

## Change Set 033 — Semantic publication gate
- Adds `engine/intelligence/semantic_publication_gate.py` and tests.
- Separates generated, base-scene accepted, semantic-verification complete, and publication-ready states.
- Cross-checks locked identity reference IDs from the GenerationPackage against the evidence used for visual identity verification.
- CI Run `32592258604`: SUCCESS.

## Change Set 034 — Local subject/framing verifier contract
- Adds `engine/intelligence/local_subject_verifier.py`.
- Introduces provider-neutral subject presence, full-visibility, hero-region usability, and confidence contracts.
- Fails closed on absent expected subject, unsafe crop/framing, unusable hero region, or low confidence.
- Initial test fixture used obsolete `GeneratedImageObservation` fields and was corrected in commit `fef938174ffffb5e64d52b1f456e0cd59a2d80c0` to match the actual observation contract.

## Change Set 035 — Local identity similarity contract
- Adds `engine/intelligence/local_identity_similarity.py` and tests.
- Uses only identity reference asset IDs already locked into the GenerationPackage.
- The verifier may not replace, omit, or drift from those references.
- Required-person scenes fail closed on mismatch or identity confidence below 0.90.
- The domain remains independent of any particular face-embedding library.

## Change Set 036 — Local semantic safety contract
- Adds `engine/intelligence/local_semantic_safety.py` and tests.
- Separates generation defects and forbidden-visual detection from subject and identity checks.
- The semantic-safety request must exactly match the package's locked forbidden-visual constraints.
- Low confidence, semantic defects, or forbidden elements block the scene.
- CI Run `32592908056` after subject/identity/semantic contract integration: SUCCESS.

## Change Set 037 — Real visual proof artifact registration
- Adds `engine/intelligence/visual_proof.py`.
- Adds `tools/phase18_visual_proof.py`.
- Adds `tests/test_phase18_visual_proof.py`.
- A visual proof can only be registered from a real existing PNG; the tool never fabricates a placeholder image.
- PNG dimensions are read from the real file and must match LocalGenerationProvenance.
- The registered proof writes both `<request_id>.png` and `<request_id>.json` into `output/phase18_visual_proof/`.
- Metadata records model, provider, backend, deterministic seed, request ID, dimensions, aspect ratio, `$0-local` mode, and output reference.
- The existing Phase 18 GitHub workflow will expose real PNGs from this directory as visual-proof artifacts.

## Change Set 038 — Clean base-scene / deterministic-overlay separation
- Updates `engine/intelligence/generation_package.py` and regression tests.
- Removes contradictory prompt language that previously told the AI generator to use exact PUL7SAR/club marks even though official branding is owned by post-composition.
- The AI prompt now explicitly generates only the clean editorial base scene.
- PUL7SAR logo, heartbeat mark, exact club/competition crests, social icons, headline/score/footer typography, and contextual number-7/pulse treatment remain deterministic post-composition assets.
- Non-hero layout boxes are treated as protected quiet regions for later overlays rather than instructions to paint overlays into the AI image.
- Current CI for this final integration is tracked separately and must be green before Change Set 038 is considered closed.

## Production safety through Change Set 038
- `main.py`: untouched.
- Telegram production publishing: untouched.
- Legacy production image sourcing/rendering: untouched.
- No paid provider connected.
- No paid API selected.
- No production secret/API key added.
- No model weights or font files committed.
- No local image model executed by GitHub CI.
- No fake PNG is generated to satisfy Visual Proof.
- Missing semantic verification remains fail-closed.

## Architecture after Change Set 038
`Article -> Story Intelligence -> Fact / Identity / Sentiment / Neutrality -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Theme / Assets / Layout -> Generation Package -> Zero-Cost Eligibility -> Runtime / Backend Readiness -> Unified $0 Readiness -> LocalBackendRequestCompiler -> Local Backend -> Provenance -> Real PNG -> Subject/Framing + Identity Similarity + Semantic Safety + Protected-Region/Safe-Crop Inspection -> SemanticPublicationGate -> Quality-First Candidate Selection -> Deterministic PUL7SAR PostComposition -> Typography -> FinalExportGate -> Visual Proof Artifact / Platform Export`

## Immediate next work
1. Close Change Set 038 CI; repair any regression before proceeding.
2. Build the real GPU execution handoff so the same generation request can run on a compatible local/self-hosted/temporary free GPU runtime without coupling the PUL7SAR core to that environment.
3. Produce the first genuine `$0` base-scene PNG and register it through `phase18_visual_proof.py`.
4. Inspect the resulting PNG against the Golden Visual benchmark; do not equate successful generation with visual acceptance.
5. Connect concrete local zero-cost semantic verifier implementations only after licensing/runtime/quality are proven.
