# Phase 18 Implementation Log — CS496

## Scope
First-Golden preflight evidence binding on `phase18/story-intelligence` only. `main` was not modified.

## Baseline reviewed
- Branch baseline: CS495 `3436af77da9a34fdbe47cb1f2b5fda5079a92980`.
- CS495 was confirmed identical to the branch head before this change set.
- Recent Phase 18 Actions for the CS495 SHA were completing successfully.
- Existing preflight-only workflow already enforced self-hosted NVIDIA/CUDA/BF16 labels, `$0-local`, offline mode, immutable dispatch SHA, exact branch isolation, snapshot inventory, blocker probing, probe-step outcome validation, and diagnostics-only artifact upload.

## Material gap
A successful preflight produced four separate diagnostics, but there was no single manifest cryptographically binding those exact bytes to the immutable dispatch source SHA. This left avoidable ambiguity when carrying a green preflight result forward to the later authoritative Candidate 1 execution.

## Added
### `tools/phase18_bind_first_golden_preflight_evidence.py`
- Requires exact `phase18/story-intelligence` branch and a 40-character lowercase source SHA.
- Requires the zero-cost network guard, runner identity, approved snapshot inventory, and execution-blocker evidence files.
- SHA-256 hashes and records the byte size of each required evidence file.
- Re-validates blocker schema, exact required branch, zero blockers, ready status, and closed authority fields.
- Emits an evidence-only manifest with generation, Human Review, Golden, publication, and Seeds 2–4 authority all explicitly false.
- Rejects repository-path escape for evidence and output.

### `tests/test_phase18_first_golden_preflight_evidence_binding.py`
Regression coverage for:
- successful four-file binding and closed authority;
- rejection of a non-ready blocker report;
- rejection of branch drift and malformed source SHA.

## Modified
### `.github/workflows/phase18-first-golden-preflight-only.yml`
- Added the binder to immutable tracked-source presence checks.
- After readiness succeeds, creates `preflight-evidence-binding.json` from the four exact preflight evidence files and `${{ github.sha }}`.
- Existing `if: always()` diagnostics upload remains unchanged, so failed hosts still retain raw blocker diagnostics even though only a successful preflight can produce the binding manifest.

## Deleted
None.

## Preserved gates
No factual/source-consensus, identity/entity, sentiment/loser-respect, zero-cost/network isolation, semantic-publication, model/runtime provenance, CUDA/native-BF16, PNG structural/chunk-semantic/canonical, Human Visual Review, Golden-quality, publication, or Seeds 2–4 authority was weakened. No paid API, model download, CPU generation fallback, FP16 fallback, or FP32 fallback was added.

## Testing status
The new pure-Python regression tests were added to the repository test suite. GitHub Actions on the resulting branch commits are the authoritative CI execution for this connector-driven change set; do not claim terminal-green until those runs complete successfully.

## First genuine Golden PNG status
Not generated in this change set. No GPU result is fabricated.

## Exact remaining external blocker
A compatible self-hosted NVIDIA runner must be online with CUDA-enabled PyTorch, a real CUDA device supporting native BF16, sufficient GPU/host/cache/filesystem headroom, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under `$0-local`/offline-only constraints.

## Next step
After CS496 CI is green, run the preflight-only workflow on the compatible NVIDIA host. Only a zero-blocker preflight with a source-bound evidence manifest should precede the authoritative Candidate 1 workflow. If the host is unavailable or incompatible, retain the exact diagnostics and do not fabricate a Golden PNG.
