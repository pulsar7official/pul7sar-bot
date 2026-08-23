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

## Change Set 059 — Fail-closed Golden GPU host qualification
- Adds `engine/intelligence/gpu_host_qualification.py` to turn observed runtime facts into a deterministic eligibility receipt before queue mutation or model generation.
- Requires local CUDA runtime, CUDA-enabled PyTorch, proven GPU identity, at least the model-declared VRAM floor, explicit native BF16 support, and observable CUDA compute capability.
- Adds `tools/phase18_qualify_gpu_host.py`, a read-only JSON qualification command that installs/downloads nothing and calls no paid API.
- Adds CPU-safe regression coverage for a qualified host plus insufficient VRAM, unknown BF16, missing compute capability and CPU-only rejection cases.
- Qualification is deliberately narrower than generation/publication readiness: it does not claim model-cache, Diffusers, PNG, semantic-safety or Golden-quality success.
- Detailed record: `docs/PHASE18_CHANGESET_059_GPU_HOST_QUALIFICATION.md`.

## Change Set 060 — Integrated first-PNG fail-closed preflight
- Updates `tools/phase18_first_png.py` so the direct one-command path now incorporates the newer Change Set 059 GPU-host qualification and Change Set 058 exact-model cache preflight before Golden readiness and before durable queue mutation.
- Host qualification must return `eligible=true`; incompatible hardware fails before model-weight download.
- Model cache/prefetch must return `ready=true` and remain `$0-local`; paid-provider drift is terminal.
- Adds repository-scoped host-qualification and model-cache evidence receipts to the first-PNG result payload.
- Adds configurable positive `--minimum-free-gib` while keeping the conservative 30 GiB default.
- Adds `tests/test_phase18_first_png_preflight.py` covering strict preflight ordering, non-eligible hosts, nonzero qualification failure, cache readiness/cost lock, disk-headroom forwarding and repository-scoped evidence paths.
- No prompt, seed, canvas, provider/model identity, Fact Lock, identity, sentiment, semantic-publication or Golden-quality gate is weakened.
- Detailed record: `docs/PHASE18_CHANGESET_060_INTEGRATED_FIRST_PNG_PREFLIGHT.md`.

## Change Set 061 — Tamper-evident GPU evidence manifest
- Adds `engine/intelligence/golden_evidence_bundle.py` to hash the first real PNG, first-PNG result and explicit supporting receipts with SHA-256.
- Requires the generation result to keep `publication_ready=false`, validates a non-empty PNG signature, and rejects evidence paths outside the repository.
- Adds `tools/phase18_build_gpu_evidence_manifest.py` and CPU-safe regression tests for hashing, fake-PNG rejection, publication-gate preservation, path confinement and receipt deduplication.
- Updates `.github/workflows/phase18-gpu-smoke.yml` to build the compact evidence index after real-PNG verification and before GitHub artifact upload.
- Adds GPU-host qualification evidence to the uploaded artifact scope so the first genuine proof can be audited from hardware qualification through result bytes.
- The manifest is evidence integrity only; it cannot confer semantic safety, identity validity, Golden quality or publication readiness.
- Detailed record: `docs/PHASE18_CHANGESET_061_GPU_EVIDENCE_MANIFEST.md`.

## Change Set 062 — Replayable Golden GPU evidence verification
- Extends `engine/intelligence/golden_evidence_bundle.py` with `verify_golden_evidence_manifest`, which independently replays the canonical manifest SHA-256 plus every recorded evidence file size and SHA-256.
- Tightens first-PNG evidence construction to require non-empty job/request identity and a canonical 64-hex generation payload SHA-256.
- Rejects duplicate paths, repository-path escape, missing evidence, byte/size drift, manifest metadata drift, invalid PNG membership/signature and any mutation of `publication_ready=false`.
- Adds `tools/phase18_verify_gpu_evidence_manifest.py` to write a machine-readable verification receipt without granting semantic, visual, or publication approval.
- Updates the self-hosted GPU workflow so evidence is built, replay-verified against the actual runner bytes, and only then uploaded as an artifact.
- Expands CPU-safe regression coverage for manifest replay, metadata tampering, evidence-byte tampering, path confinement even after outer-digest recomputation, and workflow ordering.
- No prompt, seed, canvas, provider/model identity, Fact Lock, identity, sentiment, semantic-publication or Golden-quality gate is weakened.
- Detailed record: `docs/PHASE18_CHANGESET_062_EVIDENCE_REPLAY_VERIFICATION.md`.

