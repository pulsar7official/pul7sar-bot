# PUL7SAR Phase 18 — Implementation Log

This document is the authoritative implementation journal for Phase 18 on the `phase18/story-intelligence` branch. Phase 18 remains isolated from `main` and production publishing paths unless a future explicit merge is approved.

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

## Change Sets 034–038 — Local semantic/identity verification and exact-overlay separation
- Adds local subject/framing verification, identity-similarity contracts, semantic-safety contracts and real PNG proof registration.
- Required-person scenes fail closed on missing/mismatched identity evidence.
- Exact logos, crests, social marks and typography are deterministic post-composition assets and must not be hallucinated by the image model.

## Change Set 039 — Real FLUX.2 Klein local execution
- Adds concrete Diffusers `Flux2KleinPipeline` execution for `black-forest-labs/FLUX.2-klein-4B`.
- Apache-2.0, `$0-local`, deterministic seed, guidance 1.0, four inference steps.
- No paid BFL API is connected.

## Change Sets 040–042 — Exact canvas, portable GPU handoff and cryptographic integrity
- Generates Instagram feed at aligned `1088x1360`, then deterministically normalizes to exact `1080x1350`.
- CPU/CI compiles provider/model/prompt/seed/canvas without claiming GPU readiness.
- Handoff schema `pul7sar-local-generation-v2` protects provider, model, prompt, constraints, canvas, seed, request ID, references and metadata with canonical SHA-256.

## Change Set 043 — Quality-first Golden batch
- Builds deterministic seeds `7007001`–`7007004`; only seed varies.
- Manifest locks native/target canvas, request IDs and payload hashes.
- CI Run `32594690472`: SUCCESS.

## Change Sets 044–050 — Sequential execution, Golden quality and BF16 lock
- Executes candidates sequentially through the same locked single-request path.
- Golden Visual quality is separate from semantic safety; hard blockers override aesthetic score.
- Weighted Golden minimum is `8.5/10`, critical core floor `8.0/10`, `9.0+` is `elite`.
- Durable executor result JSON replaces stdout parsing.
- Golden generation is locked to proven native BF16 with no silent FP16 downgrade.
- CI Runs include `32595997677`, `32596095005`, `32596245628`, `32596910115`, `32596936433`, `32596975853`: SUCCESS.
- Detailed record: `docs/PHASE18_CHANGESET_050_GPU_DTYPE.md`.

## Change Sets 051–053 — Durable generation jobs, worker queue and recovery
- Adds provider-neutral generation jobs, bounded attempts, leases, worker capability matching and result identity checks.
- Adds `FilesystemGenerationJobStore`, locked FLUX worker adapter, enqueue command and GPU worker command.
- Handoff-integrity failure is terminal; expired leases can be recovered without resetting attempt history.
- Detailed record: `docs/PHASE18_CHANGESET_051_052_GPU_AUTOMATION.md`.

## Change Set 054 — Durable heartbeat and measured capacity telemetry
- Persists worker readiness/heartbeat and real execution timing.
- Throughput remains `unproven` until genuine successful GPU generation exists; raw generation capacity is never publication capacity.
- Detailed record: `docs/PHASE18_CHANGESET_054_WORKER_TELEMETRY.md`.

## Change Set 055 — CUDA high-water memory telemetry
- Adds optional PyTorch CUDA peak-memory instrumentation and executor timing.
- Missing counters remain unavailable rather than fake zeros.
- Detailed record: `docs/PHASE18_CHANGESET_055_CUDA_MEMORY_TELEMETRY.md`.

## Change Set 056 — One-command first genuine Golden PNG
- Adds `engine/intelligence/golden_smoke.py` and `tools/phase18_first_png.py`.
- Composes Golden batch verification, CUDA/FLUX/BF16 readiness, durable enqueue, one normal worker cycle and real-PNG validation.
- Incompatible hosts fail before queue mutation; generation success remains `publication_ready=false` pending semantic and Golden review.
- CI Run `32611296349`: SUCCESS.
- Detailed record: `docs/PHASE18_CHANGESET_056_ONE_COMMAND_FIRST_PNG.md`.

## Change Set 057 — Self-hosted GPU Golden smoke workflow
- Adds `.github/workflows/phase18-gpu-smoke.yml` for manually confirmed self-hosted Linux/x64/CUDA/BF16 runners.
- Reuses the locked one-command path and uploads genuine evidence only; no paid-provider secret is embedded.
- Detailed record: `docs/PHASE18_CHANGESET_057_SELF_HOSTED_GPU_SMOKE.md`.

## Change Set 058 — Fail-closed model-cache preflight
- Adds exact `black-forest-labs/FLUX.2-klein-4B` cache qualification/prefetch with conservative disk-headroom checks and `$0-local` receipt.
- `huggingface_hub` becomes an explicit GPU-side dependency.
- Detailed record: `docs/PHASE18_CHANGESET_058_MODEL_CACHE_PREFLIGHT.md`.

