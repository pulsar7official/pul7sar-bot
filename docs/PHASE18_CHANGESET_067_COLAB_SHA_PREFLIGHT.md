# PUL7SAR Phase 18 — Change Set 067

## Colab CPU preflight + exact handoff SHA result provenance

Change Set 067 hardens the semi-automatic Colab loop before the next v2 Golden GPU spend. It does not change the approved FLUX.2 Klein model, BF16 policy, seed set, canvases, `$0-local` policy, factual/identity/sentiment logic, semantic publication gate, or Golden quality thresholds.

### Why this change exists

The v2 Visual Intelligence policy now intentionally changes the Golden prompt/composition grammar. A Colab checkout may still contain durable result JSON from an older prompt. Request ID and seed checks alone are not enough to prove that an existing PNG was generated from the exact current handoff bytes. The GPU executor therefore now persists the cryptographically verified handoff `payload_sha256` in every successful result, and the Colab runner requires that digest before it will reuse a result.

### Added / modified

- `tools/phase18_flux2_execute.py`
  - adds `_handoff_payload_sha256()`;
  - replays `LocalGenerationHandoff.read()` before exposing the supplied digest;
  - persists `payload_sha256` in `REAL_VISUAL_PROOF_GENERATED` result JSON.
- `tools/phase18_colab_runner.py`
  - runs a compact CPU-safe Golden regression preflight before GPU readiness/execution by default;
  - targeted modules cover unified-scene policy, Golden batch verification, FLUX handoff command integrity, and the Colab runner itself;
  - adds `--skip-targeted-tests` only as an explicit operator override;
  - strengthens result reuse to require status + request ID + seed + model ID + exact payload SHA-256 + `$0-local`;
  - legacy result JSON without the digest is never silently reused;
  - validates the same exact identity/SHA/cost contract immediately after a fresh GPU execution.
- `tests/test_phase18_flux2_execute_command.py`
  - verifies correct digest extraction and integrity replay on tampered handoffs.
- `tests/test_phase18_colab_runner.py`
  - verifies exact result reuse matching and rejection of stale/legacy/mismatched results.

### Deleted

Nothing.

### Safety invariants preserved

- branch remains locked to `phase18/story-intelligence`;
- `main`, `main.py`, Telegram publishing and legacy production image sourcing are untouched;
- no paid image API or provider is introduced;
- no model/dtype/canvas/seed downgrade is permitted;
- generation success still cannot imply semantic or publication readiness;
- identity-reference execution remains blocked until verified asset-path resolution exists.

### Remaining blocker

The next meaningful visual verdict requires a fresh v2 candidate-1 GPU run on the already proven Colab Tesla T4 (or another compatible CUDA/BF16 host). CPU/GitHub preparation cannot truthfully manufacture that PNG. The intended next Colab command is the branch-locked semi-automatic runner after pulling this change set; it will self-test, rebuild and verify the v2 batch, prove readiness, execute candidate 1, bind the result to the exact handoff SHA, and display the PNG.