## Change Set 063 — T4 low-VRAM sequential offload path
- First real Colab/Tesla T4 execution reached FLUX.2 transformer attention but failed with `torch.OutOfMemoryError`; the host exposed 14.56 GiB VRAM and the failing attention allocation requested an additional 3.54 GiB with only about 3.00 GiB free.
- Root cause was not handoff integrity, provider/model identity, prompt, seed, BF16 lock or CUDA readiness. The existing runtime already used Diffusers model-level CPU offload, but its peak resident CUDA footprint was still too high at the locked `1088x1360` Golden canvas.
- Updates `engine/intelligence/flux2_klein_diffusers.py` to prefer Diffusers `enable_sequential_cpu_offload()` when available and fall back to `enable_model_cpu_offload()` only when sequential offload is unavailable.
- Adds explicit `offload_mode` result metadata (`sequential_cpu`, `model_cpu`, or `none`) so real evidence can distinguish the memory strategy used.
- Preserves the exact approved model, BF16 dtype, deterministic seed, prompt, native/target canvas, guidance scale, four-step inference path, `$0-local` policy and all semantic/Golden publication gates.
- Extends `tests/test_phase18_flux2_klein_diffusers.py` to verify sequential preference, model-offload fallback and emitted offload metadata.
- Targeted Colab regression after pull: `8 passed`.
- `main` and production publishing paths remain untouched.

## Change Set 064 — First genuine T4 PNG proof
- Retrying the exact candidate-1 Golden handoff after Change Set 063 completed successfully on the Colab Tesla T4.
- Result status: `REAL_VISUAL_PROOF_GENERATED`.
- Locked seed remained `7007001`; model remained `black-forest-labs/FLUX.2-klein-4B`; dtype remained BF16; native canvas remained `1088x1360`; target canvas remained `1080x1350`; cost mode remained `$0-local`.
- Observed execution time was approximately 252.7 seconds on this T4 sample.
- The proof establishes real inference and image persistence, not semantic safety, Golden-quality acceptance, production throughput, or publication readiness.
- Human inspection exposed a visual-composition failure: the general multi-league concept was rendered as a four-panel football collage.

## Change Set 065 — Unified-scene Visual Intelligence correction
- Corrects the root prompt/scene grammar that allowed the first proof to become a collage instead of merely patching one seed.
- `VisualFamilyRouter` now routes general-world stories toward a single unified editorial scene with one focal hierarchy and continuous perspective.
- `GenerationPackageCompiler` now imposes one full-bleed physical world, one coherent camera perspective and one lighting system, and explicitly prohibits collage, montage, split-screen, grids, diptych/triptych/contact-sheet, tiled panels, framed windows, image-within-image composition, seams and panel borders.
- `PromptConstraintCompiler` adds deterministic positive reframes for the new composition constraints so FLUX-like providers cannot silently drop them.
- Golden benchmark advances to `golden-visual-general-season-opener-v2`; the old `five visual zones` language is removed and league breadth is integrated inside one stadium world.
- Golden batch advances to `pul7sar-golden-batch-v2` with `composition_grammar=single_continuous_scene` and v2 request IDs.
- Batch verification remains backward-aware for v1 but makes the v2 composition grammar and prompt lock fail-closed.
- Adds `tests/test_phase18_unified_scene_policy.py`.
- Detailed record: `docs/PHASE18_CHANGESET_064_066_COLAB_VISUAL_INTELLIGENCE.md`.

## Change Set 066 — Semi-automatic Colab Golden runner
- Adds `tools/phase18_colab_runner.py` so future Colab loops do not require manual readiness/build/verify/execute/display commands.
- Refuses to operate outside `phase18/story-intelligence` and optional update is restricted to `git pull --ff-only`.
- Always rebuilds and verifies the current Golden batch so stale handoffs from an older Visual Intelligence policy are not silently reused.
- Re-checks Golden GPU readiness, executes one selected candidate through the locked FLUX executor, verifies manifest/result seed and request identity, requires a real PNG, writes a durable Colab summary, and keeps `publication_ready=false`.
- When invoked with IPython `%run`, it attempts to display the resulting PNG inline automatically.
- Reuses a matching successful candidate unless `--force` is explicitly requested.
- Adds `tests/test_phase18_colab_runner.py`.
- Detailed record: `docs/PHASE18_CHANGESET_064_066_COLAB_VISUAL_INTELLIGENCE.md`.

