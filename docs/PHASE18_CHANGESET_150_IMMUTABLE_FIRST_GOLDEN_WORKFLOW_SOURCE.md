# PUL7SAR Phase 18 — Change Set 150

## Immutable First-Golden Workflow Source

### Problem

The canonical self-hosted first-Golden workflow introduced in Change Set 149 checked out the moving branch name `phase18/story-intelligence`. On a scarce GPU run, the branch could move after `workflow_dispatch` but before checkout, causing the runner to execute code different from the commit that triggered the run. The old main-isolation check also used a shallow checkout and suppressed comparison errors, which meant a missing `origin/main`/merge-base could silently skip the `main.py` protection.

### Change

`.github/workflows/phase18-first-golden-review.yml` now:

- requires `github.ref` to equal `refs/heads/phase18/story-intelligence` before any GPU work;
- validates that `github.sha` is a full 40-character commit SHA;
- checks out the immutable `${{ github.sha }}` instead of the moving branch ref;
- verifies `git rev-parse HEAD` equals the dispatched SHA;
- fetches `main` read-only with sufficient history for an explicit merge-base;
- fails closed if a merge-base cannot be established;
- checks the merge-base-to-dispatched-commit diff for `main.py` without suppressing Git errors;
- preserves all existing CUDA/BF16, `$0-local`, Original Scene, Qwen, FLUX, provenance, semantic, human-review and publication gates.

### Regression coverage

`tests/test_phase18_first_golden_review_workflow.py` now locks:

- dispatch-ref equality to the Phase 18 branch;
- immutable SHA checkout;
- HEAD-to-dispatch-SHA equality;
- explicit read-only `main` fetch and merge-base establishment;
- fail-closed `main.py` isolation without the previous stderr-suppressed comparison.

### Safety

No generation model, prompt, seed, canvas, precision rule, Fact Lock, Identity gate, Sentiment/Neutrality gate, Qwen semantic gate, Golden score threshold, brand/typography integrity rule, or publication gate was changed.

No file was deleted. `main` was not modified.
