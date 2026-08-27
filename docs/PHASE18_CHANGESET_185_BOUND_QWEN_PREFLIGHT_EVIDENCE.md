# PUL7SAR Phase 18 — Change Set 185

## Bound Qwen Preflight Evidence in the Canonical Golden v6 Path

### Purpose

Close the evidence gap between the pre-FLUX immutable Qwen semantic preflight and the resource/runtime lock that ultimately stages Golden Editorial v6 Candidate 1.

Before this change, the canonical GitHub workflow ran `phase18_preflight_semantic_gpu.py` as a separate step and replayed it later, while `phase18_colab_first_genuine_resources_locked.py` sealed GPU, host-memory, runtime and strict-staging evidence without owning the semantic-preflight and Qwen-cache receipts itself.

That meant the semantic model was checked before FLUX, but its receipt was not part of the same SHA-bound resource/runtime evidence set that authorized Candidate 1 staging.

### Implementation

`tools/phase18_colab_first_genuine_resources_locked.py` now:

- qualifies GPU and live host memory first;
- runs immutable Qwen semantic/model preflight before Candidate 1;
- validates `pul7sar-phase18-semantic-gpu-preflight-v2`;
- validates `pul7sar-phase18-qwen-model-cache-v2`;
- requires exact `Qwen/Qwen2.5-VL-3B-Instruct` identity and approved immutable revision;
- verifies the canonical cached snapshot revision and semantic-preflight-to-cache path binding;
- requires CUDA semantic readiness and `$0-local`;
- rejects generation/queue/PNG/publication authority drift from semantic preflight;
- captures the runtime fingerprint only after semantic preflight is proven;
- seals both `semantic-preflight.json` and `qwen-model-cache.json` into the final evidence map by SHA-256 and byte size;
- upgrades the resource lock to `pul7sar-first-genuine-golden-v6-resource-lock-v3` with `FIRST_GENUINE_GOLDEN_V6_RESOURCE_RUNTIME_SEMANTIC_LOCK_VERIFIED`.

The canonical workflow now relies on that single bound execution seam instead of maintaining a separate unbound Qwen preflight step. Its replay phase revalidates the semantic preflight, Qwen cache, immutable snapshot path, runtime fingerprints, strict staging and final PNG before artifact upload.

### Regression coverage

`tests/test_phase18_first_genuine_golden_v6_workflow.py` now locks the order:

`GPU qualification → host RAM → immutable Qwen preflight/cache → runtime fingerprint PRE → strict Candidate 1 → runtime fingerprint POST → evidence replay`

It also requires semantic/cache receipts to be present inside the final evidence map and keeps Human/Golden/Publication/Seeds authority closed.

### Safety properties preserved

No factual, identity, sentiment, zero-cost, semantic-publication or visual-quality gate is weakened. Candidate 1 remains the only authorized seed until it genuinely exists and passes review. No fake PNG, paid provider, precision downgrade or publication bypass is introduced.
