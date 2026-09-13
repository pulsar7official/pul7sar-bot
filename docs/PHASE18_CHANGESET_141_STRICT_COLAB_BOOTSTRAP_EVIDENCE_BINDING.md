# PUL7SAR Phase 18 — Change Set 141

## Strict Colab Bootstrap Evidence Binding

### Objective

Make the preferred first-Golden Colab entrypoint tamper-evident across the pre-GPU and semantic-model preparation stages, not only across the later human-review packet.

Change Sets 139–140 already protected combined Qwen + FLUX cache headroom before model downloads. Change Set 138 already made the first-Golden Colab path strict and fail-closed. The remaining gap was that the final bootstrap receipt referenced repository integrity, cache budget, Qwen preparation and the sealed review receipt primarily by path. A stale or replaced receipt could therefore be harder to diagnose after the GPU session.

### Changes

`tools/phase18_colab_first_golden_bootstrap.py` now:

- requires the exact Qwen cache receipt after semantic-model prefetch;
- validates schema `pul7sar-phase18-qwen-model-cache-v1`;
- validates model `Qwen/Qwen2.5-VL-3B-Instruct`;
- validates `$0-local` and `ready=true`;
- records SHA-256 and file size for repository-integrity evidence;
- records SHA-256 and file size for the combined first-Golden cache-budget receipt;
- records SHA-256 and file size for the Qwen model-cache receipt;
- records SHA-256 and file size for the sealed Candidate 1 human-review receipt;
- upgrades the final bootstrap schema to `pul7sar-first-golden-colab-bootstrap-v2`;
- keeps human approval, Golden approval, publication readiness and Seeds 2–4 authorization explicitly false.

`tests/test_phase18_colab_first_golden_bootstrap.py` now adds regression coverage for:

- the v2 bootstrap contract;
- Qwen model-cache identity drift;
- presence of all four SHA-bound bootstrap evidence records;
- fail-closed behavior when required bootstrap evidence is missing;
- preservation of the established ordering: repository integrity -> runtime repair -> shared-cache budget -> semantic runtime -> Qwen prefetch -> sealed Candidate 1 staging.

### Safety preserved

This change does not:

- alter Fact Lock;
- alter entity/identity verification;
- alter sentiment or losing-side neutrality;
- authorize a paid provider;
- alter FLUX.2 Klein 4B, BF16, seeds or canvas locks;
- bypass Qwen BASE_SCENE or HYBRID_SURFACE checks;
- bypass deterministic football geometry or artifact integrity;
- change Golden 8.5 / 9.0+ thresholds;
- grant brand, typography or SemanticPublicationGate approval;
- fabricate any PNG or benchmark.

### Deleted

Nothing.

### Remaining execution blocker

The first genuine Golden Hybrid v5 Candidate 1 still requires a compatible NVIDIA CUDA + BF16 host. This change only reduces evidence ambiguity around that scarce execution window; it does not claim GPU generation occurred.
