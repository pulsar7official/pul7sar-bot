# PUL7SAR Phase 18 — Implementation Log

This document is the authoritative implementation journal for Phase 18 on the `phase18/story-intelligence` branch.

## Change Sets 001–030 — Intelligence and generation foundation
Foundation through local image inspection: Fact Lock, StoryAnalyzer, identity verification, classification, neutrality, Visual Family routing, Concept Director, sentiment, Generation Authorization, platform profiles, scene specification, exact assets, deterministic layout, dry-run manifest, theme/brand semantics, provider capability/selection/execution, post-composition, typography/final export, base-scene acceptance, zero-cost policy, provider adapters, candidate selection, generation-session orchestration, zero-cost local model profile, prompt-constraint reframing, runtime compatibility, local backend readiness/provenance, readiness report, execution boundary, optional Diffusers/ComfyUI shells, evidence extraction, and fail-closed local image inspectors. Production paths remain isolated.

## Change Set 031 — Unified local readiness service
- Adds `engine/intelligence/local_readiness_service.py`.
- Separates generation readiness from publication readiness and exposes blockers/warnings.
- CI Run `32588437912`: SUCCESS.

## Change Set 032 — Zero-cost semantic vision verification policy
- Requires subject/framing, semantic-defect, forbidden-visual, protected-region and identity checks where applicable.
- Missing local capability blocks publication readiness; paid/network verification cannot silently enter `$0-local` mode.

## Change Set 033 — Semantic publication gate
- Adds `engine/intelligence/semantic_publication_gate.py` and tests.
- Cross-checks locked identity references against visual verification evidence.
- CI Run `32592258604`: SUCCESS.

## Change Set 034 — Local subject/framing verifier
- Adds provider-neutral subject presence, full visibility, hero-region usability and confidence contracts.
- Fails closed on absent subject, unsafe crop/framing or low confidence.

## Change Set 035 — Local identity similarity contract
- Uses only identity reference IDs already locked into the GenerationPackage.
- Required-person scenes fail closed on mismatch or identity confidence below 0.90.

## Change Set 036 — Local semantic safety contract
- Separates generation defects/forbidden visuals from subject and identity checks.
- CI Run `32592908056`: SUCCESS.

## Change Set 037 — Real visual-proof registration
- Registers only real existing PNGs and validates dimensions against generation provenance.
- Never fabricates a placeholder proof.

## Change Set 038 — Clean base scene / deterministic overlay separation
- The image model generates only the editorial base scene.
- Exact logos, crests, social marks and typography remain deterministic post-composition assets.

## Change Set 039 — Real FLUX.2 Klein local execution
- Adds concrete Diffusers `Flux2KleinPipeline` execution for `black-forest-labs/FLUX.2-klein-4B`.
- Apache-2.0, `$0-local`, deterministic seed, guidance 1.0, four inference steps.
- No paid BFL API is connected.

## Change Set 040 — Exact platform canvas normalization
- Generates Instagram feed at aligned `1088x1360`, then deterministically normalizes to exact `1080x1350`.

## Change Set 041 — Portable GPU generation handoff
- CPU/CI compiles exact provider/model/prompt/seed/canvas without claiming GPU readiness.
- GPU execution independently re-checks CUDA, VRAM and backend readiness.

## Change Set 042 — Cryptographic handoff integrity
- Handoff schema `pul7sar-local-generation-v2` protects provider, model, prompt, constraints, canvas, seed, request ID, references and metadata with canonical SHA-256.

## Change Set 043 — Quality-first Golden batch
- Builds deterministic seeds `7007001`–`7007004`; only seed varies.
- Manifest locks native/target canvas, request IDs and payload hashes.
- CI Run `32594690472`: SUCCESS.

## Change Set 044 — Sequential GPU batch executor
- Executes candidates sequentially through the same locked single-request path and stops on first failure.

## Change Set 045 — Explicit Golden Visual scorecard
- Separates safety from aesthetics.
- Hard blockers include fantasy staging, fake logos/crests, pseudo-text, invented results, clutter and broken geometry/anatomy.

