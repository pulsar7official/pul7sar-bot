# PUL7SAR Phase 18 — Implementation Log

This document is the authoritative implementation journal for Phase 18 on the `phase18/story-intelligence` branch. Phase 18 remains isolated from `main` and production publishing paths unless a future explicit merge is approved.

## Change Sets 001–030 — Intelligence and generation foundation
Foundation through local image inspection: Fact Lock, StoryAnalyzer, identity verification, classification, neutrality, Visual Family routing, Concept Director, sentiment, Generation Authorization, platform profiles, scene specification, exact assets, deterministic layout, dry-run manifest, theme/brand semantics, provider capability/selection/execution, post-composition, typography/final export, base-scene acceptance, zero-cost policy, provider adapters, candidate selection, generation-session orchestration, zero-cost local model profile, prompt-constraint reframing, runtime compatibility, local backend readiness/provenance, readiness report, execution boundary, optional Diffusers/ComfyUI shells, evidence extraction, and fail-closed local image inspectors. Production paths remain isolated.

## Change Sets 031–038 — Readiness, semantic/identity verification and exact-overlay separation
- Unified local readiness separates generation readiness from publication readiness.
- Zero-cost semantic vision verification requires subject/framing, defect, forbidden-visual, protected-region and identity checks where applicable.
- `SemanticPublicationGate` cross-checks locked identity references against verification evidence.
- Required-person scenes fail closed on missing/mismatched identity evidence.
- Exact logos, crests, social marks and typography are deterministic post-composition assets and must not be hallucinated by the image model.
- CI references include `32588437912` and `32592258604`: SUCCESS.

## Change Sets 039–043 — Real FLUX.2 Klein local path, exact canvas and Golden batch
- Concrete Diffusers execution for `black-forest-labs/FLUX.2-klein-4B`, Apache-2.0, `$0-local`, deterministic seed, guidance 1.0 and four inference steps.
- Instagram native canvas `1088x1360`, deterministically normalized to `1080x1350`.
- Handoff schema `pul7sar-local-generation-v2` protects provider/model/prompt/constraints/canvas/seed/request/references/metadata by canonical SHA-256.
- Golden batch uses seeds `7007001`–`7007004`; only seed varies.
- CI Run `32594690472`: SUCCESS.

## Change Sets 044–050 — Sequential execution, Golden quality and BF16 lock
- Candidates execute sequentially through the same locked request path.
- Golden Visual quality remains separate from semantic safety; hard blockers override aesthetic score.
- Weighted Golden minimum `8.5/10`, critical core floor `8.0/10`, `9.0+` elite.
- Durable executor result JSON replaces stdout parsing.
- Native BF16 is required; no silent FP16 downgrade.
- Detailed record: `docs/PHASE18_CHANGESET_050_GPU_DTYPE.md`.

## Change Sets 051–055 — Durable GPU jobs, recovery and telemetry
- Provider-neutral generation jobs, bounded attempts, leases, worker capability matching and result identity checks.
- `FilesystemGenerationJobStore`, locked FLUX worker adapter, enqueue command and GPU worker command.
- Handoff-integrity failure is terminal; expired leases recover without resetting attempt history.
- Worker heartbeat, measured execution timing and CUDA high-water memory telemetry are persisted.
- Throughput remains `unproven` until genuine successful GPU generation exists; raw generation capacity is never publication capacity.
- Detailed records: `docs/PHASE18_CHANGESET_051_052_GPU_AUTOMATION.md`, `docs/PHASE18_CHANGESET_054_WORKER_TELEMETRY.md`, `docs/PHASE18_CHANGESET_055_CUDA_MEMORY_TELEMETRY.md`.

## Change Sets 056–062 — One-command first PNG, host/cache qualification and replayable evidence
- `tools/phase18_first_png.py` composes Golden verification, GPU host qualification, model-cache preflight, CUDA/FLUX/BF16 readiness, durable enqueue, one worker cycle and real-PNG validation.
- Self-hosted GPU workflow remains manual and zero-cost-policy safe.
- Exact `black-forest-labs/FLUX.2-klein-4B` cache qualification is fail-closed with conservative disk checks.
- GPU host must prove local CUDA, CUDA-enabled PyTorch, required VRAM, native BF16 and observable compute capability.
- Genuine PNG/evidence receipts are SHA-256 manifested and independently replay-verified before artifact upload.
- Generation success remains `publication_ready=false` pending semantic and Golden review.
- CI Run `32611296349`: SUCCESS for the one-command path; later evidence verification also passed CPU CI.

