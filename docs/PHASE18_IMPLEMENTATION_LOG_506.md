# Phase 18 Implementation Log — CS506

## Scope
Branch: `phase18/story-intelligence` only. `main` was not modified.

## State reviewed
CS505 HEAD was `72df011f61fd858710eedbddf3e5ac74a0e69e60`. Story Intelligence Verification #6124 and CPU Verification Diagnostics #309 both completed successfully on that exact SHA. During the live-path review, the repository was inspected beyond the older `phase18-first-genuine-golden-v6.yml` workflow.

## Material finding
A separate live workflow, `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml`, already exists and is the freshness-bound Candidate-1 path. It is restricted to `phase18/story-intelligence`, runs only on the self-hosted NVIDIA/CUDA/BF16 Phase-18 runner labels, enforces `$0-local` plus both offline model flags, captures the zero-cost network guard, execution-blocker probe, approved snapshot inventory, and immutable runner/CUDA identity before Candidate 1, and then invokes `tools/phase18_run_first_genuine_golden_v6_canonical_fresh.py` rather than the older direct canonical-attested launcher.

This corrects the narrower CS505 remaining-note: the older authoritative workflow still calls canonical-attested directly, but a live freshness-bound workflow is already present. Rewriting the older 30KB workflow is therefore not required to obtain a freshness-bound first genuine Candidate 1; doing so would add unnecessary risk while the dedicated fresh workflow already preserves the stronger path.

## Added
- `tests/test_phase18_live_fresh_workflow_activation.py`
- this implementation log

## Modified
None.

## Deleted
None.

## Tests added
Stdlib `unittest` regression coverage locks the live fresh workflow to:
1. the exact `phase18/story-intelligence` branch and self-hosted GPU/CUDA/BF16 labels;
2. `$0-local`, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and native-BF16 with no FP16/FP32 substitution;
3. capture of all four authoritative pre-generation evidence files before Candidate 1;
4. invocation of the freshness-bound canonical launcher, with no earlier direct canonical-attested invocation;
5. continued presence of source-bound artifact, PNG structure/chunk/canonical-encoding, review-bundle, Human Visual Review, Golden-quality, publication, and Seeds 2-4 gates.

## Gate preservation
No production generator, model, workflow, factual/source-consensus, identity/entity, sentiment/loser-respect, semantic-publication, zero-cost, PNG, Human Review, Golden-quality, publication, or Seeds authority was weakened or changed. This change only adds a regression lock around the already-existing stronger live workflow.

## Remaining
The first genuine Golden Visual PNG still requires actual execution of the dedicated fresh workflow on a compatible self-hosted NVIDIA runner with CUDA-enabled PyTorch, at least one CUDA device with native BF16, sufficient GPU/RAM/cache/filesystem headroom, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally. No model download, paid API, CPU generation fallback, FP16/FP32 substitution, or fabricated PNG is permitted. CS506 itself must pass CPU CI before it is considered terminal-green.
