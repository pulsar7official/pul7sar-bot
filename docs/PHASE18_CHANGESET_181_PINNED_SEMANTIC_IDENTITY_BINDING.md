# PUL7SAR Phase 18 — Change Set 181

## Pinned Semantic Identity Binding at First Genuine Golden Staging

### Goal

Close the remaining semantic-provenance gap at the boundary where Golden Editorial v6 Candidate 1 becomes eligible for human visual review.

Generation provenance was already replayed against the exact Candidate 1 PNG, pinned FLUX revision, BF16 precision tier, seed, request ID, payload SHA, executor result, proof metadata, and `$0-local` cost mode. The semantic receipt, however, was only required to report an approved Qwen inspection and complete layer gate. A stale or incompatible semantic runtime identity could therefore survive farther than intended before human review.

### Implementation

`tools/phase18_colab_first_genuine_golden.py` now requires the semantic receipt to prove:

- `semantic_runtime.ready == true`;
- `semantic_runtime.model_id == Qwen/Qwen2.5-VL-3B-Instruct`;
- `semantic_runtime.cuda_available == true`;
- `semantic_visual_inspection.approved == true`;
- the exact approved revision-pinned isolated BASE_SCENE verifier ID;
- the same Candidate 1 PNG path already bound to generation provenance.

The staging receipt is upgraded to `pul7sar-first-genuine-golden-staging-v3` and records:

- approved Qwen model ID;
- approved immutable Qwen upstream revision;
- exact semantic verifier ID;
- semantic runtime readiness/CUDA evidence;
- SHA-256 of the semantic receipt itself;
- existing pinned FLUX generation provenance and PNG evidence.

No semantic approval is inferred from the model name alone. The source-controlled verifier ID must match the revision-pinned Qwen inspector implementation, and the durable semantic receipt remains SHA-bound in staging.

### Regression coverage

`tests/test_phase18_first_genuine_golden.py` now verifies:

- staging-v3 success with pinned FLUX and Qwen identities;
- semantic receipt SHA binding;
- rejection of semantic model ID drift;
- rejection of semantic runtime not-ready state;
- rejection when CUDA is not proven for the semantic runtime;
- rejection of verifier-ID drift;
- all previous BF16, zero-cost, PNG identity, composition-map, pitch-policy, provenance replay, and publication-blocking behavior.

### Safety / quality impact

This change does not authorize publication, Golden quality, brand composition, typography, or Seeds 2–4. It only tightens the evidence required before Candidate 1 may enter human visual review.

All existing factual, identity, sentiment/neutrality, zero-cost, semantic-publication, and Golden visual-quality gates remain fail-closed.