## Change Set 067 — Colab CPU preflight and exact handoff-SHA result provenance
- `tools/phase18_flux2_execute.py` now replays the versioned handoff integrity check and persists the exact verified `payload_sha256` in every real GPU result.
- `tools/phase18_colab_runner.py` now runs a compact CPU-safe Golden regression preflight by default before GPU readiness/execution, covering unified-scene policy, Golden batch verification, executor handoff integrity and the Colab runner itself.
- Existing Colab result reuse is strengthened from request ID + seed to status + request ID + seed + model ID + exact payload SHA-256 + `$0-local`; legacy/stale result JSON without the digest is never silently reused.
- A fresh GPU result is checked against the same identity/SHA/cost contract before its PNG can be surfaced by the runner.
- `tests/test_phase18_flux2_execute_command.py` adds verified-digest and tamper-replay coverage.
- `tests/test_phase18_colab_runner.py` adds exact reuse-contract and legacy-result rejection coverage.
- No files deleted; no production path or quality/safety gate weakened.
- Detailed record: `docs/PHASE18_CHANGESET_067_COLAB_SHA_PREFLIGHT.md`.

## Current verified Golden Visual state
A genuine Phase 18 PNG has been generated on a Google Colab Tesla T4 using the locked FLUX.2 Klein BF16 path with sequential CPU offload. That first v1 proof is retained as technical evidence but is visually rejected as a Golden candidate because it produced a four-panel collage. The current benchmark is v2 and explicitly locks `single_continuous_scene`; Change Set 067 now guarantees that the next Colab result is bound to the exact current v2 handoff SHA before reuse or acceptance as a fresh technical proof. A v2 PNG has not yet been generated, so no Golden-quality claim is made.

## Production safety through Change Set 067
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
- GPU host qualification, model caching, evidence hashing and evidence replay do not independently imply publication readiness.
- Low-VRAM mitigation changes memory placement only; it does not weaken model, dtype, prompt, seed, canvas, factual, identity, semantic or visual-quality constraints.
- Unified-scene Visual Intelligence changes composition semantics only; exact logos, PUL7SAR branding and typography remain deterministic post-composition assets.
- Colab automation is branch-locked and cannot silently update or run against `main`.
- Colab durable-result reuse now requires the exact current handoff SHA-256 and `$0-local` contract; stale legacy output cannot be treated as a current v2 proof.

## Architecture after Change Set 067
`Article -> Story Intelligence -> Fact / Identity / Sentiment / Neutrality -> Visual Family -> Unified Single-Scene Concept Grammar -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Theme / Assets / Layout -> Generation Package -> Provider Constraint Reframing -> Zero-Cost Eligibility -> Portable SHA-256 Handoff -> Golden Batch v2 [single_continuous_scene] -> Colab CPU Regression Preflight -> Colab/Self-Hosted Golden Runner -> FLUX/BF16 Readiness -> Sequential-CPU-Offload GPU Execution -> Exact Handoff-SHA Result Binding -> CUDA High-Water Memory Telemetry -> Native FLUX PNG -> Exact Platform Normalization -> Real PNG Visual Proof -> Human/Automated Semantic Inspection -> SemanticPublicationGate -> Strict Golden Visual 8.5/9.0 Quality Gate -> Quality-First Selection -> Deterministic PUL7SAR PostComposition -> Typography -> FinalExportGate -> Platform Export`

## Immediate next work
1. Pull Change Set 067 into the active Colab T4 checkout.
2. Run `tools/phase18_colab_runner.py --update --candidate 1`; its targeted CPU regression preflight now runs automatically before GPU execution.
3. Execute only v2 candidate 1; do not spend GPU time on candidates 2–4 until the new unified-scene direction is visually judged.
4. Judge the fresh SHA-bound v2 PNG specifically for removal of collage/panel structure, editorial hierarchy, realism, protected-zone cleanliness and overall PUL7SAR direction.
5. If v2 candidate 1 is directionally correct, run the remaining deterministic seeds sequentially and apply the strict Golden scorecard.
6. Use observed successful runtimes and memory telemetry—not theoretical throughput—to size the future production GPU worker pool.
7. Keep verified-reference-person execution blocked until asset-path resolution and identity similarity remain end-to-end enforced.
