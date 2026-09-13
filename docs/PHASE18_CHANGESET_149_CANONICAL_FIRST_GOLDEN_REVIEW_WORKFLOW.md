# Phase 18 Change Set 149 — Canonical First Golden Review Workflow

## Purpose

Provide one explicit self-hosted GitHub Actions entrypoint for the first genuine Golden Hybrid v5 Candidate 1 that uses the already-hardened strict bootstrap and Original Scene path all the way to the SHA-sealed human-review packet.

This change does not replace FLUX.2 Klein 4B, does not introduce a hosted or paid GPU, and does not bypass any semantic, factual, identity, neutrality, visual-quality, branding, typography or publication gate.

## Gap closed

The branch already contained two mature pieces:

1. the older `phase18-gpu-smoke.yml`, which exposes each GPU/provenance/semantic stage individually;
2. `phase18_colab_first_golden_bootstrap.py`, which is now the stricter canonical orchestration path because it includes repository/reference integrity, exact runtime repair, shared Qwen+FLUX cache budgeting, exact Qwen prefetch, Original Scene runtime admission, Candidate 1 generation/provenance, BASE_SCENE QA, deterministic football Hybrid, HYBRID_SURFACE QA, and SHA-sealed human-review staging.

A dedicated GitHub workflow did not yet invoke that complete strict orchestration path as a single operation. That meant the safest Colab path and the easiest self-hosted GitHub path were not the same operational contract.

## Added

### `.github/workflows/phase18-first-golden-review.yml`

A manual-only workflow that:

- requires the exact confirmation token `RUN_PHASE18_FIRST_GOLDEN_REVIEW`;
- checks out only `phase18/story-intelligence`;
- runs only on `[self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]`;
- refuses to install or replace PyTorch automatically;
- invokes `tools/phase18_colab_first_golden_bootstrap.py` as the canonical strict Candidate 1 entrypoint;
- requires the `pul7sar-first-golden-colab-bootstrap-v2` receipt;
- replays SHA-256 and byte-size evidence for repository integrity, shared cache budget, Qwen model cache and the sealed human-review receipt;
- replays SHA-256 for the exact Base and Hybrid PNGs presented for human review;
- keeps human approval, Golden approval, publication authority and Seeds 2–4 authorization false;
- uploads the complete Phase 18 GPU/review evidence bundle for inspection.

### `tests/test_phase18_first_golden_review_workflow.py`

Regression coverage proving that the new workflow:

- is manual-only and Phase-18-only;
- requires the self-hosted CUDA/BF16 label set;
- uses the strict Original Scene → sealed review orchestration path;
- does not install PyTorch or reference paid-provider secrets;
- replays all bootstrap evidence and both review-image hashes;
- cannot grant Human, Golden, Publication or Seeds 2–4 authority;
- uploads artifacts only after the strict bootstrap and evidence replay.

## Modified

None. This change is additive so the established GPU smoke workflow remains available as a verbose engineering path while the new workflow becomes the preferred single-entrypoint path for the first real Golden review packet.

## Deleted

Nothing.

## Gates preserved

No change was made to:

- Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality;
- `$0-local` execution policy;
- FLUX.2 Klein 4B selection;
- native BF16 requirement;
- Candidate/request/seed/canvas/SHA locks;
- generated text/branding/exact-fact/entity-mark/sport-geometry exclusions;
- Original Scene runtime admission;
- Qwen BASE_SCENE and HYBRID_SURFACE inspection;
- deterministic football geometry;
- first-PNG provenance and evidence replay;
- Golden 8.5 minimum / 9.0+ elite thresholds;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate;
- final Publication Readiness.

The workflow intentionally stops at the sealed Candidate 1 human-review packet. It never fills the human decision, never assigns a Golden score, never enables Seeds 2–4, and never publishes.

## Genuine PNG status

This change does not claim a new Golden Hybrid v5 PNG. A genuine result still requires an actual self-hosted NVIDIA CUDA + native-BF16 machine capable of running the locked FLUX.2 Klein 4B and Qwen path.
