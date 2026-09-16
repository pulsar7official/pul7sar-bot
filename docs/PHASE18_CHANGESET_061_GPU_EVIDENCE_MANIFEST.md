# PUL7SAR Phase 18 — Change Set 061

## GPU evidence manifest and artifact integrity

### Purpose
The first genuine Golden Visual PNG must be easy to audit and retrieve after GPU execution without confusing generation success with publication approval. Change Set 061 adds a compact tamper-evident evidence manifest around the existing GPU smoke output.

### Added
- `engine/intelligence/golden_evidence_bundle.py`
  - Validates the first-PNG result JSON.
  - Requires `publication_ready=false`.
  - Requires the referenced PNG to exist, be non-empty and carry the PNG signature.
  - Rejects evidence paths that escape the repository root.
  - Hashes every evidence file with SHA-256 and records byte size.
  - Emits deterministic schema `pul7sar-golden-gpu-evidence-v1` plus a canonical manifest SHA-256.
  - Does not calculate visual quality, semantic safety, identity similarity or publication approval.

- `tools/phase18_build_gpu_evidence_manifest.py`
  - Builds the manifest from the real first-PNG result.
  - Supports explicit additional receipts such as GPU qualification, model-cache readiness and local readiness evidence.
  - Writes the manifest under `output/phase18_gpu_smoke/` by default.

- `tests/test_phase18_golden_evidence_bundle.py`
  - Covers valid manifest construction and hashing.
  - Rejects `publication_ready=true`.
  - Rejects fake/non-PNG evidence.
  - Rejects repository-path escape.
  - Deduplicates repeated receipts.

### Workflow integration
The self-hosted GPU smoke workflow builds the evidence manifest only after a real PNG has passed existence/signature checks, before artifact upload. The uploaded artifact therefore contains both the raw proof files and a compact integrity index.

### Safety invariants
- No prompt, seed, canvas, provider/model ID or payload SHA is modified.
- No Fact Lock, identity, sentiment, semantic-publication or Golden-quality rule is weakened.
- `publication_ready` remains false after generation and after manifest creation.
- The manifest cannot substitute for semantic verification or the strict 8.5/9.0 Golden review.
- No paid provider/API, production secret, model weight or font file is introduced.
- `main` and production publishing remain untouched.

### Remaining blocker
A genuine PNG still requires a compatible NVIDIA CUDA/BF16 host to execute the already locked FLUX.2 Klein candidate. Change Set 061 does not fabricate a PNG; it ensures the first real result can be audited, hashed and retrieved cleanly when that host becomes available.
