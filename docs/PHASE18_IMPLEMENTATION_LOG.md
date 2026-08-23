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
- Prompt/seed/canvas/provider tampering is rejected before generation.
- Recomputing the hash cannot bypass the independent `$0-local` cost-policy check.

## Change Set 043 — Quality-first Golden Visual candidate batch
- Adds `tools/phase18_build_golden_batch.py` and tests.
- CI builds four deterministic requests using seeds `7007001`–`7007004`.
- Only the seed varies; prompt/model/platform geometry, constraints and cost policy stay identical.
- `manifest.json` records request IDs, native `1088x1360`, target `1080x1350`, normalization and payload SHA-256.
- CI Run `32594690472`: SUCCESS.

## Change Set 044 — Sequential GPU batch executor
- Adds `tools/phase18_flux2_batch_execute.py` and tests.
- Executes candidate handoffs sequentially through the same single-request executor.
- Never parallelizes model inference, avoiding VRAM contention.
- Stops on the first failed candidate and verifies seed/request identity.

## Change Set 045 — Explicit Golden Visual quality scorecard
- Adds `engine/intelligence/golden_visual_quality.py` and tests.
- Safety and aesthetics are separated: a safe scene can still fail Golden Visual quality.
- Weighted criteria cover editorial realism, composition hierarchy, stadium depth, controlled lighting, protected-zone cleanliness and crop strength.
- Hard blockers include fantasy/monument staging, fake logos/crests, pseudo-text, invented results, clutter and broken geometry/anatomy.

## Change Set 046 — FLUX-specific Diffusers readiness
- Generic `diffusers` import is no longer enough for the approved model.
- Adds `Flux2KleinDiffusersProbe`, proving the installed build exposes `Flux2KleinPipeline` before weights are loaded.
- Older incompatible Diffusers builds fail closed.

## Change Set 047 — Strict Golden Visual approval floor
- Raises weighted floor to `8.5/10`, critical core dimensions to `8.0/10`, and marks `9.0+` as `elite`.
- Hard blockers override numeric score.
- CI Run `32595997677`: SUCCESS.
- Detailed record: `docs/PHASE18_CHANGESET_047_049.md`.

## Change Set 048 — Durable executor result channel
- Single-request GPU execution persists structured `--result` JSON.
- Batch orchestration no longer parses noisy model/runtime stdout.
- Missing/malformed results fail closed.
- CI Run `32596095005`: SUCCESS.

## Change Set 049 — Production-equivalent first-candidate GPU smoke proof
- Batch executor adds `--limit 1` without altering the four-candidate manifest.
- Colab uses the same orchestration as the eventual full batch.
- CI Run `32596245628`: SUCCESS.

## Change Set 050 — CUDA-aware Golden BF16 verification
- `LocalRuntimeProbe` records BF16 support and compute capability.
- `LocalDTypeSelector` locks the Golden benchmark to BF16.
- Unsupported/unproven BF16 fails closed; no FP16 fallback.
- CI Run `32596910115`: SUCCESS.
- Notebook CI Run `32596936433`: SUCCESS.
- Runbook CI Run `32596975853`: SUCCESS.
- Detailed record: `docs/PHASE18_CHANGESET_050_GPU_DTYPE.md`.

## Change Set 051 — Provider-neutral generation jobs and GPU worker service
- Adds `engine/intelligence/generation_jobs.py`, `engine/intelligence/generation_worker.py`, and worker tests.
- Defines durable job identity, bounded attempts, lease ownership/expiry, capability matching, result identity verification, explicit retryability and terminal failure semantics.
- A worker cannot silently switch provider/model/request/payload identity or bypass CUDA/BF16 requirements.

## Change Set 052 — Durable filesystem queue + locked FLUX worker adapter
- Adds `engine/intelligence/generation_job_store.py` with exclusive enqueue and atomic filesystem claims.
- Adds `engine/intelligence/flux_worker_executor.py`, connecting leased jobs to the existing real FLUX executor while keeping prompt/model/seed/canvas inside the SHA-256 handoff.
- Adds `tools/phase18_enqueue_generation.py` and `tools/phase18_gpu_worker.py`.
- Adds queue persistence and executor-boundary tests.
- Fixes immutable metadata serialization by avoiding `dataclasses.asdict()` deep-copy of `MappingProxyType`.
- Handoff integrity failures are explicit terminal failures and cannot fall into generic retry handling.
- Detailed record: `docs/PHASE18_CHANGESET_051_052_GPU_AUTOMATION.md`.

## Change Set 053 — Dead-worker lease recovery and queue telemetry
- Adds expired lease recovery to `FilesystemGenerationJobStore` for both leased and running jobs.
- Expired jobs with attempts remaining return to `queued` through the legal `retryable_failed` transition; exhausted jobs become `terminal_failed`.
- Preserves the existing attempt count and records `lease_expired` rather than pretending the prior execution succeeded or never happened.
- Adds `QueueSnapshot` and `LeaseRecoverySummary` for pending/active/state counts and explicit recovery reporting.
- `tools/phase18_gpu_worker.py` now performs recovery before every poll/execute cycle and emits queue counts plus recovered/terminal-expired job IDs.
- Adds regression tests for successful recovery, exhausted-attempt terminal failure and queue snapshots.
- No automatic model/provider/precision downgrade is introduced during recovery.

