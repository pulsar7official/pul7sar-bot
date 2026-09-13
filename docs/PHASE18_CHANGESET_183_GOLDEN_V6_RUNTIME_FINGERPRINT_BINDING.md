# PUL7SAR Phase 18 — Change Set 183

## Golden v6 Runtime Fingerprint Binding

### Objective

Bind the canonical first genuine Golden Editorial v6 Candidate 1 to the exact approved software/runtime stack immediately before and immediately after generation + BASE_SCENE semantic staging.

The canonical v6 path already proved immutable source SHA, CUDA/native BF16, live GPU VRAM, live host RAM, pinned FLUX/Qwen revisions, strict semantic staging, PNG provenance and downstream authority closure. The remaining reproducibility gap was that the v6 resource-lock wrapper did not replay the software-stack fingerprint that Phase 18 already uses in the older first-Golden path.

### Changes

#### Modified: `tools/phase18_colab_first_genuine_resources_locked.py`

- captures `generation-runtime-fingerprint` immediately after GPU/RAM qualification and before strict Candidate 1 staging;
- captures the runtime fingerprint again after generation + BASE_SCENE semantic/layer staging;
- fails closed through `verify_matching_runtime_fingerprints()` if any approved runtime component changes during the run;
- persists both pre/post fingerprint receipts inside `output/phase18_gpu_smoke`;
- SHA-binds both receipts into the final evidence set;
- upgrades the final contract to `pul7sar-first-genuine-golden-v6-resource-lock-v2`;
- records `runtime_fingerprint_sha256` and `runtime_stable_across_generation=true`;
- keeps Human, Golden, Publication and Seeds 2-4 authority closed.

#### Modified: `.github/workflows/phase18-first-genuine-golden-v6.yml`

- replays the expanded five-file evidence set;
- verifies pre/post runtime fingerprint receipts using the same canonical verifier;
- requires the replayed runtime digest to match the digest sealed into the final resource/runtime-lock receipt;
- keeps the immutable dispatch SHA, Phase 18 branch isolation, self-hosted CUDA/BF16, `$0-local`, strict staging and PNG replay gates unchanged.

#### Modified: `tests/test_phase18_first_genuine_golden_v6_workflow.py`

- regression-locks order: GPU -> host RAM -> runtime fingerprint pre -> strict Candidate 1 -> runtime fingerprint post -> fingerprint verification;
- requires canonical workflow replay of both runtime receipts;
- requires the v2 resource/runtime-lock contract;
- continues to assert Human/Golden/Publication/Seeds authority remains closed.

### Deleted

None.

### Gates preserved

No factual, identity, sentiment, zero-cost, semantic-publication or visual-quality gate was weakened. In particular:

- Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality and losing-side respect;
- `$0-local`;
- pinned FLUX.2 Klein 4B revision;
- pinned Qwen2.5-VL revision/verifier identity;
- native BF16;
- live GPU VRAM and host-RAM qualification;
- Candidate/request/seed/canvas/SHA locks;
- generated text/branding/exact-fact/entity-mark/exact-sport-geometry prohibitions;
- Qwen BASE_SCENE semantic and layer-ownership QA;
- Golden 8.5 minimum / 9.0+ elite target;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate.

### Genuine PNG status

No Golden Editorial v6 PNG is claimed by this change set. A compatible self-hosted NVIDIA CUDA host with native BF16, sufficient live VRAM/RAM, safe local Diffusers runtime/offload and the pinned local model revisions is still required. The change materially reduces the remaining gap by making the first real Candidate 1 reproducible against a single stable runtime digest across generation and semantic staging.
