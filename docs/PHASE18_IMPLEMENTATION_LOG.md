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

## Change Set 088 — Base-scene evidence bridge into HybridLayerQualityGate
- Added `engine/intelligence/base_scene_layer_evidence.py` to normalize explicit findings from real `BaseSceneEvidence.forbidden_visuals_detected` into the exact `LayerLeakageEvidence` fields consumed by `HybridLayerQualityGate`.
- Added `tests/test_phase18_base_scene_layer_evidence.py` covering a clean complete inspection, known text/brand/sport-geometry leakage, missing inspection-completeness proof, and unknown/unclassified visual findings.
- The adapter is deliberately fail-closed: a clean image cannot be inferred merely because no forbidden tuple was returned. `BaseSceneEvidence.provenance["forbidden_visual_inspection_complete"]` must explicitly be `true`, and unknown forbidden observations block automatic clearance instead of being discarded.
- This materially reduces the gap between real generated-image probe output and layer-ownership QA without pretending that computer-vision capabilities exist when they do not.
- No production code path, paid provider, fact/identity/sentiment/neutrality rule, semantic-publication gate, Golden thresholds, model, precision or `main` branch state was changed.

## Change Set 089 — Concrete semantic layer-leakage evidence
- Added `engine/intelligence/semantic_layer_evidence.py`, a fail-closed adapter from `SemanticVisualVerdict` to `LayerLeakageEvidence`. It requires each requested semantic layer check to be actually inspected above the configured confidence floor; missing or low-confidence checks block completion instead of being treated as clean.
- Expanded the local zero-cost Qwen2.5-VL inspection schema with explicit `exact_numbers_absent` and `generated_sport_geometry_absent` checks, while retaining separate scene, defect, framing and final geometry-alignment checks. This lets the vision stage distinguish model-owned editorial numbers/field markings from deterministic layers rather than inferring those violations from generic text or defect output.
- Updated `tools/phase18_qwen25_vl_inspect.py` to emit normalized layer-leakage evidence and completion blockers alongside the semantic verdict. Optional CLI requirements decide whether exact-number and sport-geometry checks are mandatory for the active plan.
- Added `tests/test_phase18_semantic_layer_evidence.py` for clean complete evidence, text/brand/number/geometry leakage mapping, missing required geometry inspection and low-confidence fail-closed behavior.
- Identity remains separate: this adapter does not claim identity similarity and does not convert missing identity verification into a clean identity result.
- No production path, paid provider, Fact Lock, sentiment/neutrality rule, semantic-publication rule, Golden threshold, FLUX model, BF16 lock or `main` state changed.

## Change Set 090 — Semantic base-scene execution gate before deterministic composition
- Added `engine/intelligence/base_scene_execution_gate.py`, combining semantic inspection completeness with `HybridLayerQualityGate` so a base scene cannot advance merely because an inspection attempt was logged.
- Added `tests/test_phase18_base_scene_execution_gate.py` covering clean completion, missing required geometry inspection, model-generated sport geometry, and generated PUL7SAR/platform branding.
- Updated `tools/phase18_colab_one_command.py`: Qwen readiness and base-scene semantic inspection are now mandatory before `FootballHybridComposer`; failed/incomplete semantic layer evidence or layer-ownership leakage blocks composition immediately.
- The one-command receipt now records normalized `base_scene_layer_gate` evidence and blockers.
- Hybrid-stage inspection no longer asks whether generated sport geometry is absent, because the sport geometry at that stage is intentionally deterministic; perspective/alignment verification remains mandatory.
- Detailed record: `docs/PHASE18_CHANGESET_090_BASE_SCENE_EXECUTION_GATE.md`.
- No production path, paid provider, Fact Lock, identity, sentiment/neutrality, semantic-publication rule, Golden threshold, FLUX model, BF16 lock or `main` state changed.

