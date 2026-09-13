# PUL7SAR Phase 18 — Change Set 158

## Immutable Qwen Semantic Model Revision Lock

### Problem

The Golden Candidate path already locked the FLUX.2 Klein 4B upstream revision, but the Qwen semantic verifier still identified only the mutable Hugging Face repository name `Qwen/Qwen2.5-VL-3B-Instruct`. A future upstream change to that repository could therefore alter BASE_SCENE or HYBRID_SURFACE semantic evidence while PUL7SAR still reported the same model ID.

That is unacceptable for the first genuine Golden Visual because semantic evidence must be reproducible and attributable to exact model bytes, not only a mutable repository name.

### Approved immutable semantic revision

Model: `Qwen/Qwen2.5-VL-3B-Instruct`

Approved Hugging Face revision:

`66285546d2b821cf421d4f5eb2576359d3770cd3`

The revision was resolved from the public Hugging Face model history before being committed to the Phase 18 contract.

### Changes

- Extended `engine/intelligence/approved_model_revisions.py` with the exact Qwen model ID and full 40-character revision.
- Upgraded `tools/phase18_prefetch_qwen.py` so both local-only cache lookup and network acquisition use the same immutable revision.
- Qwen cache receipts are now `pul7sar-phase18-qwen-model-cache-v2` and record approved revision, resolved snapshot revision, and `revision_pinned=true`.
- Canonical Hugging Face `snapshots/<commit-sha>` paths are replay-validated before the cache can be accepted.
- Upgraded `tools/phase18_preflight_semantic_gpu.py` to `pul7sar-phase18-semantic-gpu-preflight-v2` and made revision proof a required fail-closed condition.
- Updated `Qwen25VLConfig` and isolated subprocess configuration to carry the approved revision explicitly.
- `Qwen25VLSemanticInspector._load()` now rejects model-ID or revision drift before creating the Transformers pipeline and passes the immutable revision directly to `pipeline(...)`.
- Updated the strict first-Golden Colab bootstrap so the Candidate 1 path will not proceed from Qwen cache preparation to sealed review staging unless the exact semantic revision is proven.

### Regression coverage

Tests now cover:

- exact 40-character Qwen revision identity;
- revision propagation through cache lookup/download;
- canonical snapshot revision replay;
- semantic-preflight model/revision/cost-mode validation;
- Qwen runtime rejection of revision drift before pipeline load;
- strict Golden bootstrap rejection of semantic revision drift;
- preservation of process isolation and all downstream publication gates.

### Preserved gates

No relaxation was made to Fact Lock, Entity/Identity Verification, Sentiment/Neutrality, `$0-local`, native BF16, Candidate/request/seed/canvas/SHA locks, generated text/branding/exact-fact/entity-mark/sport-geometry prohibitions, Qwen BASE_SCENE/HYBRID_SURFACE requirements, deterministic football geometry, Golden 8.5/9.0 thresholds, Exact Brand Integrity, Typography Integrity, or SemanticPublicationGate.

No fake PNG, paid provider, secret, precision downgrade, or publication authority was introduced.

### Remaining blocker

A genuine Golden Hybrid v5 Candidate 1 still requires a compatible NVIDIA CUDA host with native BF16 and sufficient live free VRAM to run the locked FLUX revision followed by the locked Qwen semantic revision. No GPU result is claimed by this change set.
