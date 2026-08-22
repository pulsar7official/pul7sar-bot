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
- CI Run `32592908056`: SUCCESS.

## Change Set 037 — Real visual proof artifact registration
- Adds `engine/intelligence/visual_proof.py`, `tools/phase18_visual_proof.py`, and tests.
- A visual proof can only be registered from a real existing PNG; the tool never fabricates a placeholder image.
- PNG dimensions are read from the real file and must match LocalGenerationProvenance.
- Registered proof writes PNG plus provenance JSON under `output/phase18_visual_proof/`.

## Change Set 038 — Clean base-scene / deterministic-overlay separation
- Updates `engine/intelligence/generation_package.py` and regression tests.
- The image model generates only the clean editorial base scene.
- PUL7SAR logo, heartbeat mark, exact club/competition crests, social icons, headline/score/footer typography, and contextual number-7/pulse treatment remain deterministic post-composition assets.
- Non-hero layout boxes are protected quiet regions, not instructions to paint overlays into the AI scene.

## Change Set 039 — Real FLUX.2 Klein local execution path
- Adds concrete `Flux2KleinPipeline` Diffusers wrapper and execution command.
- Approved model remains `black-forest-labs/FLUX.2-klein-4B`, Apache-2.0, `$0-local`.
- Generation uses deterministic seed, guidance scale `1.0`, and four inference steps.
- Optional CPU offload remains enabled for VRAM efficiency.
- No paid BFL API is connected.

## Change Set 040 — Exact platform canvas normalization
- Adds deterministic canvas normalization for model-native alignment.
- Instagram feed target `1080x1350` is generated natively at `1088x1360`, then normalized back to exact platform size.
- Similar 16-pixel alignment handling is applied to other platform canvases without changing PUL7SAR's destination geometry.
- Native dimensions and normalization metadata are preserved in provenance.

## Change Set 041 — Portable GPU generation handoff
- Adds `engine/intelligence/local_generation_handoff.py` and the Golden Visual handoff builder.
- CPU/CI can compile the exact provider/model/prompt/seed/canvas request without pretending the CPU host is generation-ready.
- GPU execution independently re-checks CUDA, VRAM and backend readiness before model invocation.
- The first general-season Golden Visual handoff is generated automatically by CI.

## Change Set 042 — Cryptographic handoff integrity
- Handoff schema advances to `pul7sar-local-generation-v2`.
- A canonical SHA-256 protects provider, model, backend, prompt, constraints, native canvas, seed, request ID, reference IDs and metadata.
- Prompt/seed/canvas/provider tampering is rejected before model execution.
- Recomputing the hash cannot bypass the independent `$0-local` cost-policy check.

## Change Set 043 — Quality-first Golden Visual candidate batch
- Adds `tools/phase18_build_golden_batch.py` and tests.
- CI now builds four deterministic requests using seeds `7007001`–`7007004`.
- Only the seed varies; prompt/model/platform/layout/factual constraints remain identical.
- `manifest.json` records each request ID, native canvas `1088x1360`, exact target canvas `1080x1350`, normalization requirement, and payload SHA-256.
- The candidate batch is uploaded as a multi-file GitHub Actions artifact.
- CI Run `32594690472`: SUCCESS.
- Artifact `9481231735` contains all four handoffs plus the manifest.

## Change Set 044 — Sequential GPU batch executor
- Adds `tools/phase18_flux2_batch_execute.py` and tests.
- Executes candidate handoffs sequentially through the same single-request executor.
- Never parallelizes model inference, avoiding VRAM contention.
- Stops on the first failed candidate.
- Verifies each returned seed against the locked batch manifest.
- Writes a machine-readable real-proof batch execution report.

## Change Set 045 — Explicit Golden Visual quality scorecard
- Adds `engine/intelligence/golden_visual_quality.py` and tests.
- Safety and aesthetics are separated: a safe scene can still fail Golden Visual quality.
- Weighted criteria cover editorial realism, composition hierarchy, stadium depth, controlled lighting, protected-zone cleanliness and platform crop strength.
- Hard blockers include fantasy/monument staging, fake logos/crests, pseudo-text, invented results, cluttered collage treatment and broken geometry/anatomy.
- A high numeric score can never override a hard blocker.
- Adds `tools/phase18_review_golden_batch.py` to enforce complete review coverage and select only among approved candidates.

## Change Set 046 — FLUX-specific Diffusers readiness
- Generic `diffusers` import is no longer enough for the approved model.
- Adds `Flux2KleinDiffusersProbe`, which proves the installed build actually exposes `Flux2KleinPipeline` without downloading weights or making network calls.
- `tools/phase18_local_readiness.py` and the real executor now use this model-specific backend preflight.
- Older Diffusers builds that import successfully but lack the required pipeline fail closed before weight loading.

## Current verified Golden Visual batch
Downloaded CI artifact contents have been independently rechecked outside GitHub Actions. All four candidate JSON payloads recompute to their declared SHA-256 values:

- seed `7007001` -> `e6a1ed5b5314bee977e0f2dd9c191f9c4f27f03bcb38b0716ff64b86964a2bfa`
- seed `7007002` -> `102390c144a158288df4f6a3c0f22eecdc2b9823d0bfe262e14bb7131a1c25ba`
- seed `7007003` -> `0dd9e4fe988ee93e718a3ea5dccab09b38c38bacd4433e6c12325b3b662b28ec`
- seed `7007004` -> `06cd395693c3b43ee1f5578e6194c9b1f24c225dd9aac7e857eac8ad99ac31ce`

Every current Golden Visual request is therefore transport-ready and tamper-evident. This does **not** mean a PNG has been generated yet.

## Production safety through Change Set 046
- `main.py`: untouched.
- Telegram production publishing: untouched.
- Legacy production image sourcing/rendering: untouched.
- No paid provider connected.
- No paid API selected.
- No production secret/API key added.
- No model weights or font files committed.
- No local image model executed by GitHub CPU CI.
- No fake PNG is generated to satisfy Visual Proof.
- Missing semantic verification remains fail-closed.
- Golden Visual aesthetic approval is now an additional gate, not a substitute for semantic publication safety.

## Architecture after Change Set 046
`Article -> Story Intelligence -> Fact / Identity / Sentiment / Neutrality -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Theme / Assets / Layout -> Generation Package -> Zero-Cost Eligibility -> Portable SHA-256 Handoff -> FLUX-Specific CUDA/Diffusers Readiness -> Sequential Candidate Generation -> Native Canvas Provenance -> Exact Platform Normalization -> Real PNG Visual Proof -> Subject/Framing + Identity Similarity + Semantic Safety + Protected-Region/Safe-Crop Inspection -> SemanticPublicationGate -> Golden Visual Quality Scorecard -> Quality-First Selection -> Deterministic PUL7SAR PostComposition -> Typography -> FinalExportGate -> Platform Export`

## Immediate next work
1. Close the current FLUX-specific readiness CI run; repair any regression before proceeding.
2. Provide the lowest-friction free-GPU execution entry point for the already-built four-candidate artifact.
3. Execute at least one genuine `$0` Golden Visual handoff on a compatible CUDA runtime and register the resulting PNG.
4. If candidate 1 is technically successful, execute the remaining batch sequentially and compare all four using the Golden Visual scorecard.
5. Reject every candidate below the visual benchmark; do not promote a merely functioning image.
6. After the non-person Golden Visual proves the generation path, connect verified reference-image asset resolution for identity-required stories.