## Change Set 059 — Fail-closed GPU host qualification
- Requires local CUDA, CUDA-enabled PyTorch, proven GPU identity, required VRAM, explicit native BF16 support and observable compute capability before generation.
- Adds read-only `tools/phase18_qualify_gpu_host.py`.
- Detailed record: `docs/PHASE18_CHANGESET_059_GPU_HOST_QUALIFICATION.md`.

## Change Set 060 — Integrated first-PNG fail-closed preflight
- `tools/phase18_first_png.py` composes host qualification, exact-model cache preflight, readiness and queue mutation in fail-closed order.
- Adds repository-scoped qualification/cache evidence; no safety or quality gate is weakened.
- Detailed record: `docs/PHASE18_CHANGESET_060_INTEGRATED_FIRST_PNG_PREFLIGHT.md`.

## Change Set 061 — Tamper-evident GPU evidence manifest
- Hashes first real PNG and supporting receipts with SHA-256, validates PNG signature and repository path confinement.
- Evidence integrity never implies publication readiness.
- Detailed record: `docs/PHASE18_CHANGESET_061_GPU_EVIDENCE_MANIFEST.md`.

## Change Set 062 — Replayable Golden GPU evidence verification
- Independently replays manifest/evidence hashes, sizes, path confinement, PNG membership/signature and `publication_ready=false`.
- Adds `tools/phase18_verify_gpu_evidence_manifest.py` and inserts replay verification before artifact upload.
- Detailed record: `docs/PHASE18_CHANGESET_062_EVIDENCE_REPLAY_VERIFICATION.md`.

## Change Set 063 — T4 low-VRAM sequential offload path
- First real Colab/Tesla T4 attempt reached FLUX.2 transformer attention but failed with CUDA OOM on the locked canvas.
- `engine/intelligence/flux2_klein_diffusers.py` now prefers Diffusers sequential CPU offload and falls back to model CPU offload only when required.
- Result metadata records `offload_mode`; model, BF16, prompt, seed, canvas, guidance, four-step inference and `$0-local` remain unchanged.
- Targeted Colab regression after pull: `8 passed`.

## Change Set 064 — First genuine T4 PNG proof
- The exact candidate-1 handoff completed successfully after Change Set 063 on a Colab Tesla T4.
- Status: `REAL_VISUAL_PROOF_GENERATED`; seed `7007001`; `black-forest-labs/FLUX.2-klein-4B`; BF16; native `1088x1360`; target `1080x1350`; `$0-local`.
- Observed execution time was about 252.7 seconds.
- This proved genuine inference/persistence only. Human review rejected the visual because the general multi-league concept became a four-panel football collage.

## Change Set 065 — Unified-scene Visual Intelligence correction
- Replaces collage-permissive general-world grammar with one full-bleed physical world, one coherent camera perspective, one lighting system and one focal hierarchy.
- Explicitly forbids collage, montage, split-screen, grids, diptych/triptych/contact-sheet, tiled panels, framed windows, image-within-image composition, seams and panel borders.
- Golden benchmark advanced to v2 with `composition_grammar=single_continuous_scene`.
- Detailed record: `docs/PHASE18_CHANGESET_064_066_COLAB_VISUAL_INTELLIGENCE.md`.

## Change Set 066 — Semi-automatic Colab Golden runner
- Adds `tools/phase18_colab_runner.py`, branch-locked to `phase18/story-intelligence` with optional `git pull --ff-only` update.
- Rebuilds/verifies current Golden batch, re-checks GPU readiness, executes selected candidate, binds result identity, requires real PNG and keeps `publication_ready=false`.
- Detailed record: `docs/PHASE18_CHANGESET_064_066_COLAB_VISUAL_INTELLIGENCE.md`.

## Change Set 067 — Colab CPU preflight and exact handoff-SHA result provenance
- FLUX executor persists the verified `payload_sha256`; Colab result reuse now requires status + request ID + seed + model + exact SHA + `$0-local`.
- Colab runs CPU-safe Golden regression preflight before GPU readiness/execution.
- Detailed record: `docs/PHASE18_CHANGESET_067_COLAB_SHA_PREFLIGHT.md`.

## Change Set 068 — Golden v2 smoke compatibility and CI regression repair
- Repairs stale v1 assumptions after the v2 migration and adds Golden batch/smoke modules to Colab targeted preflight.
- GitHub Actions Run `32629634107`: SUCCESS.
- Detailed record: `docs/PHASE18_CHANGESET_068_GOLDEN_V2_SMOKE_COMPAT.md`.

## Intervening visual corrections after the v2 proof — regulation geometry and exact-brand exclusion
A second genuine Colab proof established that the single-scene correction removed the prior four-panel structure, but human inspection found two new hard visual failures: malformed association-football pitch markings/geometry and an AI-generated `PUL7SAR` text treatment that was not the approved logo.