## Change Set 046 — FLUX-specific Diffusers readiness
- Proves installed Diffusers exposes `Flux2KleinPipeline`; generic package import is insufficient.

## Change Set 047 — Strict Golden approval floor
- Weighted minimum `8.5/10`; critical core dimensions `8.0/10`; `9.0+` is `elite`.
- Hard blockers override score.
- CI Run `32595997677`: SUCCESS.

## Change Set 048 — Durable executor result channel
- GPU executor persists structured JSON instead of requiring stdout parsing.
- CI Run `32596095005`: SUCCESS.

## Change Set 049 — Production-equivalent candidate-1 smoke path
- Adds `--limit 1` without altering the four-candidate manifest.
- CI Run `32596245628`: SUCCESS.

## Change Set 050 — CUDA-aware Golden BF16 verification
- Locks Golden generation to proven native BF16; no silent FP16 downgrade.
- CI Run `32596910115`: SUCCESS.
- Notebook CI Run `32596936433`: SUCCESS.
- Runbook CI Run `32596975853`: SUCCESS.
- Detailed record: `docs/PHASE18_CHANGESET_050_GPU_DTYPE.md`.

## Change Set 051 — Provider-neutral generation jobs and GPU worker
- Adds durable job identity, bounded attempts, lease ownership/expiry, capability matching, result identity checks, retryability and terminal failure semantics.

## Change Set 052 — Durable filesystem queue + locked FLUX worker adapter
- Adds `FilesystemGenerationJobStore`, FLUX worker adapter, enqueue command and GPU worker command.
- Fixes immutable metadata serialization and makes handoff-integrity failure terminal.
- Detailed record: `docs/PHASE18_CHANGESET_051_052_GPU_AUTOMATION.md`.

## Change Set 053 — Dead-worker recovery and queue telemetry
- Recovers expired leased/running jobs without resetting attempt history.
- Exhausted jobs become terminal; queue snapshots expose state counts.

## Change Set 054 — Durable heartbeat and measured capacity telemetry
- Persists worker readiness/heartbeat and real execution timing.
- Throughput remains `unproven` until a genuine successful GPU PNG exists.
- Raw generation capacity is never represented as publication capacity.
- Detailed record: `docs/PHASE18_CHANGESET_054_WORKER_TELEMETRY.md`.

## Change Set 055 — CUDA high-water memory telemetry
- Adds optional PyTorch CUDA peak-memory instrumentation and executor timing.
- Missing counters remain unavailable rather than becoming fake zeros.
- Detailed record: `docs/PHASE18_CHANGESET_055_CUDA_MEMORY_TELEMETRY.md`.

## Change Set 056 — One-command first genuine Golden PNG
- Adds `engine/intelligence/golden_smoke.py` and `tools/phase18_first_png.py`.
- Composes Golden batch verification, CUDA/FLUX/BF16 readiness, durable enqueue, one normal worker cycle and real-PNG existence validation.
- Incompatible hosts fail before queue mutation.
- Generation success remains `publication_ready=false` pending semantic and Golden review.
- CI Run `32611296349`: SUCCESS.
- Detailed record: `docs/PHASE18_CHANGESET_056_ONE_COMMAND_FIRST_PNG.md`.

## Change Set 057 — Self-hosted GPU Golden smoke workflow
- Adds `.github/workflows/phase18-gpu-smoke.yml` for manually confirmed, explicitly labelled self-hosted Linux/x64/CUDA/BF16 runners.
- Reuses the locked one-command path and uploads real evidence as a GitHub artifact.
- Does not install/replace PyTorch automatically and embeds no paid-provider secret.
- Detailed record: `docs/PHASE18_CHANGESET_057_SELF_HOSTED_GPU_SMOKE.md`.

