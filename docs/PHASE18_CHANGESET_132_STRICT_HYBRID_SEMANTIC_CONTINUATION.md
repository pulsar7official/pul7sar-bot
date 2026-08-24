# PUL7SAR Phase 18 — Change Set 132

## Strict Hybrid Semantic Continuation from the Proven First PNG

### Purpose

Change Set 131 created a tamper-evident bridge from the genuine provenance-locked Candidate 1 PNG into the canonical Hybrid v5 summary consumed by the existing semantic/composition path. One orchestration gap remained: the self-hosted GPU smoke workflow sealed that handoff into evidence, but did not continue the same run through BASE_SCENE semantic/layer ownership, deterministic football composition and HYBRID_SURFACE semantic/alignment inspection.

That meant a successful first GPU run could still stop one stage before the most valuable visual proof.

Change Set 132 closes that gap without generating another FLUX image and without weakening any gate.

### Added

#### `tools/phase18_continue_hybrid_from_first_png.py`

A strict continuation command that:

- runs only on `phase18/story-intelligence`;
- requires Candidate 1;
- consumes the canonical `output/phase18_colab/latest.json` first-PNG Hybrid handoff;
- replays the handoff contract, BF16, `$0-local`, deterministic-surface ownership and base PNG SHA-256;
- does **not** run FLUX and does **not** mutate the generation queue;
- calls the existing Hybrid v5 semantic/composition implementation on the already-proven base bytes;
- requires BASE_SCENE semantic approval and complete layer-ownership approval before deterministic composition;
- requires deterministic football artifact integrity;
- requires HYBRID_SURFACE semantic/alignment approval;
- produces a SHA-256-bound Hybrid PNG receipt;
- leaves Golden quality and publication approval false.

Successful status:

`FIRST_GOLDEN_HYBRID_SEMANTIC_PROOF_READY`

The stage may set `semantic_layer_gate_approved=true` and `hybrid_semantic_review_approved=true` only after the actual local Qwen checks pass. It cannot set `golden_quality_approved` or `publication_ready` to true.

#### `tests/test_phase18_first_png_hybrid_semantic_continuation.py`

Regression coverage for:

- successful BASE_SCENE + HYBRID_SURFACE continuation;
- Hybrid semantic failure remaining fail-closed;
- publication-authority drift rejection;
- handoff/base-PNG SHA tampering rejection before Qwen/composition;
- branch and Candidate 1 locks.

### Modified

#### `.github/workflows/phase18-gpu-smoke.yml`

The self-hosted GPU smoke now continues after the first-PNG Hybrid handoff:

`Candidate 1 → provenance postflight → Hybrid handoff → strict BASE_SCENE semantic/layer QA → deterministic football composition → HYBRID_SURFACE semantic/alignment QA → evidence sealing`

The workflow validates that:

- the continuation status is exact;
- Candidate 1 and Golden v5 remain locked;
- BASE_SCENE semantic/layer ownership approved;
- HYBRID_SURFACE semantic/alignment approved;
- deterministic hybrid artifact integrity is valid;
- a real Hybrid PNG exists;
- Golden quality remains unapproved;
- publication remains blocked.

The new continuation receipt is included in the tamper-evident GPU evidence manifest.

#### `tests/test_phase18_gpu_smoke_hybrid_handoff.py`

The workflow-order regression contract now requires:

`generation < provenance postflight < Hybrid handoff < strict Hybrid semantic continuation < evidence sealing`

It also verifies that the continuation may close semantic gates but not Golden-quality or publication gates.

### Deleted

Nothing.

### Gate preservation

No change was made to:

- Fact Lock;
- entity/identity verification;
- sentiment and losing-side neutrality;
- `$0-local` policy;
- FLUX.2 Klein 4B model lock;
- native BF16 lock;
- seed/canvas locks;
- generated text exclusion;
- generated PUL7SAR branding exclusion;
- generated exact score/number exclusion;
- generated club/entity mark exclusion;
- generated exact sport geometry exclusion;
- Qwen BASE_SCENE or HYBRID_SURFACE semantic requirements;
- deterministic football geometry ownership;
- Golden minimum 8.5 / elite 9.0+ thresholds;
- SemanticPublicationGate;
- exact brand or typography integrity.

### Effect on the remaining gap

A single future compatible CUDA/BF16 run can now produce not only the genuine FLUX Candidate 1 base PNG, but also the first strict semantic-approved deterministic Hybrid proof from the **same provenance-locked pixels**. No second FLUX generation is required to reach this point.

The remaining post-GPU steps are visual/human pitch-integration review, SHA-bound Golden quality review, exact brand/typography composition and final publication gates.