The active Golden benchmark therefore advanced cumulatively:
- v3 locks `sport_geometry=association_football_regulation_pitch`, including one halfway line, one correctly placed centre circle/mark, coherent penalty/goal areas, goal lines/touchlines and perspective-consistent markings. `GoldenVisualBlockers` gained `broken_sport_surface_geometry`.
- v4 locks `generated_branding_allowed=false` and `brand_composition_policy=exact_assets_only_after_generation`. The AI base scene must contain zero PUL7SAR/PULSAR lettering, generated wordmark, number-7/pulse treatment, readable sponsor text, pseudo-text or substitute platform branding. `GoldenVisualBlockers` gained `generated_platform_brand_or_wordmark`.
- `GenerationPackageCompiler`, `PromptConstraintCompiler`, Golden handoff/batch builders, verifier and unified-scene regression tests enforce those cumulative locks.
- Detailed brand-exclusion record: `docs/PHASE18_CHANGESET_068_EXACT_BRANDING_EXCLUSION.md` (historical filename retained even though Change Set 068 was already used by the earlier v2 smoke repair).

## Change Set 069 — Golden v4 durable-smoke compatibility
- Branch review found a real integration mismatch: the active builder/verifier were already v4, while `engine/intelligence/golden_smoke.py` still accepted only v1/v2 and `tests/test_phase18_golden_smoke.py` still expected the v2 request ID.
- `golden_smoke.py` now supports v1–v4 and applies cumulative fail-closed manifest locks: v2+ unified scene, v3+ regulation football-pitch geometry, v4 generated-brand prohibition plus exact-assets-only post-generation branding.
- Before candidate 1 may enter the durable queue, the coordinator also replays matching SHA-protected prompt markers for unified composition, sport geometry and brand exclusion.
- `tests/test_phase18_golden_smoke.py` now expects `golden-general-season-opener-v4-001` and adds regression coverage for grammar, geometry, generated-brand permission and brand-composition-policy drift while retaining SHA, zero-cost, job-identity and terminal-failure checks.
- Added `docs/PHASE18_CHANGESET_069_GOLDEN_V4_SMOKE_COMPAT.md`.
- Files deleted: none.
- Production paths and all factual/identity/sentiment/semantic/quality/BF16/zero-cost gates remain unchanged.

## Current verified Golden Visual state
- Genuine GPU execution on the locked FLUX.2 Klein BF16 path is proven on a Colab Tesla T4 with sequential CPU offload.
- The first genuine proof was rejected for collage/panel composition.
- The later genuine single-scene proof was rejected for malformed football-pitch geometry and incorrect generated PUL7SAR text/branding.
- The active benchmark is now `golden-visual-general-season-opener-v4` / `pul7sar-golden-batch-v4`.
- A genuine v4 Candidate 1 PNG has not yet been executed, so no v4 visual-quality or publication claim is made.

## Production safety through Change Set 069
- `main`: untouched.
- `main.py`: untouched.
- Telegram production publishing: untouched.
- Legacy production image sourcing/rendering: untouched.
- No paid provider or paid image API selected.
- No production secret/API key added.
- No model weights or font files committed.
- No fake PNG or fake performance sample is generated.
- Missing semantic verification remains fail-closed.
- Golden approval remains additional to semantic-publication safety.
- Unsupported BF16 never triggers a silent precision downgrade.
- Exact PUL7SAR branding remains deterministic post-composition only.

## Architecture after Change Set 069
`Article -> Story Intelligence -> Fact / Identity / Sentiment / Neutrality -> Visual Family -> Unified Single-Scene Concept Grammar -> Regulation Sport-Geometry Lock -> Generated-Brand Exclusion -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Theme / Assets / Layout -> Generation Package -> Provider Constraint Reframing -> Zero-Cost Eligibility -> Portable SHA-256 Handoff -> Golden Batch v4 -> Colab CPU Regression Preflight -> Colab/Self-Hosted Golden Runner -> FLUX/BF16 Readiness -> Sequential-CPU-Offload GPU Execution -> Exact Handoff-SHA Result Binding -> CUDA Telemetry -> Native PNG -> Exact Platform Normalization -> Real Visual Proof -> Semantic Inspection -> SemanticPublicationGate -> Golden 8.5/9.0 Quality Gate -> Quality-First Selection -> Exact-Asset PUL7SAR PostComposition -> Typography -> FinalExportGate -> Platform Export`

## Immediate next work
1. Pull the latest `phase18/story-intelligence` into the active Colab T4 checkout.
2. Run only v4 Candidate 1 through `PYTHONPATH=. python tools/phase18_colab_runner.py --update --candidate 1` (or the durable one-command smoke path).
3. Do not spend GPU time on Candidates 2–4 until Candidate 1 is checked for all four basics: one continuous scene, regulation football-pitch geometry, zero generated platform branding/text, and premium editorial quality.
4. If Candidate 1 clears those blockers, run remaining deterministic seeds and apply semantic plus strict Golden quality review.
5. Keep verified-reference-person execution blocked until asset-path resolution and identity similarity are enforced end-to-end.
