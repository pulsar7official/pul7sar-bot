# Phase 18 — Change Set 257: Atomic Fresh-Story Semantic Replay

## Purpose

Change Set 257 closes the remaining manual gap between Change Set 256 production-gate execution and the existing Change Set 237/238 fresh-story contracts. It is CPU-only and intentionally stops before controlled-trial/runtime generation authorization.

## Canonical flow

1. Re-open one exact Change Set 256 output inside the repository workspace.
2. Re-hash the CS256 evidence-pack receipt, every evidence file, and every production gate receipt.
3. Reconstruct Change Set 235 `fresh_story_evidence_manifest` from the exact current evidence bytes.
4. Reconstruct Change Set 236 `fresh_story_gate_verification_contract` against one common story snapshot SHA-256.
5. Execute Change Set 237 `build_fresh_story_gate_receipt_bundle` so all six receipts must be present, byte-bound, same-story, and within one explicit freshness window.
6. Execute Change Set 238 `build_fresh_story_gate_semantic_replay` with the canonical `GATE_REPLAY_VERIFIERS` registry.
7. Immediately call `verify_fresh_story_gate_semantic_replay`, which re-executes the six production semantics and requires `verification_details_sha256` equality.
8. Publish the staged output directory only after the full sequence succeeds.

## Authority boundary

A successful CS257 run may record only:

- `production_semantic_replay_executed = true`
- `fresh_story_gates_passed = true`

It must keep all later authorities false, including controlled-trial validity, canonical generation authorization, model loading, inference, genuine Golden PNG creation, semantic approval, human review, Golden quality approval, and publication readiness.

## Fail-closed checks

CS257 rejects source-run paths outside the repository, symlinked or missing evidence, evidence-pack byte drift, receipt-byte drift, gate-order drift, cross-story receipts, stale/future receipts through CS237/238, verifier-registry drift, verifier identity/version drift, semantic details drift, and any attempt to reuse an existing output directory.

## Golden PNG status

This change does not execute CUDA or Qwen-Image-2512. A genuine Golden PNG remains blocked until a compatible zero-cost runtime can prove NVIDIA CUDA, native BF16, sufficient live VRAM/RAM, the exact pinned Qwen revision, a compatible QwenImagePipeline, successful sequential CPU offload, and canonical `$0-local` execution on one runtime.