## Change Set 058 — Fail-closed model-cache preflight
- Adds `engine/intelligence/model_cache.py` with explicit cached/uncached qualification and conservative disk-headroom checks.
- Adds `tools/phase18_prefetch_flux2.py` to prove or download only the approved `black-forest-labs/FLUX.2-klein-4B` open-weight snapshot before GPU generation.
- Writes a machine-readable cache receipt containing provider/model/license/cost mode, cache path, apparent snapshot size and qualification evidence.
- Adds `tests/test_phase18_model_cache.py` covering cached eligibility, insufficient/sufficient disk, unknown-space fail-closed behavior and input validation.
- Strengthens `tests/test_phase18_gpu_smoke_workflow.py` to require model prefetch before model-specific readiness and before the first-PNG command.
- Makes `huggingface_hub` an explicit GPU-side dependency.
- Updates the self-hosted GPU smoke workflow to prefetch/verify the exact model before Golden readiness and generation, avoiding wasted GPU time on first-run storage/download failures.
- No prompt, seed, canvas, factual, identity, sentiment, semantic-publication or Golden-quality gate is weakened.
- Detailed record: `docs/PHASE18_CHANGESET_058_MODEL_CACHE_PREFLIGHT.md`.

## Current verified Golden Visual batch
The deterministic four-candidate handoffs remain transport-ready and tamper-evident. Seeds are `7007001`, `7007002`, `7007003`, and `7007004`; only seed varies. A genuine PNG is still not claimed because a compatible CUDA/BF16 runtime has not executed the handoff.

## Production safety through Change Set 058
- `main`: untouched by Phase 18 development changes.
- `main.py`: untouched.
- Telegram production publishing: untouched.
- Legacy production image sourcing/rendering: untouched.
- No paid provider or paid image API selected.
- No production secret/API key added.
- No model weights or font files committed.
- GitHub CPU CI does not claim to generate a FLUX image.
- No fake PNG or fake performance sample is generated.
- Missing semantic verification remains fail-closed.
- Golden Visual approval remains additional to semantic publication safety.
- Unsupported/unproven BF16 does not trigger a silent precision downgrade.
- Raw generation throughput is never represented as publication throughput.
- First-PNG orchestration fails before enqueueing if Golden GPU readiness is not proven.
- Model caching does not imply GPU readiness or publication readiness.

## Architecture after Change Set 058
`Article -> Story Intelligence -> Fact / Identity / Sentiment / Neutrality -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Theme / Assets / Layout -> Generation Package -> Zero-Cost Eligibility -> Portable SHA-256 Handoff -> Verified Golden Batch -> Approved Model Cache Preflight -> One-Command Smoke Coordinator -> Durable Generation Job -> Atomic Queue Lease -> Expired-Lease Recovery -> BF16/CUDA GPU Worker -> Worker Heartbeat + Measured Runtime Telemetry -> Locked FLUX Executor + CUDA High-Water Memory Telemetry -> Native FLUX PNG -> Exact Platform Normalization -> Real PNG Visual Proof -> Subject/Framing + Identity Similarity + Semantic Safety + Protected-Region/Safe-Crop Inspection -> SemanticPublicationGate -> Strict Golden Visual 8.5/9.0 Quality Gate -> Quality-First Selection -> Deterministic PUL7SAR PostComposition -> Typography -> FinalExportGate -> Platform Export`

## Immediate next work
1. Attach/provide a compatible NVIDIA CUDA/BF16 host with sufficient VRAM; GitHub orchestration requires labels `gpu`, `cuda`, `bf16`, `pul7sar-phase18` plus standard self-hosted Linux/x64 labels.
2. Run the manual `Phase 18 GPU Golden Smoke` workflow with confirmation `RUN_PHASE18_GOLDEN_GPU`, or execute `tools/phase18_first_png.py` directly on the host after `tools/phase18_prefetch_flux2.py`.
3. Capture the first genuine PNG plus latency, CUDA memory high-water data and model-cache receipt.
4. Inspect candidate 1 against semantic and strict Golden benchmarks; generation success alone is not acceptance.
5. If stable, execute remaining deterministic seeds through the same worker path and compute capacity only from observed successful samples.
6. Add distributed queue infrastructure only after the single-host worker is proven, preserving `GenerationJobStore` semantics.
7. Keep verified-reference-person execution blocked until asset-path resolution and identity similarity remain end-to-end enforced.
