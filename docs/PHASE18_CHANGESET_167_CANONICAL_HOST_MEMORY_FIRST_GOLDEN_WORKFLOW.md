# PUL7SAR Phase 18 — Change Set 167

## Canonical Host-Memory-Locked First-Golden Workflow

Change Set 166 added a fail-closed host-memory qualification step before model work, but the existing GitHub self-hosted first-Golden workflow still entered the runtime-locked path directly. That left a practical mismatch between the strict Colab path and the GitHub-controlled GPU entrypoint: a host could pass CUDA/VRAM/offload checks and only later discover that live system RAM was insufficient for sequential CPU offload.

Change Set 167 closes that gap without relaxing any publication, factual, identity, sentiment, zero-cost, semantic, or visual-quality gate.

### Added

- `.github/workflows/phase18-first-golden-review-host-memory.yml`
  - manual `workflow_dispatch` only;
  - immutable dispatched SHA and exact `phase18/story-intelligence` branch reattachment;
  - complete ancestry and `main.py` isolation proof;
  - self-hosted CUDA/BF16 labels only;
  - no hosted/paid GPU fallback and no PyTorch replacement;
  - delegates Candidate 1 to `phase18_colab_first_golden_host_memory_locked.py`;
  - replays SHA/size for the host-memory preflight and nested runtime-lock receipt;
  - verifies the exact Base and Hybrid PNG bytes presented for human review;
  - keeps human approval, Golden approval, publication readiness, and Seeds 2–4 authority closed.

- `tests/test_phase18_first_golden_host_memory_workflow.py`
  - locks manual/self-hosted/zero-cost behavior;
  - locks immutable source and main-isolation ordering;
  - requires host-memory qualification to wrap the runtime-locked Candidate 1 path;
  - requires host-memory/runtime/PNG replay before artifact upload;
  - prevents authority drift.

### Modified

None. This change is additive so the previously qualified canonical workflow remains intact while the host-memory-locked workflow becomes the preferred execution entrypoint for the next compatible GPU session.

### Deleted

None.

## Preserved gates

Unchanged and fail-closed:

- Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality;
- `$0-local` policy;
- pinned FLUX/Qwen revisions;
- native BF16;
- total/live-free VRAM gates;
- safe Diffusers offload qualification;
- live host-RAM qualification;
- runtime fingerprint stability;
- Candidate/request/seed/canvas/SHA locks;
- generated text/branding/exact facts/entity marks/sport-geometry prohibitions;
- Qwen `BASE_SCENE` and `HYBRID_SURFACE` gates;
- deterministic football geometry;
- provenance/evidence replay;
- Golden 8.5 minimum / 9.0+ elite thresholds;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate.

## Remaining blocker

A genuine Golden Hybrid v5 PNG still requires an actual execution host satisfying the complete local runtime contract: NVIDIA CUDA, native BF16, sufficient total and live-free VRAM, safe Diffusers offload capability, sufficient live system RAM, pinned model revisions, stable runtime fingerprint, and `$0-local` execution.

No PNG, score, benchmark, or visual success is fabricated by this change set.