## Change Set 054 — Durable worker heartbeat and measured capacity telemetry
- Adds `engine/intelligence/worker_telemetry.py` with immutable heartbeat/performance contracts, filesystem persistence and a raw-generation capacity estimator.
- Adds `tests/test_phase18_worker_telemetry.py` covering persistence, fail-closed unproven capacity, successful-sample-only throughput math, validation and path safety.
- `tools/phase18_gpu_worker.py` now writes a durable readiness heartbeat and refreshes it after every cycle.
- Every non-idle worker cycle records observed elapsed time, GPU identity, VRAM, BF16/dtype context and outcome.
- Throughput remains numerically `unproven` until a genuine successful GPU PNG sample exists; no synthetic benchmark is accepted.
- Capacity output is explicitly labelled `raw_generation_only_not_publication_capacity`; semantic and Golden gates still determine publishability.
- Detailed record: `docs/PHASE18_CHANGESET_054_WORKER_TELEMETRY.md`.

## Change Set 055 — CUDA high-water memory and executor timing telemetry
- Adds `engine/intelligence/cuda_memory.py` with optional PyTorch CUDA peak-memory instrumentation that remains importable on CPU CI.
- Resets CUDA peak-memory counters immediately before the concrete FLUX Diffusers execution boundary when supported.
- Captures peak/current allocated and reserved memory after real visual-proof registration, never substituting fake zeroes when counters are unavailable.
- `tools/phase18_flux2_execute.py` now persists execution UTC start/finish, monotonic elapsed seconds, CUDA device index, counter-reset evidence and memory high-water metrics in the existing dedicated result JSON.
- Adds `tests/test_phase18_cuda_memory.py` covering realistic counters, unavailable CUDA and broken-counter fail-safe behavior without requiring a GPU.
- No prompt/model/seed/canvas, BF16, factual, identity, semantic-publication or Golden-quality gate is weakened.
- Detailed record: `docs/PHASE18_CHANGESET_055_CUDA_MEMORY_TELEMETRY.md`.

## Current verified Golden Visual batch
The deterministic four-candidate handoffs remain transport-ready and tamper-evident. Seeds are `7007001`, `7007002`, `7007003`, and `7007004`; only seed varies across the benchmark batch. A genuine PNG is still not claimed because a compatible CUDA/BF16 runtime has not executed the handoff.

## Production safety through Change Set 055
- `main.py`: untouched.
- Telegram production publishing: untouched.
- Legacy production image sourcing/rendering: untouched.
- No paid provider connected.
- No paid API selected.
- No production secret/API key added.
- No model weights or font files committed.
- GitHub CPU CI does not claim to generate the FLUX image.
- No fake PNG or fake performance sample is generated.
- Missing CUDA memory counters remain explicitly unavailable rather than becoming invented measurements.
- Missing semantic verification remains fail-closed.
- Golden Visual aesthetic approval remains additional to semantic publication safety.
- Unsupported or unproven BF16 does not trigger a silent precision downgrade.
- Raw generation throughput is never represented as publication throughput.

## Architecture after Change Set 055
`Article -> Story Intelligence -> Fact / Identity / Sentiment / Neutrality -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Theme / Assets / Layout -> Generation Package -> Zero-Cost Eligibility -> Portable SHA-256 Handoff -> Durable Generation Job -> Atomic Queue Lease -> Expired-Lease Recovery -> BF16/CUDA GPU Worker -> Worker Heartbeat + Measured Runtime Telemetry -> Locked FLUX Executor + CUDA High-Water Memory Telemetry -> Native FLUX PNG -> Exact Platform Normalization -> Real PNG Visual Proof -> Subject/Framing + Identity Similarity + Semantic Safety + Protected-Region/Safe-Crop Inspection -> SemanticPublicationGate -> Strict Golden Visual 8.5/9.0 Quality Gate -> Quality-First Selection -> Deterministic PUL7SAR PostComposition -> Typography -> FinalExportGate -> Platform Export`

## Immediate next work
1. Run the enqueue + worker path on a compatible `$0` CUDA/BF16 host for candidate 1.
2. Capture the first genuine PNG together with latency and CUDA high-water memory from Change Set 055.
3. Use only observed successful samples to calculate raw generation capacity and determine whether latency or VRAM is the primary worker bottleneck.
4. Inspect candidate 1 against semantic and strict Golden benchmarks; generation success alone is not acceptance.
5. If stable, execute the remaining deterministic seeds through the same durable worker path.
6. Add a distributed queue adapter only after the single-host worker is proven, preserving `GenerationJobStore` semantics.
7. Keep verified-reference-person execution blocked until asset-path resolution and identity similarity remain end-to-end enforced.
