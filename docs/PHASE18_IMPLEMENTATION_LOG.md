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
- `flux2_klein_diffusers.py` now prefers sequential CPU offload and falls back to model CPU offload only when required.
- Model, BF16, prompt, seed, canvas, guidance, four-step inference and `$0-local` remain unchanged.

## Change Set 064 — First genuine T4 PNG proof
- Candidate 1 completed on Colab Tesla T4 using the locked FLUX.2 Klein BF16 path.
- Seed `7007001`, native `1088x1360`, target `1080x1350`, `$0-local`; observed execution about 252.7 seconds.
- This proved genuine inference/persistence only. Human review rejected the visual because it became a four-panel football collage.

## Change Sets 065–068 — Unified scene, Colab automation and v2 regression repair
- Golden composition grammar moved to one continuous full-bleed scene with explicit collage/montage/split-screen/grid prohibitions.
- Semi-automatic `phase18_colab_runner.py` is branch-locked, rebuilds/verifies Golden handoffs, rechecks GPU readiness, binds result identity/SHA and never promotes generation to publication.
- Colab CPU preflight runs before GPU use.
- FLUX executor persists exact handoff SHA; stale result reuse is rejected.
- Golden v2 smoke assumptions were repaired; CI Run `32629634107`: SUCCESS.

## Intervening visual corrections — Golden v3/v4
A later genuine single-scene proof removed the collage but human inspection found two hard failures: malformed association-football pitch proportions/markings and an AI-generated PUL7SAR treatment that was not the approved logo.

The benchmark therefore advanced cumulatively:
- v3: `sport_geometry=association_football_regulation_pitch`; one coherent 105x68-style pitch, halfway line, centre circle/mark, penalty/goal areas, goal/touch lines and perspective-consistent markings. `broken_sport_surface_geometry` is a hard Golden blocker.
- v4: `generated_branding_allowed=false`; `brand_composition_policy=exact_assets_only_after_generation`. Generated PUL7SAR/PULSAR lettering, pseudo-wordmarks, pulse/7 substitutes, readable sponsor text and pseudo-text are forbidden. `generated_platform_brand_or_wordmark` is a hard blocker.

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
Canonical numbering reconciles an earlier provisional 069–074 label collision; the historical filename is retained but its contents now state the canonical sequence.

- **071 Story-to-Visual Editorial Engine:** event taxonomy and production modes (`generative_scene`, `hybrid`, `deterministic_composition`, `verified_asset_editorial`); low-confidence stories fall back to verified assets rather than more imaginative generation.
- **072 Sport-aware production rules:** sport physics/surface/equipment risks are separated from event semantics across football, basketball, tennis, golf, combat sports, athletics, motorsport, swimming, cycling, volleyball, handball, ice hockey, winter sports and conservative unknown fallback.
- **073 Visual-compatible editorial language:** headline/copy grammar is planned with the visual anchor and uses supplied verified fact slots only.
- **074 Visual-aware angle selection:** candidate angles are ranked by editorial value, fact/identity confidence and visual reliability; low-confidence identity, invented-scene dependency and other hard blockers fail closed.
- **075 Unified editorial planning:** orchestrator, planning service and event resolver connect selected angle -> concise headline -> sport-aware production mode -> geometry/layer contracts -> generation authorization without inferring missing facts from prose.
- **076 Hybrid layer ownership:** atmosphere may be generative, while geometry, exact data, typography and PUL7SAR branding belong to deterministic/verified layers; identity-sensitive subjects belong to verified assets or separately verified depictions.

Detailed record: `docs/PHASE18_CHANGESET_069_074_STORY_TO_VISUAL_EDITORIAL_ENGINE.md` (historical filename retained; canonical numbering 071–076 inside).

## Change Set 077 — Event-specific sports fact schemas
- `engine/intelligence/sports_fact_schema.py` defines required/optional/exact-render/identity slots for the active editorial-event taxonomy.
- Results, live moments, previews, transfers, contracts, injuries, comebacks, suspensions, retirement, appointments, dismissals, statements, records, awards, trophies, draws, tables, tactics, officiating, controversies, financial/organization news, schedules, qualification, elimination and general stories validate before copy/visual planning.
- Scores, minutes, dates, standings, formations, fees, record values and similar exact facts are routed to deterministic rendering rather than generative invention.

## Change Set 078 — Fact-Lock-to-editorial slot binding
- `engine/intelligence/fact_locked_editorial_adapter.py` requires every supplied editorial/visual slot to be backed by a `LockedClaim(kind=FACT)` declaring the same slot.
- `SAFE_INFERENCE` and `FORBIDDEN` claims cannot satisfy required slots.
- Missing required slots, unbacked values and FACT claims below the 0.80 production-confidence floor fail closed.
- Fact-schema and adapter contracts are exported through `engine/intelligence/__init__.py`.

## Change Set 079 — Hybrid layer leakage QA
- Adds `engine/intelligence/visual_layer_qa.py` and `tests/test_phase18_visual_layer_qa.py`.
- `HybridLayerQualityGate` blocks generated text, platform branding, exact numbers, entity marks, unverified identity and sport geometry when those pixels belong to deterministic/verified layers.
- This gate consumes inspection evidence; it does not replace computer-vision extraction, `SemanticPublicationGate` or Golden visual-quality review.
- Colab CPU preflight now includes the layer-QA regression module before spending GPU time.
- Detailed record: `docs/PHASE18_CHANGESET_077_079_FACT_SCHEMA_LAYER_QA.md`.

