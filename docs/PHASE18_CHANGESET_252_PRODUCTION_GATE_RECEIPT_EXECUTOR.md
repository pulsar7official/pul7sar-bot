# Phase 18 Change Set 252 — Production Gate Receipt Executor

## Purpose

Change Set 252 closes the next non-GPU gap between the real six-verifier registry and Change Set 237/238 receipt replay. A valid fresh gate receipt can no longer be authored merely by asserting `gate_passed=true`; it is built only from the actual output of the canonical production verifier over the exact evidence bytes.

This remains CPU-only and fail-closed. It does not admit a six-gate receipt bundle, mark fresh story gates passed, authorize Qwen generation, load model weights, create pixels, approve quality, or publish.

## Production executor

`engine/intelligence/qwen_image_production_gate_receipt_executor.py` adds:

- `build_production_gate_receipt(...)` for one canonical gate;
- `build_production_gate_receipt_set(...)` for the exact six-gate order/set.

For each receipt, the executor:

1. requires a gate ID from `REQUIRED_FRESH_GATE_EVIDENCE`;
2. requires a valid common story snapshot SHA-256;
3. requires strict UTC evaluation time;
4. resolves the verifier only from `GATE_REPLAY_VERIFIERS`;
5. requires the verifier to be literally production-backed and bound to that gate;
6. reads the exact evidence bytes itself;
7. executes the real verifier using its declared verifier ID/version;
8. requires the replay output to have the exact production output shape;
9. independently compares story SHA, evidence SHA-256, byte size, verifier identity/version and `gate_passed`;
10. rejects missing/empty semantic verification details;
11. recursively rejects any attempt to smuggle semantic-replay, generation, Golden, review or publication authority through verification details;
12. hashes the actual semantic `verification_details` with `sha256_json(...)`;
13. returns exactly the Change Set 236 `REQUIRED_GATE_RECEIPT_FIELDS` in canonical order.

The resulting `verification_details_sha256` is the value Change Set 238 later checks by re-executing the same production verifier against the same byte-bound evidence.

## Six-gate set boundary

The set builder requires the evidence mapping keys to equal the six required gates in the exact canonical order. Missing, extra or reordered evidence fails before semantic execution.

This does not weaken Change Set 237 freshness checks; the produced receipts still have to be admitted within the configured maximum age, on one common story snapshot, against the byte-bound verification contract.

## Regression coverage

`tests/test_phase18_qwen_image_production_gate_receipt_executor.py` covers:

- execution of the real `zero_cost_policy` production verifier to create a valid receipt;
- independent evidence SHA-256/byte-size binding;
- exact Change Set 236 receipt field order;
- rejection of invalid zero-cost evidence instead of manufacturing a passing receipt;
- rejection of cross-story evidence;
- strict UTC evaluation timestamps;
- rejection of unknown gate IDs;
- exact six-gate set/order requirement;
- recursive rejection of malicious authority fields embedded in verifier details;
- confirmation that all six canonical registry entries remain production-backed and gate-bound.

## Authority boundary

A successfully built individual receipt means only that one production verifier passed one exact evidence file at one evaluation time. It does not make any of the following true:

- `production_semantic_replay_executed`
- `fresh_story_gates_passed`
- `controlled_trial_preflight_valid`
- `canonical_generation_authorized`
- `model_weights_loaded`
- `inference_executed`
- `genuine_golden_png_created`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`

## Remaining path

The next non-GPU milestone is to supply one genuine, source-backed, same-story six-evidence set, execute Change Set 252 over all six files, admit the fresh receipts through Change Set 237, and then run Change Set 238 semantic replay. No synthetic/study fixture may be promoted as genuine story evidence.

The genuine Golden PNG remains separately blocked on a compatible `$0-local` CUDA/BF16 Qwen-Image-2512 runtime.
