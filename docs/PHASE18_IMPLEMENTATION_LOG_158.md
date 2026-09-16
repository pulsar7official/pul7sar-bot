# PUL7SAR Phase 18 — Implementation Log 158

## Scope and branch state

Repository: `pulsar7official/pul7sar-bot`

Write target: `phase18/story-intelligence` only.

Starting Phase 18 HEAD reviewed before changes: `8e6c9f9ed3fe759e9d0db0cc5f48d069f0c9888e`.

`main` was independently at `5c95eff1aaf404491304835898b719911e0647a1` when reviewed. The branch comparison remained `diverged`; after the implementation changes Phase 18 was 1408 commits ahead and 145 behind `main`. `main` / `main.py` were not modified, merged, force-updated, or used as a write target.

Change Set 157 verification is confirmed: GitHub Actions Phase 18 Story Intelligence Verification run `32904013025` / run `2739` completed with `success` on `8e6c9f9ed3fe759e9d0db0cc5f48d069f0c9888e`, and the companion Phase 18 CPU workflows on that commit also completed successfully.

## Change Set 158 — Immutable Qwen Semantic Model Revision Lock

### Why this materially reduces the remaining gap

FLUX generation was already revision-bound, but the semantic verifier still loaded Qwen by mutable repository name. That left a reproducibility gap: BASE_SCENE or HYBRID_SURFACE evidence could change after an upstream model update even if Candidate identity, FLUX revision, prompt, seed and image bytes remained fixed.

Change Set 158 closes that gap by binding Qwen cache acquisition, semantic GPU preflight, isolated runtime loading and the strict first-Golden bootstrap to one immutable upstream semantic-model revision.

Approved Qwen revision:

`66285546d2b821cf421d4f5eb2576359d3770cd3`

The public Hugging Face history for `Qwen/Qwen2.5-VL-3B-Instruct` was checked before pinning this full commit SHA.

### Added

- Qwen immutable model/revision constants in `engine/intelligence/approved_model_revisions.py`.
- Revision-aware regression assertions in `tests/test_phase18_qwen_model_prefetch.py`.
- Runtime revision-drift regression coverage in `tests/test_phase18_qwen_process_isolation.py`.
- Semantic preflight revision-drift coverage in `tests/test_phase18_semantic_gpu_preflight.py`.
- Strict bootstrap semantic revision-drift coverage in `tests/test_phase18_colab_first_golden_bootstrap.py`.
- `docs/PHASE18_CHANGESET_158_IMMUTABLE_QWEN_MODEL_REVISION.md`.
- `docs/PHASE18_IMPLEMENTATION_LOG_158.md`.

### Modified

- `engine/intelligence/approved_model_revisions.py`
  - added `QWEN25_VL_3B_MODEL_ID` and `QWEN25_VL_3B_REVISION`.
- `tools/phase18_prefetch_qwen.py`
  - cache-only resolution and download now use the same immutable revision;
  - canonical snapshot revision is replay-validated;
  - receipt upgraded to `pul7sar-phase18-qwen-model-cache-v2`;
  - receipt records approved revision, resolved revision and `revision_pinned=true`.
- `tools/phase18_preflight_semantic_gpu.py`
  - receipt upgraded to `pul7sar-phase18-semantic-gpu-preflight-v2`;
  - exact Qwen revision and canonical snapshot path are required;
  - revision drift fails before FLUX generation.
- `engine/intelligence/qwen25_vl_inspector.py`
  - `Qwen25VLConfig` carries immutable `model_revision`;
  - isolated subprocess transfers the revision explicitly;
  - runtime loader rejects model/revision drift before pipeline creation;
  - Transformers pipeline receives the immutable revision directly;
  - verifier ID advanced to revision-pinned v6.
- `tools/phase18_colab_first_golden_bootstrap.py`
  - strict Candidate 1 path validates Qwen cache v2 and the exact approved semantic revision before sealed review staging;
  - bootstrap result records the pinned Qwen revision.
- `tests/test_phase18_qwen_model_prefetch.py`
  - updated for revision-aware cache contract.
- `tests/test_phase18_semantic_gpu_preflight.py`
  - updated for cache/preflight v2 and fail-closed revision checks.
- `tests/test_phase18_qwen_process_isolation.py`
  - verifies default revision pin and runtime drift rejection.
- `tests/test_phase18_colab_first_golden_bootstrap.py`
  - fixture upgraded to Qwen cache v2;
  - explicit revision drift rejection added.

### Deleted

None.

## Preserved contracts and gates

No change was made to:

- Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality;
- `$0-local` policy;
- FLUX.2 Klein 4B model identity or immutable FLUX revision;
- native BF16 requirement;
- Candidate/request/seed/canvas/SHA locks;
- generated text / platform branding / exact facts / entity marks / sport geometry prohibitions;
- Qwen BASE_SCENE and HYBRID_SURFACE semantic inspection requirements;
- deterministic football geometry ownership;
- generation provenance/evidence replay;
- Golden visual-quality thresholds (8.5 minimum, 9.0+ elite);
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate / final publication readiness.

The Qwen revision lock adds no paid provider, no secret, no precision downgrade, no fake image and no publication authority.

## Tests and verification status

The implementation adds regression coverage for immutable Qwen cache, semantic preflight, isolated runtime loading and strict bootstrap integration. A fresh GitHub Actions result must be observed on the new HEAD before Change Set 158 is described as fully CI-green. No success is inferred solely from writing the tests.

## Remaining exact blocker to first genuine Golden Visual PNG

No compatible physical execution host is available in the current tool/runtime environment. Candidate 1 still requires an NVIDIA CUDA host proving native BF16 and sufficient live free VRAM for the immutable FLUX.2 Klein 4B revision, followed by semantic verification with the immutable Qwen revision above. No PNG, visual score, benchmark or GPU success is fabricated.

Current intended path:

`immutable Phase 18 source → repository/runtime/cache checks → immutable FLUX revision → immutable Qwen revision → Original Scene admission → Candidate 1 lease → lease-bound live GPU requalification → genuine FLUX PNG → revision-bound provenance replay → BASE_SCENE ownership QA → deterministic football Hybrid → HYBRID_SURFACE QA → sealed human review → Golden 8.5/9.0 → exact brand/typography → SemanticPublicationGate`

Seeds 2–4 remain unauthorized until Candidate 1 exists genuinely and passes the required semantic and visual review gates.