## Change Set 080 — Complete deterministic football geometry contract
- `engine/intelligence/football_pitch_geometry.py` now owns a stable 105m x 68m reference pitch plus exact halfway/boundary lines, penalty and goal areas, centre circle, centre/penalty marks, both penalty arcs and all four 1m corner arcs.
- Integrity receipt now proves counts for centre mark, penalty marks, penalty arcs and corner arcs in addition to the original line/area symmetry checks.
- Existing `engine/intelligence/football_pitch_projection.py` was reviewed as the perspective layer and already projects world-space primitives through a four-corner homography; the current implementation consumes lines, rectangles, circles, arcs and point marks via `project_all_markings()` while retaining the older polyline-only API.
- `tests/test_phase18_football_pitch_geometry.py` verifies the complete marking set and penalty-arc orientation.
- `tests/test_phase18_football_pitch_projection.py` verifies projected penalty/corner arcs and centre/penalty point marks as well as the original homography/circle checks.
- Football geometry/projection contracts are exported through `engine/intelligence/__init__.py`.
- Colab CPU preflight includes both deterministic football geometry and projection test modules, so a geometry regression blocks GPU expenditure.
- Files deleted during numbering cleanup: superseded `docs/PHASE18_CHANGESET_075_077_FACT_SCHEMA_LAYER_QA.md`; replaced by canonical `docs/PHASE18_CHANGESET_077_079_FACT_SCHEMA_LAYER_QA.md`.

## Change Set 081 — Golden v4 CPU verification alignment
- Branch review found `.github/workflows/phase18-intelligence.yml` still building with the stale `golden-general-season-opener-v2-001` request/artifact naming while active builders, durable smoke and Colab runner are locked to Golden v4.
- CPU CI now builds `golden-general-season-opener-v4-001`, uploads v4-named handoff/candidate artifacts, and explicitly asserts `pul7sar-golden-batch-v4`, `single_continuous_scene`, `association_football_regulation_pitch`, `generated_branding_allowed=false`, and `exact_assets_only_after_generation` before artifact upload.
- Added `tests/test_phase18_intelligence_workflow.py` to reject stale v2 request/artifact names and preserve Phase-18-only, CPU-safe, no-secret workflow isolation.
- Detailed record: `docs/PHASE18_CHANGESET_081_GOLDEN_V4_CI_ALIGNMENT.md`.
- Files deleted: none in Change Set 081.

## Current verified Golden Visual state
- Genuine FLUX.2 Klein BF16 GPU execution is proven on Colab Tesla T4 with sequential CPU offload.
- Proof 1: rejected for collage/panel composition.
- Proof 2: single scene, but rejected for malformed football geometry and incorrect generated PUL7SAR text/branding.
- Active benchmark: `golden-visual-general-season-opener-v4` / `pul7sar-golden-batch-v4`.
- A genuine v4 Candidate 1 PNG has not yet been executed after the latest hybrid/editorial/geometry hardening. No v4 visual-quality or publication claim is made.

## Production safety through Change Set 081
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

## Architecture after Change Set 081
`Article -> Fact Lock -> Event Fact Schema -> Fact-Locked Editorial Slots -> Visual-Aware Angle Selection -> Editorial Copy/Headline + Visual Anchor -> Sport Rule -> Hybrid Layer Ownership -> Generation Authorization -> Unified Single-Scene / Generated-Brand Exclusion -> Generation Package -> Zero-Cost Eligibility -> SHA-256 Handoff -> Golden Batch v4 -> Golden-v4 CPU Contract Verification -> Colab CPU Preflight (including layer QA + football geometry/projection) -> CUDA/BF16 FLUX Execution -> Native PNG -> Visual Evidence Extraction -> Hybrid Layer Leakage QA -> Semantic Inspection -> SemanticPublicationGate -> Golden 8.5/9.0 Quality Gate -> Deterministic Geometry/Data/Typography + Verified Assets -> Exact Logo Integrity Gate -> FinalExportGate -> Platform Export`

## Immediate next work
1. Wire real generated-image evidence/probes into `HybridLayerQualityGate`; until then layer leakage cannot be auto-cleared.
2. Build a deterministic raster/vector composer for the projected football markings so the 105m x 68m contract becomes actual pixels over the generated atmosphere rather than only a geometry plan.
3. Resolve and checksum-lock the approved PUL7SAR logo asset before any final composition can pass.
4. Keep real-person execution blocked until verified reference assets and identity similarity are enforced end-to-end.
5. Only after the above CPU-safe integration is green, run v4 Candidate 1 on a compatible CUDA/BF16 host. Do not spend GPU time on Candidates 2–4 until Candidate 1 is checked for: one continuous scene, no generated text/branding, no model-owned football geometry, correct deterministic overlay integration, and premium editorial quality.
6. If Candidate 1 clears hard blockers, run the remaining deterministic seeds and apply semantic plus strict Golden quality review.
