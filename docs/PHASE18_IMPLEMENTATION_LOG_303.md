# Phase 18 Implementation Log 303 — Sealed Handoff Candidate Admission

## Scope

Branch only: `phase18/story-intelligence`.

`main` was inspected for safety only and was not modified, merged, rebased, force-updated or used as a write target.

Starting Phase 18 HEAD: `cb1e3c6734ee3cf93ac58711762601bcae550596` (CS302).

## State reviewed before change

CS302 had already made successful canonical execution produce and replay `canonical_candidate_handoff.json`. The earlier production admission CLI, however, still accepted a bare CS262 canonical inference receipt through `--cs262-receipt`. That was a real downstream lineage bypass: post-generation QA could begin without requiring the newer CS301/302 sealed handoff.

CS303 closes that bypass at the existing production admission edge rather than adding another optional wrapper.

## Modified

### `engine/intelligence/qwen_image_canonical_candidate_byte_admission.py`

- upgrades the admission schema to v2;
- changes the production admission source from a bare canonical inference receipt to a CS301/302 candidate handoff;
- replays `verify_canonical_candidate_handoff(...)` before admission;
- requires `$0-local`, network disabled and local-files-only state from the handoff;
- derives the canonical inference receipt and candidate PNG paths only from verified handoff bindings;
- re-hashes and reopens both derived files;
- replays the canonical inference receipt independently;
- requires exact story SHA agreement;
- requires exact candidate path/hash/byte-size/dimension agreement across handoff, canonical receipt and local file bytes;
- records the sealed handoff as an explicit source binding in the admission receipt;
- replays the handoff again during admission verification;
- keeps semantic, Human Review, Golden-quality, Genuine Golden and publication authority false.

### `tools/phase18_admit_canonical_candidate_bytes.py`

- replaces `--cs262-receipt` with required `--candidate-handoff`;
- exposes no raw candidate, model, prompt, seed, dimensions, inference, network, paid-mode, approval, Golden or publication override;
- reports `handoff_sealed` in its successful result.

### `tests/test_phase18_qwen_image_canonical_candidate_byte_admission.py`

Regression coverage now verifies:

- sealed-handoff admission succeeds without quality/publication authority;
- a bare canonical inference receipt is rejected as an admission source;
- candidate byte drift after admission is rejected;
- premature semantic authority in the handoff is rejected;
- symlinked candidate input is rejected;
- pre-existing output directory is rejected fail-closed.

## Added

- `docs/PHASE18_CHANGESET_303_SEALED_HANDOFF_CANDIDATE_ADMISSION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_303.md`

## Deleted

None.

## Gate preservation

CS303 does not weaken or bypass:

- Fact/Freshness Lock;
- Entity/Identity Verification;
- sentiment neutrality and loser-respect policy;
- story-bound semantic ownership;
- `$0-local` and local-only execution;
- generated-layer/composition QA;
- semantic candidate approval;
- visual-quality adjudication;
- Human Review;
- exact brand/typography;
- `SemanticPublicationGate`;
- Genuine Golden materialization;
- publication readiness.

The admission receipt requires these downstream authorities to remain false:

- `semantic_approved`;
- `human_visual_review_approved`;
- `golden_quality_approved`;
- `genuine_golden_png_created`;
- `publication_ready`.

## Testing

The branch regression suite was updated for the new sealed-handoff contract. GitHub Actions is the authoritative repository-wide verification surface for this connector-backed run; its result must be checked on the final CS303 HEAD before declaring the change terminal-green.

No CPU/control-plane test is treated as evidence of genuine Qwen model load, CUDA inference or a Golden PNG.

## Current execution blocker

The execution environment available during this implementation run reports:

- PyTorch `2.10.0+cpu`;
- `torch.cuda.is_available() == false`;
- `torch.version.cuda == None`;
- CUDA device count `0`;
- native BF16 support unavailable;
- `nvidia-smi` unavailable.

Therefore no genuine Qwen model load, CUDA/BF16 inference, `canonical_candidate.png`, composed production PNG or Genuine Golden PNG was fabricated.

The remaining hardware/runtime requirement is a zero-cost host providing NVIDIA CUDA, CUDA-enabled PyTorch, native BF16, the CS260-authorized compatible QwenImagePipeline/Diffusers runtime, sequential CPU offload, the exact approved already-local Qwen snapshot, and enough RAM/VRAM proven by real model load and inference.

## Remaining path

Verified launch manifest → preload/offline/runtime gates → genuine local Qwen inference → CS290 provenance → CS293/CS300 replay → CS301/CS302 sealed handoff → **CS303 sealed-handoff candidate byte admission** → factual/identity/sentiment revalidation → semantic/composition/generated-layer/visual-quality gates → Human Review → exact brand/typography → `SemanticPublicationGate` → Genuine Golden materialization → publication readiness.
