# Phase 18 Implementation Log — CS502

## Scope
Repair the exact CPU validation regressions surfaced by CS501 without weakening any production, factual, identity, sentiment, zero-cost, semantic-publication, CUDA/native-BF16, PNG-integrity, Human Review, Golden-quality, publication, or Seeds 2–4 gate.

## Evidence reviewed
CS501 CPU diagnostics reported `PHASE18_CPU_VALIDATION_FAILED` at unittest discovery/execution with six errors:

1. `test_phase18_authoritative_first_golden_pre_generation_evidence_binding` could not import because `pytest` is not installed in the stdlib-only CPU verification environment.
2. `test_phase18_first_golden_preflight_evidence_binding` had the same unsupported `pytest` dependency.
3. Four existing `CanonicalFreshWrapperTests` reached the new CS500 immutable-binder Git proof with synthetic 40-character SHAs (`a*40` through `d*40`), causing expected `git ls-tree` failure before those tests could exercise their intended freshness/canonical semantics.

## Changes
### Modified
- `tests/test_phase18_authoritative_first_golden_pre_generation_evidence_binding.py`
  - Converted pytest fixtures/context managers to stdlib `unittest`, `tempfile`, and `unittest.mock.patch`.
  - Preserved all semantic rejection coverage: network SHA/guard drift, CUDA/native-BF16 failure, empty snapshot inventory, blocker not ready, branch drift, malformed SHA, authority closure, and exact evidence hashing.
- `tests/test_phase18_first_golden_preflight_evidence_binding.py`
  - Converted to stdlib-only unittest execution.
  - Preserved successful hashing/closed-authority checks and non-ready/branch/SHA rejection checks.
- `tests/test_phase18_first_golden_canonical_fresh_wrapper.py`
  - Isolated the new immutable-binder proof and pre-generation binder in tests whose purpose is freshness/canonical result semantics.
  - The production immutable proof is not removed or bypassed; dedicated CS500 activation/proof tests remain responsible for that gate.
  - Synthetic SHAs can no longer accidentally invoke real Git object lookup in unrelated wrapper tests.

### Added
- `docs/PHASE18_IMPLEMENTATION_LOG_502.md`

### Deleted
- None.

## Gate preservation
No production code or authoritative workflow was relaxed. The CS500 immutable binder proof remains in the real canonical-fresh wrapper before evidence binding, freshness capture, and Candidate 1. No paid API, model download, CPU generation fallback, FP16/FP32 substitution, publication shortcut, or semantic bypass was introduced.

## Test intent
The Phase 18 CPU validator uses `python -m unittest discover -v -s tests -p 'test_phase18_*.py'`; therefore Phase 18 regression tests must be executable without an undeclared pytest dependency. CS502 restores that contract while retaining the same assertions.

## Remaining execution gap
After CPU CI returns green, the first genuine Golden Visual PNG still requires a compatible self-hosted NVIDIA runner with CUDA-enabled PyTorch, a real CUDA device supporting native BF16, sufficient GPU/RAM/cache/filesystem headroom, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under the `$0-local` offline-only contract. No Golden PNG is claimed until that execution genuinely occurs and all downstream machine/evidence/Human Review gates pass.
