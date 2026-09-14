# Phase 18 Implementation Log — CS458 First-Golden Freshness Guard

## Scope

Branch: `phase18/story-intelligence` only. `main` was not modified.

Starting HEAD: `f0511a6c8f06094aeb18be54c452664a711eba2d` (CS457).

CS457 central `Phase 18 Story Intelligence Verification` was confirmed successful before this change set.

## Problem closed

The canonical output replay added in CS457 proves that the resource-lock receipt and PNG are internally coherent after generation. A remaining execution risk was stale-success evidence: mutable files from an earlier attempt (`latest.json`, semantic receipt, staging receipt, resource-lock receipt) could already exist on a persistent self-hosted runner. A future execution path needs a deterministic way to prove that those mutable receipts were created or refreshed by the current attempt rather than merely rediscovered after a nominally successful command.

## Added

### `tools/phase18_first_golden_freshness_guard.py`

CPU-safe, network-free two-phase freshness contract:

- `capture --output <baseline>` records pre-attempt existence, SHA-256, byte count and `mtime_ns` for the four mutable Candidate 1 receipts.
- `verify --baseline <baseline> --output <verification>` requires every receipt to be present and created/changed relative to the baseline.
- The post-attempt replay additionally requires staging and resource-lock receipts to reference the same repository-contained PNG and verifies its PNG signature and SHA-256 against both receipts.
- The tool never performs generation, model loading/download, workflow dispatch, queue mutation, publication, or Seeds 2–4 authorization.
- `$0-local`, offline-only and closed authority declarations remain explicit in both baseline and verification payloads.

Tracked mutable receipts:

1. `output/phase18_colab/latest.json`
2. `output/phase18_visual_proof/editorial/candidate-01-golden-editorial-v6-receipt.json`
3. `output/phase18_visual_proof/editorial/candidate-01-first-genuine-golden-staging.json`
4. `output/phase18_gpu_smoke/first-genuine-golden-v6-resource-lock.json`

### `tests/test_phase18_first_golden_freshness_guard.py`

Regression coverage for:

- fresh post-attempt evidence accepted with authority remaining closed;
- unchanged pre-existing receipts rejected as stale;
- staging/resource-lock PNG path drift rejected;
- baseline generation-authority drift rejected.

## Modified

None.

## Deleted

None.

## Local test executed before repository write

```text
python -m unittest discover -s tests -p 'test_phase18_first_golden_freshness_guard.py' -v
```

Result: 4 tests run, all passed.

## Preserved gates

No changes were made to factual verification, identity/entity verification, sentiment/loser-respect policy, SemanticPublicationGate, Human Review / visual-quality approval, Candidate 1 prompt/seed/dimensions/steps/guidance, approved Qwen2.5-VL or FLUX.2 identities/revisions, native-BF16 policy, CUDA qualification, `$0-local`, offline-only resolution, publication authority, or Seeds 2–4 authority.

## Remaining work

The freshness guard is deliberately standalone in CS458 so its contract is independently testable before wiring it into the authoritative GPU workflow/canonical launcher. The next safe integration step is to capture the baseline immediately before Candidate 1 generation and replay it immediately after canonical output generation, then retain both receipts as evidence.

The actual First Genuine Golden Visual PNG remains blocked until a compatible self-hosted NVIDIA execution host is available with CUDA-enabled PyTorch, a real CUDA device, native BF16, sufficient live VRAM/RAM/cache headroom, compatible runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under `$0-local` and offline-only policy. No PNG is claimed by this change set.