## Change Set 063 — T4 low-VRAM sequential offload
- First Colab/Tesla T4 attempt reached FLUX.2 attention but failed with CUDA OOM on the locked canvas.
- `flux2_klein_diffusers.py` prefers sequential CPU offload and falls back to model CPU offload only when required.
- Model, BF16, prompt, seed, canvas, guidance, four-step inference and `$0-local` remain unchanged.

## Change Set 064 — First genuine T4 PNG proof
- Candidate 1 completed on Colab Tesla T4 using the locked FLUX.2 Klein BF16 path.
- Seed `7007001`, native `1088x1360`, target `1080x1350`, `$0-local`; observed execution about 252.7 seconds.
- This proved genuine inference/persistence only. Human review rejected the visual because it became a four-panel football collage.

## Change Sets 065–068 — Unified scene, Colab automation and v2 regression repair
- Golden composition grammar moved to one continuous full-bleed scene with explicit collage/montage/split-screen/grid prohibitions.
- `phase18_colab_runner.py` is branch-locked, rebuilds/verifies Golden handoffs, rechecks GPU readiness, binds result identity/SHA and never promotes generation to publication.
- Colab CPU preflight runs before GPU use.
- FLUX executor persists exact handoff SHA; stale result reuse is rejected.
- Golden v2 smoke assumptions were repaired; CI Run `32629634107`: SUCCESS.

## Intervening visual corrections — Golden v3/v4
A later genuine single-scene proof removed the collage but human inspection found two hard failures: malformed association-football pitch proportions/markings and an AI-generated PUL7SAR treatment that was not the approved logo.

The benchmark advanced cumulatively:
- v3: `sport_geometry=association_football_regulation_pitch`; `broken_sport_surface_geometry` is a hard Golden blocker.
- v4: `generated_branding_allowed=false`; `brand_composition_policy=exact_assets_only_after_generation`; `generated_platform_brand_or_wordmark` is a hard blocker.

Detailed brand-exclusion record: `docs/PHASE18_CHANGESET_068_EXACT_BRANDING_EXCLUSION.md`.

## Change Set 069 — Golden v4 durable-smoke compatibility
- `golden_smoke.py` supports v1–v4 but applies cumulative fail-closed locks for the current benchmark: unified scene, regulation football geometry, no generated branding and exact-assets-only post-generation branding.
- Candidate 1 cannot enter the durable queue until matching SHA-protected prompt markers replay successfully.
- Regression tests reject grammar, geometry, generated-brand permission and brand-policy drift.
- Detailed record: `docs/PHASE18_CHANGESET_069_GOLDEN_V4_SMOKE_COMPAT.md`.

## Change Set 070 — Exact PUL7SAR logo integrity gate
- Deterministic post-composition requires the PUL7SAR logo asset to declare a 64-hex SHA-256 plus a matching runtime `AssetIntegrityRecord`.
- Missing checksum, missing runtime evidence or mismatch fails closed; exactly one untinted PUL7SAR logo remains required.
- The approved production logo bytes are still unresolved, so final composition intentionally remains blocked until the correct asset is selected and checksum-locked.
- Detailed record: `docs/PHASE18_CHANGESET_070_EXACT_LOGO_INTEGRITY_GATE.md`.

## Change Sets 071–076 — Story-to-Visual editorial architecture
Canonical numbering reconciles an earlier provisional 069–074 label collision; the historical filename is retained but its contents state the canonical sequence.

- **071 Story-to-Visual Editorial Engine:** event taxonomy and production modes; low-confidence stories fall back to verified assets rather than more imaginative generation.
- **072 Sport-aware production rules:** sport physics/surface/equipment risks are separated from event semantics.
- **073 Visual-compatible editorial language:** headline/copy grammar is planned with the visual anchor and uses supplied verified fact slots only.
- **074 Visual-aware angle selection:** candidates are ranked by editorial value, fact/identity confidence and visual reliability; unsafe angles fail closed.
- **075 Unified editorial planning:** selected angle -> concise headline -> sport-aware production mode -> geometry/layer contracts -> generation authorization without inferring missing facts from prose.
- **076 Hybrid layer ownership:** atmosphere may be generative, while geometry, exact data, typography and PUL7SAR branding belong to deterministic/verified layers; identity-sensitive subjects require verified assets or separately verified depictions.

