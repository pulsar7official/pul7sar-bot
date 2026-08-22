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
- CI builds four deterministic requests using seeds `7007001`–`7007004`.
- Only the seed varies; prompt/model/platform/layout/factual constraints remain identical.
- `manifest.json` records each request ID, native canvas `1088x1360`, exact target canvas `1080x1350`, normalization requirement, and payload SHA-256.
- The candidate batch is uploaded as a multi-file GitHub Actions artifact.
- CI Run `32594690472`: SUCCESS.

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
- `tools/phase18_local_readiness.py` and the real executor use this model-specific backend preflight.
- Older Diffusers builds that import successfully but lack the required pipeline fail closed before weight loading.

## Change Set 047 — Strict Golden Visual approval floor
- Raises the Golden weighted floor to `8.5/10` and critical core dimensions to `8.0/10`.
- Adds `9.0+` `elite` classification for flagship visual targets.
- An image with a hard visual blocker remains `below_golden` regardless of score.
- Review output now exposes `quality_tier`.
- CI Run `32595997677`: SUCCESS.
- Detailed record: `docs/PHASE18_CHANGESET_047_049.md`.

## Change Set 048 — Durable executor result channel
- Single-request GPU execution can persist its structured result with `--result`.
- Batch orchestration no longer parses noisy model/runtime stdout as JSON.
- Each candidate result file is validated for status, seed and request identity.
- Missing or malformed result files fail closed.
- CI Run `32596095005`: SUCCESS.
- Detailed record: `docs/PHASE18_CHANGESET_047_049.md`.

## Change Set 049 — Production-equivalent first-candidate GPU smoke proof
- Batch executor adds `--limit N`; `--limit 1` is the first real GPU smoke path.
- The four-candidate manifest stays unchanged while only candidate 1 is executed.
- Colab now uses the same batch orchestration for the smoke proof and the eventual full batch.
- Structured partial execution report is read to locate/display the real PNG.
- CI Run `32596245628`: SUCCESS.
- Detailed record: `docs/PHASE18_CHANGESET_047_049.md`.

## Change Set 050 — CUDA-aware dtype selection
- `LocalRuntimeProbe` records BF16 support and compute capability when PyTorch can prove them.
- Adds `LocalDTypeSelector` with `auto`, `float16`, `bfloat16`, and `float32` policies.
- Real execution defaults to `auto`: BF16 only when explicitly supported; otherwise FP16.
- Explicit BF16 fails closed if support is not proven.
- Local readiness reports the recommended dtype before model loading.
- GPU execution reports requested/resolved dtype, GPU identity, VRAM, BF16 support and compute capability.
- Colab uses `--dtype auto` for both candidate 1 and the full batch.
- CI Run `32596622314`: SUCCESS for the integrated code/test path.
- Runbook CI Run `32596643514`: SUCCESS.
- Detailed record: `docs/PHASE18_CHANGESET_050_GPU_DTYPE.md`.

## Current verified Golden Visual batch
The deterministic four-candidate handoffs remain transport-ready and tamper-evident. Seeds are `7007001`, `7007002`, `7007003`, and `7007004`; only seed varies across the benchmark batch. The current code still reports truthfully that a real PNG has **not yet been generated** because a compatible CUDA runtime has not yet executed the handoff.

## Production safety through Change Set 050
- `main.py`: untouched.
- Telegram production publishing: untouched.
- Legacy production image sourcing/rendering: untouched.
- No paid provider connected.
- No paid API selected.
- No production secret/API key added.
- No model weights or font files committed.
- GitHub CPU CI does not claim to generate the FLUX image.
- No fake PNG is generated to satisfy Visual Proof.
- Missing semantic verification remains fail-closed.
- Golden Visual aesthetic approval is additional to, not a substitute for, semantic publication safety.
- Dtype fallback cannot bypass CUDA/VRAM/model readiness.

## Architecture after Change Set 050
`Article -> Story Intelligence -> Fact / Identity / Sentiment / Neutrality -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Theme / Assets / Layout -> Generation Package -> Zero-Cost Eligibility -> Portable SHA-256 Handoff -> Golden Batch Integrity -> FLUX-Specific CUDA/Diffusers Readiness -> CUDA-Aware Dtype Resolution -> --limit 1 GPU Smoke Proof -> Dedicated Result JSON -> Native FLUX PNG -> Exact Platform Normalization -> Real PNG Visual Proof -> Full Sequential Candidate Batch -> Subject/Framing + Identity Similarity + Semantic Safety + Protected-Region/Safe-Crop Inspection -> SemanticPublicationGate -> Strict Golden Visual 8.5/9.0 Quality Gate -> Quality-First Selection -> Deterministic PUL7SAR PostComposition -> Typography -> FinalExportGate -> Platform Export`

## Immediate next work
1. Execute candidate 1 on a compatible `$0` CUDA runtime with `--limit 1 --dtype auto` and register the first genuine PNG.
2. Inspect the real result against the strict Golden benchmark; generation success alone is not visual acceptance.
3. If candidate 1 proves runtime stability, execute the remaining deterministic seeds sequentially.
4. Review all real candidates and reject the entire batch if none reaches the Golden bar.
5. After the non-person Golden Visual proves the complete generation path, connect verified reference-image resolution for identity-required stories without weakening identity similarity gates.
