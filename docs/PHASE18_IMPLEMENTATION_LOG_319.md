# Phase 18 Implementation Log 319 — Deterministic Composition Preparation Checkpoint

## Baseline reviewed first

Target repository: `pulsar7official/pul7sar-bot`

Target branch only: `phase18/story-intelligence`

Baseline branch HEAD at the start of CS319:

`cd9e48e84fe39b0713a820806a6b9b9613bd9829`

Observed `main` during the branch-isolation check:

`89b69e0972047af615162518dcc32dc1a16cd2dd`

No write, merge, rebase, reset, force-update, or other mutation was performed on `main`.

Before implementation, the prior CS318 branch state was also verified through GitHub Actions: `Phase 18 Story Intelligence Verification` run `33632514192`, run number `4633`, completed successfully on `cd9e48e84fe39b0713a820806a6b9b9613bd9829`.

## Investigation finding

CS318 safely reaches CS268 when no human identity review is required, or stops at CS266 when manual identity review is required. The next production contracts already existed:

1. CS269 consumes an approved CS268 receipt plus an explicit repository-bound composition input manifest.
2. CS269 binds layer ownership exactly. Required non-generative layers cannot be silently omitted. Verified assets must be repository byte bindings. Deterministic layers must specify an exact renderer contract and payload SHA-256.
3. CS270 consumes a READY CS269 receipt plus an explicit deterministic payload manifest and reopens the exact payload files from the repository, requiring the payload bytes and renderer contracts to match CS269.
4. Neither CS269 nor CS270 renders pixels or grants semantic, human-review, Golden, or publication authority.

The remaining operational gap was that these two contracts required separate manual command coordination after CS268, and there was no single fail-closed checkpoint identifying whether preparation was blocked at the composition-input manifest layer or at deterministic payload materialization.

Automatically inventing the manifests would have been unsafe. The CS268 hybrid layer plan intentionally assigns exact editorial typography, verified marks/assets, sport geometry, score/data, and PUL7SAR branding to non-generative owners. Therefore CS319 does not fabricate those inputs.

## Change implemented

Added:

`tools/phase18_prepare_deterministic_composition_checkpoint.py`

The new tool:

- independently verifies the exact CS268 receipt and requires `generated_layer_qa_approved=true`;
- reasserts that all downstream authority fields remain closed;
- requires the composition manifest to already exist inside the repository;
- optionally accepts an explicit deterministic payload manifest, also required to exist inside the repository;
- builds and independently replays CS269;
- only when CS269 is READY and a payload manifest was supplied, builds and independently replays CS270;
- checks that story SHA and exact candidate binding remain identical through CS268 → CS269 → CS270;
- writes a non-authoritative `composition_preparation_checkpoint.json` inside the requested repository output directory;
- never executes composition, model inference, rendering, image decoding/re-encoding, network access, or publication.

The checkpoint reports one of four states:

`COMPOSITION_INPUT_MANIFEST_BLOCKED`

`DETERMINISTIC_PAYLOAD_MANIFEST_REQUIRED`

`DETERMINISTIC_PAYLOAD_BINDING_BLOCKED`

`COMPOSITION_EXECUTION_PREFLIGHT_READY`

Even the final state is only a preparation result. It does not mean `composition_executed=true`.

## Authority boundary preserved

The CS319 checkpoint is explicitly `authoritative=false` and always keeps:

`composition_executed=false`

`composed_visual_approved=false`

`semantic_approved=false`

`human_visual_review_approved=false`

`golden_quality_approved=false`

`genuine_golden_png_created=false`

`publication_ready=false`

No factual/freshness, Entity/Identity, sentiment neutrality, loser-respect, `$0-local`, semantic-publication, Generated-Layer QA, Composition QA, Golden Quality, Human Visual Review, Exact Brand/Typography, Final Semantic Approval, Genuine Golden materialization, or final publication-readiness rule was weakened.

## Tests added

Added:

`tests/test_phase18_deterministic_composition_preparation_checkpoint.py`

Regression coverage locks the following properties:

- CS319 reuses the existing CS268/CS269/CS270 verification contracts rather than bypassing them.
- It requires explicit composition and payload manifests.
- It never invokes QwenImagePipeline or rendering/image APIs.
- All downstream authority fields stay false.
- Repository containment is mandatory for output/manifests.
- The four explicit preparation/blocker states remain present.
- Story SHA and exact candidate binding drift are rejected between CS268, CS269, and CS270.

## Files changed in CS319

Added:

- `tools/phase18_prepare_deterministic_composition_checkpoint.py`
- `tests/test_phase18_deterministic_composition_preparation_checkpoint.py`
- `docs/PHASE18_CHANGESET_319_DETERMINISTIC_COMPOSITION_PREPARATION_CHECKPOINT.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_319.md`

Modified existing files: none.

Deleted files: none.

## Commits

Production checkpoint:

`9ff4317e758b90fbb2ecea1672b0a884caef7071`

Regression tests:

`a072c129cc2dc611548b733975ee02f1efab7496`

CS319 contract documentation:

`891b5d1d35c0d628c0d432f4d059705cf30cf853`

This implementation-log commit is the fourth CS319 commit; the final branch HEAD is recorded after the write completes and GitHub verification starts.

## What remains

CS319 intentionally does not create composition inputs. A genuine generated candidate that reaches CS268 must still be accompanied by the exact repository-owned composition manifest required by its hybrid layer plan. Depending on the story, this may include verified identity/entity assets, deterministic editorial typography, deterministic sport geometry, exact score/data payloads, and the approved PUL7SAR brand asset. Deterministic layers must additionally be materialized as exact payload files whose SHA-256 values match CS269 before CS270 can become READY.

Only after CS270 is READY may the existing deterministic composition execution stage be considered. The resulting composed PNG must still traverse Composition/Post-composition QA, Golden Quality, Human Visual Review, Exact Brand/Typography, Final Composed Approval, Final Semantic Approval, the lineage-bound SemanticPublicationGate, CS285 Genuine Golden exact-byte materialization, and CS286 publication readiness.

## Genuine PNG status and hardware blocker

No image was fabricated in CS319. The current automation/runtime does not provide a compatible NVIDIA CUDA execution environment for the canonical Qwen-Image inference path. A real first candidate still requires a zero-cost host with CUDA-enabled PyTorch, a usable NVIDIA CUDA device, native BF16, the approved compatible Qwen-Image runtime, the exact already-local pinned Qwen snapshot, the pinned local semantic-verifier assets, and sufficient RAM/VRAM for a real model load and inference.

CS319 reduces the remaining non-GPU gap by converting the CS268 → CS269 → CS270 handoff into one deterministic preparation checkpoint while refusing to invent any layer input that belongs to factual/editorial/brand/identity/geometry ownership.
