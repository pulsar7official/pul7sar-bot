# Phase 18 Implementation Log 273 — Composed Candidate Hybrid-Surface Semantic QA

## Branch boundary

- Repository: `pulsar7official/pul7sar-bot`
- Writable branch: `phase18/story-intelligence` only
- Starting Phase 18 HEAD: `0c87624653ca671bd17b38b3e6ccab1f7de673cf`
- Starting `main` SHA observed read-only: `6482f8d98fe2f0a0890679a5cc8108b5d6e48378`
- `main` was not committed to, merged, rebased, force-updated, or otherwise modified.
- `compare_commits(0c876246..., phase18/story-intelligence)` was `identical` before this Change Set, so no unreviewed branch drift preceded CS273.

## Baseline verification

Before CS273, the preceding CS272 HEAD was confirmed CI-green:

- Workflow: `Phase 18 Story Intelligence Verification`
- Run: `33302522145`
- Run number: `4181`
- Result: `completed / success`

Other Phase 18 workflows associated with that SHA were also reported `completed / success` by GitHub.

## Gap found

CS272 correctly byte-admitted the exact `composed_candidate.png`, but it was deliberately non-semantic. Therefore downstream logic still lacked a byte-bound post-composition semantic inspection proving that deterministic/verified composition had not introduced or exposed visual defects such as broken sport geometry, conflicting perspective, residual generated/pseudo text, generated brand/marks, or conflicting generated geometry.

The repository already contained the intended solution primitives. `qwen25_vl_inspector.py` defines `SemanticInspectionStage.HYBRID_SURFACE` specifically for the image after deterministic sport-geometry composition, and the existing `SemanticVisualVerdictGate` plus `SemanticLayerEvidenceAdapter` already enforce fail-closed normalized evidence. CS273 reuses these contracts instead of creating a parallel QA policy.

## Added

### Production/control-plane engine

`engine/intelligence/qwen_image_composed_candidate_hybrid_surface_semantic_qa.py`

Adds a byte-bound CS273 run and verifier that:

- requires a successfully reverified CS272 receipt;
- reopens the exact CS272 composed PNG and rejects path/symlink/byte drift;
- invokes the pinned Qwen2.5-VL inspector in `HYBRID_SURFACE` mode;
- requires the existing verifier ID and approved model ID/revision;
- reuses `SemanticVisualVerdictGate` with geometry-alignment, exact-number-absence and generated-sport-geometry-absence requirements enabled;
- reuses `SemanticLayerEvidenceAdapter` at minimum confidence 0.85;
- treats missing/not-inspected/low-confidence evidence as blocking;
- records semantic verdict and normalized layer evidence;
- permits only `hybrid_surface_semantic_qa_approved` as the new stage-specific approval;
- keeps global semantic, Human Review, Golden, and publication authorities false;
- re-verifies receipt digest, CS272 bytes, composed PNG bytes, inspector identity, verdict normalization, recomputed decision, and layer evidence.

### Regression coverage

`tests/test_phase18_qwen_image_composed_candidate_hybrid_surface_semantic_qa.py`

Covers:

- successful hybrid-surface inspection with no authority escalation;
- sport-geometry alignment failure;
- confidence below the 0.85 threshold;
- residual generated-text evidence;
- composed-PNG byte tamper;
- CS272 receipt byte tamper;
- premature Golden authority;
- verifier-ID drift;
- output-directory reuse.

Test PNG content is synthetic control-plane fixture data only and is not represented as a production or Golden visual.

### CLI

`tools/phase18_run_composed_candidate_hybrid_surface_semantic_qa.py`

Runs the production CS273 inspector/verifier against an admitted CS272 receipt. It exposes no mock verdict input and does not provide a path for user-supplied replacement verifier identity. A rejected semantic verdict exits non-zero.

### Contract documentation

`docs/PHASE18_CHANGESET_273_COMPOSED_CANDIDATE_HYBRID_SURFACE_SEMANTIC_QA.md`

Documents scope, upstream requirements, reused semantic contracts, identity separation, authority boundaries, verifier behavior, tests, and remaining Golden path.

### Implementation log

`docs/PHASE18_IMPLEMENTATION_LOG_273.md`

This file records the implementation and verification state of the Change Set.

## Modified

No pre-existing production gate, renderer, semantic inspector, identity policy, sentiment policy, zero-cost policy, Visual Critic, Human Review contract, Golden threshold, Brand/Typography contract, or `SemanticPublicationGate` was modified.

This implementation log may receive a documentation-only follow-up update when the terminal GitHub Actions result for CS273 is known.

## Deleted

None.

## Commits

- `63d0a2a6882c88634722fbf2cd3d66f7335beadd` — add CS273 composed hybrid-surface semantic QA engine
- `ad89a4c7777919160c3ee46483ccd70f3d98f79f` — add CS273 regression coverage
- `09f177103ddcd3843cf28180254dec2f7e22f5c0` — add CS273 production CLI
- `1b356fc4d5f8e3a7629f8cce83b04d2ef8fb5469` — add CS273 contract documentation

## Authority preservation

CS273 may prove only:

- `semantic_inspection_executed = true`
- `hybrid_surface_semantic_qa_approved = true` when all required checks pass

It deliberately keeps:

- `composed_visual_approved = false`
- `semantic_approved = false`
- `human_visual_review_approved = false`
- `genuine_golden_png_created = false`
- `golden_quality_approved = false`
- `publication_ready = false`

Identity is not inferred by CS273 because the current pinned Qwen2.5-VL inspector returns no `identity_valid` evidence. Dedicated CS265–CS267 identity evidence remains authoritative where required.

## Test/CI state

- The CS273 engine source was syntax-compiled locally before repository write.
- GitHub Actions were triggered by the branch commits.
- At the time this initial log was written, the workflow for executable SHA `09f177103ddcd3843cf28180254dec2f7e22f5c0` had been created but remained queued; no CI-green claim is made until a terminal successful run is observed.

## Runtime / genuine Golden state

The execution runtime available to this automation was measured during this Change Set:

- `torch_version = 2.10.0+cpu`
- `cuda_available = False`
- `torch_cuda_version = None`
- `bf16_supported = False`
- `device_count = 0`
- `nvidia-smi = unavailable`

Therefore this runtime cannot truthfully perform the upstream genuine Qwen-Image CUDA/BF16 generation step. No model-load, inference, production candidate PNG, production composed PNG, Visual Critic score, Human Review result, Golden score, or Genuine Golden Visual PNG was fabricated.

The exact production blocker remains the absence of one zero-cost compatible execution host proving together: NVIDIA CUDA, native BF16, sufficient VRAM/RAM, the exact pinned `Qwen/Qwen-Image-2512` revision, successful compatible `QwenImagePipeline` load, and the required sequential CPU-offload/runtime contract.

## Remaining gap

The controlled path is now:

`genuine story -> factual/identity/sentiment/zero-cost/semantic gates -> CS257 -> CS258–260 -> CS261 -> CS262 genuine Qwen inference -> CS263 -> CS264 -> CS265–267 when required -> CS268 -> CS269 -> CS270 -> CS271 composition -> CS272 exact composed-byte admission -> CS273 HYBRID_SURFACE semantic QA -> byte-bound Visual Critic -> Human Review -> Golden threshold -> exact Brand/Typography verification -> SemanticPublicationGate`

The next safe preparatory step after a green CS273 is to inspect and bind the existing Visual Critic contract to the exact CS272/CS273 composed bytes while preserving Human Review and Golden thresholds as independent fail-closed authorities.