## Change Set 091 — Qwen / Colab runtime compatibility lock
- Reviewed the latest real Colab blocker: semantic readiness failed with `ImportError` around `PIL._typing._Ink` after the setup cell upgraded the live notebook from Pillow 11.x to Pillow 12.x; the same unconstrained install also moved Transformers onto an unverified 5.x major line.
- Updated `requirements-phase18-gpu.txt` to keep the verified semantic runtime on `transformers>=4.52.1,<5.0.0` and `Pillow>=11.3.0,<12.0.0`. FLUX/Diffusers, CUDA/BF16, seeds/canvases and `$0-local` remain unchanged.
- Hardened `Qwen25VLReadinessProbe`: Transformers major `>=5` and Pillow major `>=12` are explicit blockers, and Pillow `Image`, `ImageDraw`, `ImageFont` and `ImageText` must import coherently before the semantic runtime is considered ready.
- Updated `tools/phase18_colab_one_command.py` so a full execution proves Qwen/Pillow semantic-runtime readiness before entering the FLUX atmosphere/base-scene runner; the same readiness gate is rechecked immediately before semantic inference. `--prepare-only` may defer this check because it performs no GPU generation, while a full run cannot use `--semantic-inspection none` as a bypass.
- Expanded `tests/test_phase18_qwen_runtime_contract.py` to regression-lock both dependency ranges and Pillow runtime coherence, and added `tests/test_phase18_colab_semantic_preflight_order.py` to enforce pre-GPU semantic readiness ordering and the no-bypass/recheck contract.
- Detailed record: `docs/PHASE18_CHANGESET_091_QWEN_COLAB_RUNTIME_COMPAT.md`.
- No semantic bypass was introduced. A live notebook already contaminated by an in-place major Pillow upgrade must fail closed and may require a runtime restart rather than disabling Qwen.

## Current verified Golden Visual state
- Genuine FLUX.2 Klein BF16 GPU execution is proven on Colab Tesla T4 with sequential CPU offload.
- Proof 1: rejected for collage/panel composition.
- Proof 2: single scene, but rejected for malformed football geometry and incorrect generated PUL7SAR text/branding.
- Active historical benchmark is v4; the current branch also contains the newer v5 hybrid base-scene path where diffusion does not own final pitch geometry or branding.
- A genuine Candidate 1 PNG under the latest hybrid/evidence/runtime hardening has not yet been executed. No new visual-quality or publication claim is made.

## Production safety through Change Set 091
- `main`: untouched.
- `main.py`: untouched.
- Telegram production publishing: untouched.
- Legacy production image sourcing/rendering: untouched.
- No paid provider or paid image API selected.
- No production secret/API key added.
- No model weights or font files committed.
- No fake PNG or fake performance sample generated.
- Fact, identity, sentiment and neutrality gates remain fail-closed.
- Missing semantic verification remains fail-closed and blocks hybrid composition before the deterministic renderer.
- Golden approval remains additional to semantic-publication safety.
- Unsupported BF16 never triggers a silent precision downgrade.
- Exact PUL7SAR branding remains deterministic post-composition only and checksum/runtime-integrity protected.
- Unverified major-version drift in the Qwen/Pillow runtime is now rejected before semantic clearance can be claimed.
- Full Colab execution now proves semantic-runtime compatibility before any FLUX GPU generation, preventing the observed dependency failure from wasting another Golden generation cycle.

## Architecture after Change Set 091
`Article -> Fact Lock -> Event Fact Schema -> Fact-Locked Editorial Slots -> Visual-Aware Angle Selection -> Editorial Copy/Headline + Visual Anchor -> Scene Complexity Policy -> Sport Rule -> Geometry Capability -> Hybrid Layer Ownership -> Generation Authorization -> Unified Single-Scene / Generated-Brand Exclusion -> Generation Package -> Zero-Cost Eligibility -> SHA-256 Handoff -> Golden Batch -> CPU Contract Verification -> Colab CPU Preflight -> Qwen/Pillow Runtime Compatibility Preflight -> CUDA/BF16 FLUX Atmosphere/Base Scene -> Native PNG -> Qwen Readiness Recheck -> Qwen Semantic Inspection -> SemanticLayerEvidenceAdapter -> BaseSceneExecutionGate -> HybridLayerQualityGate -> Deterministic Football Renderer / Deterministic Data / Typography + Verified Assets -> Final Hybrid Visual QA -> SemanticPublicationGate -> Golden 8.5/9.0 Quality Gate -> Exact Logo Integrity Gate -> FinalExportGate -> Platform Export`

## Immediate next work
1. Let CPU CI validate Change Set 091, especially the compatibility bounds, strengthened readiness probe and pre-GPU ordering regression test.
2. On a fresh compatible Colab CUDA/BF16 runtime, install the locked Phase 18 GPU requirements and require the pre-GPU Qwen runtime gate to pass; never bypass the semantic gate to obtain a PNG.
3. Run only Golden Hybrid v5 Candidate 1. Composition must not begin unless base-scene semantic layer evidence is complete and clean.
4. Inspect deterministic pitch integration and final hybrid semantic alignment from that one genuine PNG before spending GPU time on seeds 2–4.
5. Resolve the approved PUL7SAR brand geometry/asset bytes and checksum-lock them before any final composition can pass.
6. Keep real-person execution blocked until verified reference assets and identity similarity are enforced end-to-end.