Detailed record: `docs/PHASE18_CHANGESET_069_074_STORY_TO_VISUAL_EDITORIAL_ENGINE.md` (historical filename retained; canonical numbering 071–076 inside).

## Change Sets 077–080 — Fact integrity, football geometry and final hybrid QA
- **077 Event-specific Fact Schemas:** `sports_fact_schema.py` defines required/optional/exact-render/identity slots for the active sports-event taxonomy; exact scores, dates, formations, fees, standings and record values are deterministic facts.
- **078 Fact Lock -> Editorial Slot Integrity:** `fact_locked_editorial_adapter.py` requires supplied visual/copy slots to be backed by `LockedClaim(kind=FACT)` for the same slot; low-confidence or inferred/forbidden claims cannot satisfy required facts.
- **079 Deterministic Football Pitch Geometry:** regulation world-space football geometry and projective perspective mapping replace diffusion-owned pitch geometry.
- **080 Layer-aware Hybrid Visual QA:** `hybrid_visual_quality_gate.py` blocks generated text/brand/fake logos, severe defects/collage, and missing deterministic geometry/exact branding/typography/verified identity required by the final layer plan.

Detailed record: `docs/PHASE18_CHANGESET_075_078_FACT_GEOMETRY_QA.md` (historical filename retained; canonical numbering 077–080 inside).

## Change Sets 081–084 — Complexity minimization, cross-sport coverage and deterministic renderer capability
- **081 Scene Complexity Minimization:** `scene_complexity_policy.py` chooses the minimum physical scene dependency needed for each event; many stories require no surface, results/previews use partial deterministic context, tactics require full deterministic surface.
- **082 Expanded Cross-Sport Rules:** explicit profiles cover more than thirty sport families plus Arabic aliases and a conservative unknown fallback.
- **083 Deterministic Football Geometry Renderer:** `football_pitch_renderer.py` uses the projective geometry plan to render a transparent Pillow pitch overlay and composite it over a base image, rather than asking FLUX to invent markings.
- **084 Geometry Capability Fail-Closed Policy:** `geometry_capabilities.py` separates exact-geometry policy from implementation readiness. Football is currently declared ready as `football_pitch_projective_v1`; unsupported exact-geometry sports simplify or block instead of falling back to generative geometry.

Detailed record: `docs/PHASE18_CHANGESET_079_082_COMPLEXITY_GEOMETRY_CAPABILITY.md` (historical filename retained; canonical numbering 081–084 inside).

## Change Set 085 — Base-scene layer leakage QA
- Added `visual_layer_qa.py` and `tests/test_phase18_visual_layer_qa.py`.
- This pre-composition gate is intentionally narrower than final `HybridVisualQualityGate`: it blocks generated text, PUL7SAR/platform branding, exact numbers, entity marks, unverified identity and generated sport geometry whenever those responsibilities belong to deterministic code or verified assets.
- It consumes inspection evidence and does not replace computer-vision extraction, `SemanticPublicationGate` or Golden visual-quality review.

## Change Set 086 — Complete football marking primitives and GPU-preflight regression protection
- `football_pitch_geometry.py` now includes centre mark, both penalty marks, both 9.15m penalty arcs and all four 1m corner arcs in addition to boundary/halfway lines, centre circle, penalty areas and goal areas.
- Geometry integrity receipt proves marking counts and symmetry.
- Geometry/projection regression tests now cover arc orientation, projected arcs and projected centre/penalty point marks.
- Geometry/projection contracts are exported through `engine/intelligence/__init__.py`.
- Colab CPU preflight now includes layer QA plus football geometry/projection regression modules, so regressions block GPU expenditure.

