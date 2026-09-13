# PUL7SAR Phase 18 — Change Set 159

## Runtime Stack Fingerprint Across First-Golden Execution

### Problem

FLUX and Qwen model revisions are now immutable, but the first genuine Candidate 1 could still be executed with different resolved Python package versions inside the allowed GPU dependency ranges. A dependency change during runtime repair or execution would make a visual proof harder to reproduce even when prompt, seed, canvas, model revisions and PNG bytes are otherwise locked.

### Change

Added an additive runtime-lock layer without modifying the existing strict Candidate 1 bootstrap.

`engine/intelligence/generation_runtime_fingerprint.py` captures a canonical contract containing:

- Python version / implementation / machine;
- exact resolved versions for Diffusers, Transformers, Accelerate, Safetensors, Hugging Face Hub, Pillow and Tokenizers;
- Torch version and CUDA runtime version;
- CUDA availability, GPU identity and compute capability;
- immutable FLUX.2 Klein 4B revision;
- immutable Qwen2.5-VL 3B revision;
- `$0-local` cost mode.

The existing exact semantic pins remain enforced (`transformers==4.56.2`, `Pillow==11.3.0`), while the currently approved bounded GPU packages remain range-qualified. Their *resolved* versions are now part of the SHA-256 fingerprint.

`tools/phase18_colab_first_golden_runtime_locked.py` is a new optional/preferred Colab entrypoint that:

1. verifies the Phase 18 branch;
2. repairs the runtime exactly once using the existing verified repair path;
3. captures a pre-execution runtime fingerprint;
4. invokes `phase18_colab_first_golden_bootstrap.py --skip-repair` so the environment is not deliberately changed again;
5. reaches the existing strict Candidate 1 sealed review path;
6. captures a post-execution runtime fingerprint;
7. fails closed unless pre/post fingerprint SHA-256 values are identical;
8. SHA-binds the pre fingerprint, post fingerprint and strict-bootstrap receipt in the final runtime-lock receipt.

The wrapper cannot authorize human approval, Golden approval, publication, or Seeds 2–4.

### Added

- `engine/intelligence/generation_runtime_fingerprint.py`
- `tools/phase18_colab_first_golden_runtime_locked.py`
- `tests/test_phase18_generation_runtime_fingerprint.py`
- `tests/test_phase18_first_golden_runtime_lock.py`
- `docs/PHASE18_CHANGESET_159_RUNTIME_STACK_FINGERPRINT.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_159.md`

### Modified

None of the existing generation, semantic, quality, or publication runtime modules were modified. The change is additive.

### Deleted

None.

### Safety / preserved gates

No change to Fact Lock, Entity/Identity Verification, Sentiment/Neutrality, `$0-local`, native BF16, model revisions, Candidate/request/seed/canvas/SHA locks, generated-text/branding/exact-fact/entity-mark/sport-geometry prohibitions, Qwen BASE_SCENE/HYBRID_SURFACE gates, deterministic football geometry, provenance replay, Golden thresholds, Exact Brand/Typography Integrity, or SemanticPublicationGate.

No PNG is fabricated and no paid provider or hosted GPU fallback is introduced.
