# PUL7SAR Phase 18 — Change Set 160

## Canonical Runtime-Locked First-Golden Workflow

### Problem closed

Change Set 159 introduced a strict first-Golden wrapper that captures a canonical software-runtime fingerprint before Candidate 1, runs the existing sealed Golden staging path without repairing the environment a second time, captures the runtime again, and fails closed unless the two fingerprints match.

The canonical self-hosted GPU workflow still invoked `phase18_colab_first_golden_bootstrap.py` directly. That meant the preferred GitHub GPU path did not yet require the new pre/post runtime fingerprint contract even though the safer wrapper already existed.

### Change

`.github/workflows/phase18-first-golden-review.yml` now invokes:

`tools/phase18_colab_first_golden_runtime_locked.py`

instead of invoking the strict bootstrap directly.

The workflow then replays and verifies:

1. `pul7sar-first-golden-runtime-lock-v1`;
2. pre-run runtime fingerprint receipt;
3. post-run runtime fingerprint receipt;
4. identical `runtime_fingerprint_sha256` across the run;
5. zero authority on both fingerprint receipts;
6. the SHA/size of the strict-bootstrap receipt referenced by the runtime-lock receipt;
7. the existing bootstrap repository/cache/GPU/Qwen/sealed-review evidence;
8. the exact Base and Hybrid review PNG hashes;
9. exact binding between the runtime-lock result and the strict-bootstrap review PNG paths/hashes.

The workflow remains manual, self-hosted, immutable-SHA checked out, complete-ancestry verified, Phase-18-only, `$0-local`, CUDA/BF16-only, and unable to authorize human acceptance, Golden quality, publication, or Seeds 2–4.

### Added

- Change Set 160 documentation.
- Implementation Log 160.

### Modified

- `.github/workflows/phase18-first-golden-review.yml`
  - canonical GPU entrypoint changed to the runtime-locked wrapper;
  - runtime-lock receipt and pre/post fingerprint receipts are replayed before bootstrap evidence;
  - runtime/bootstrap Base+Hybrid PNG bindings are replayed before artifact upload.
- `tests/test_phase18_first_golden_review_workflow.py`
  - requires the runtime-locked wrapper;
  - requires runtime fingerprint replay before bootstrap evidence replay;
  - requires closed generation/semantic/Golden/publication authority on the fingerprint receipts;
  - requires runtime-to-bootstrap review-PNG binding;
  - keeps immutable source, main isolation, self-hosted GPU and zero-cost regression locks.

### Deleted

None.

### Gates preserved

No change to Fact Lock, Entity/Identity Verification, Sentiment/Neutrality, `$0-local`, immutable FLUX/Qwen revisions, native BF16, live free-VRAM qualification, Candidate/request/seed/canvas/SHA locks, generated text/branding/exact-fact/entity-mark/sport-geometry prohibitions, Qwen BASE_SCENE/HYBRID_SURFACE inspection, deterministic football geometry, provenance/evidence replay, Golden 8.5 minimum / 9.0+ elite thresholds, Exact Brand Integrity, Typography Integrity, SemanticPublicationGate, or final publication readiness.

No paid provider, hosted GPU fallback, fake PNG, fake benchmark, precision downgrade or automatic publication authority was introduced.