## Change Set 087 — Golden v4 CPU verification alignment
- Branch review found `.github/workflows/phase18-intelligence.yml` still using stale Golden-v2 request/artifact names while the active builder, smoke coordinator and Colab runner were locked to v4.
- CPU CI now builds `golden-general-season-opener-v4-001`, uploads v4-named artifacts and explicitly asserts `pul7sar-golden-batch-v4`, `single_continuous_scene`, `association_football_regulation_pitch`, `generated_branding_allowed=false`, and `exact_assets_only_after_generation` before artifact upload.
- Added `tests/test_phase18_intelligence_workflow.py` to prevent stale-v2 regression and preserve Phase-18-only, CPU-safe, no-secret workflow isolation.
- Detailed record: `docs/PHASE18_CHANGESET_085_087_LAYER_GEOMETRY_CI_HARDENING.md`; historical `docs/PHASE18_CHANGESET_081_GOLDEN_V4_CI_ALIGNMENT.md` now declares canonical Change Set 087.

## Documentation reconciliation performed with Change Set 087
- Historical filenames were retained where renaming would create unnecessary churn, but their contents now state canonical numbering.
- Removed duplicate provisional docs `docs/PHASE18_CHANGESET_075_077_FACT_SCHEMA_LAYER_QA.md` and `docs/PHASE18_CHANGESET_077_079_FACT_SCHEMA_LAYER_QA.md` after consolidating their information into canonical records.

## Current verified Golden Visual state
- Genuine FLUX.2 Klein BF16 GPU execution is proven on Colab Tesla T4 with sequential CPU offload.
- Proof 1: rejected for collage/panel composition.
- Proof 2: single scene, but rejected for malformed football geometry and incorrect generated PUL7SAR text/branding.
- Active benchmark: `golden-visual-general-season-opener-v4` / `pul7sar-golden-batch-v4`.
- A genuine v4 Candidate 1 PNG has not yet been executed after the latest editorial/layer/geometry hardening. No v4 visual-quality or publication claim is made.

## Production safety through Change Set 087
- `main`: untouched.
- `main.py`: untouched.
- Telegram production publishing: untouched.
- Legacy production image sourcing/rendering: untouched.
- No paid provider or paid image API selected.
- No production secret/API key added.
- No model weights or font files committed.
- No fake PNG or fake performance sample generated.
- Fact, identity, sentiment and neutrality gates remain fail-closed.
- Missing semantic verification remains fail-closed.
- Golden approval remains additional to semantic-publication safety.
- Unsupported BF16 never triggers a silent precision downgrade.
- Exact PUL7SAR branding remains deterministic post-composition only and checksum/runtime-integrity protected.

## Architecture after Change Set 087
`Article -> Fact Lock -> Event Fact Schema -> Fact-Locked Editorial Slots -> Visual-Aware Angle Selection -> Editorial Copy/Headline + Visual Anchor -> Scene Complexity Policy -> Sport Rule -> Geometry Capability -> Hybrid Layer Ownership -> Generation Authorization -> Unified Single-Scene / Generated-Brand Exclusion -> Generation Package -> Zero-Cost Eligibility -> SHA-256 Handoff -> Golden Batch v4 -> Golden-v4 CPU Contract Verification -> Colab CPU Preflight -> CUDA/BF16 FLUX Atmosphere/Base Scene -> Native PNG -> Visual Evidence Extraction -> Base-Scene Layer Leakage QA -> Deterministic Football Renderer / Deterministic Data / Typography + Verified Assets -> Final Hybrid Visual QA -> Semantic Inspection -> SemanticPublicationGate -> Golden 8.5/9.0 Quality Gate -> Exact Logo Integrity Gate -> FinalExportGate -> Platform Export`

## Immediate next work
1. Wire real generated-image probes/evidence into the new base-scene `HybridLayerQualityGate`; until then text/brand/geometry leakage cannot be auto-cleared.
2. Connect `PillowFootballPitchRenderer` into the normal deterministic post-composition path and prove the overlay/canvas/alpha contract end-to-end rather than merely having a standalone renderer.
3. Resolve and checksum-lock the approved PUL7SAR logo asset before any final composition can pass.
4. Keep real-person execution blocked until verified reference assets and identity similarity are enforced end-to-end.
5. Only after the CPU-safe integration above is green, run v4 Candidate 1 on a compatible CUDA/BF16 host. Do not spend GPU time on Candidates 2–4 until Candidate 1 is checked for one continuous scene, zero generated text/branding, no model-owned football geometry, correct deterministic overlay integration, semantic safety and premium editorial quality.
6. If Candidate 1 clears hard blockers, run remaining deterministic seeds and apply semantic plus strict Golden quality review.
