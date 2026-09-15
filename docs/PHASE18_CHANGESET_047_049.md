# PUL7SAR Phase 18 — Change Sets 047–049

## Purpose
This document records the Phase 18 changes made after the first verified Golden Visual batch became transport-ready. The focus of these change sets is not adding more abstract architecture; it is tightening the actual visual benchmark and making the first real GPU execution path more reliable.

Production remains isolated. `main.py`, current Telegram publishing, and legacy image sourcing/rendering are not modified by these changes.

---

## Change Set 047 — Strict Golden Visual approval floor

### Modified files
- `engine/intelligence/golden_visual_quality.py`
- `tests/test_phase18_golden_visual_quality.py`
- `tools/phase18_review_golden_batch.py`
- `tests/test_phase18_review_golden_batch.py`

### What changed
The previous Golden Visual acceptance threshold was too permissive for the stated PUL7SAR goal. A technically clean image with a weighted score around the high-7/low-8 range could previously be accepted. That did not match the project requirement that the automated result should equal or exceed the strongest manually produced visual direction.

The quality contract now defines three explicit constants:

- `GOLDEN_WEIGHTED_FLOOR = 8.5`
- `GOLDEN_CORE_FLOOR = 8.0`
- `ELITE_TARGET = 9.0`

A candidate is approved only if:

1. It has no hard visual blocker.
2. Its weighted score is at least `8.5/10`.
3. Each critical core dimension — editorial realism, composition hierarchy, and protected-zone cleanliness — is at least `8.0/10`.

A candidate with a weighted score of `9.0+` is classified as `elite`.

Any hard blocker forces the result to `below_golden`, regardless of the numeric score. Hard blockers include fantasy/monumental staging, fake logos/crests, pseudo-text, invented results, cluttered collage treatment, and broken geometry/anatomy.

### Why it exists
The purpose is to prevent the system from confusing “generation succeeded” with “PUL7SAR-quality visual succeeded.” The visual engine is allowed to reject every candidate if none reaches the desired bar.

### Review output changes
`tools/phase18_review_golden_batch.py` now reports `quality_tier` for both ranked candidates and the selected candidate:

- `below_golden`
- `golden`
- `elite`

### Verification
The tests explicitly prove that:

- an `8.2` uniform candidate is rejected;
- an `8.6` candidate can pass the strict Golden floor;
- a `9.0+` candidate is classified as elite;
- a high-scoring candidate with a hard blocker is still rejected;
- the selector chooses the strongest approved candidate rather than the highest blocked candidate.

CI Run `32595997677`: SUCCESS after strict quality-floor integration.

---

## Change Set 048 — Durable real-GPU executor result channel

### Modified files
- `tools/phase18_flux2_execute.py`
- `tools/phase18_flux2_batch_execute.py`
- `tests/test_phase18_flux2_batch_execute.py`

### Problem addressed
The original batch executor parsed the single-request executor's stdout as JSON. That is safe in a mocked test environment but is fragile on a real GPU runtime because Diffusers, Transformers, Hugging Face model loading, CUDA, or dependency warnings may emit progress/informational text to the process streams.

A real image could therefore be generated successfully while the batch controller failed simply because stdout was not pure JSON.

### What changed
`tools/phase18_flux2_execute.py` now exposes an `execute_request(...)` function and accepts:

```text
--result <path>
```

When supplied, the executor writes the final structured result to that dedicated JSON file in addition to printing the human-readable JSON result.

The batch executor now:

1. Creates a temporary private result directory.
2. Delegates each candidate to the same single-request executor.
3. Passes a unique `--result` path.
4. Reads the dedicated JSON file instead of parsing stdout.
5. Validates status, seed, and request identity.
6. Fails closed if the result file is missing or malformed.

Temporary orchestration result files are removed automatically when the batch completes.

### Why it exists
This keeps machine state deterministic even when the underlying model runtime is noisy. It is a reliability change specifically for real GPU execution, not a cosmetic refactor.

### Verification
Tests prove that:

- candidate results remain valid even when stdout contains arbitrary progress text;
- missing executor result files fail closed;
- unexpected seeds fail closed;
- candidates still execute sequentially.

CI Run `32596095005`: SUCCESS after the durable result-file path was integrated.

---

## Change Set 049 — Production-equivalent first-candidate GPU smoke proof

### Modified files
- `tools/phase18_flux2_batch_execute.py`
- `tests/test_phase18_flux2_batch_execute.py`
- `notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb`
- `tests/test_phase18_colab_notebook.py`
- `docs/ZERO_COST_VISUAL_PROOF_RUNBOOK.md`

### What changed
The sequential batch executor now accepts:

```text
--limit N
```

The intended first real GPU proof uses:

```text
--limit 1
```

This executes only candidate 1 while preserving the original four-candidate manifest unchanged.

The first proof therefore no longer uses a separate ad-hoc command path. Candidate 1 is executed through the same batch orchestration that will later execute candidates 2–4.

The generated partial report records:

- `candidate_count`
- `execution_scope = "partial"`
- `requested_limit`
- candidate seed/request ID
- PNG path
- provenance metadata path
- native PNG path

Invalid limits (`0`, negative values, or values larger than the manifest candidate count) fail closed.

### Colab changes
`notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb` now performs this exact sequence:

1. Prove an NVIDIA GPU exists with `nvidia-smi`.
2. Clone the isolated `phase18/story-intelligence` branch.
3. Install only `requirements-phase18-gpu.txt`.
4. Run FLUX-specific local readiness.
5. Build the deterministic four-candidate Golden batch.
6. Cryptographically verify the batch before model loading.
7. Execute candidate 1 using `phase18_flux2_batch_execute.py --limit 1`.
8. Read `first-candidate-execution.json` rather than guessing output paths.
9. Confirm exactly one real candidate was produced.
10. Display the real PNG.
11. Keep full four-candidate execution opt-in until the first proof establishes runtime stability.
12. Provide the later Golden review-template and quality-selection commands.

The notebook also states the actual visual bar: weighted `8.5+`, core dimensions `8.0+`, and `9.0+` as the elite target.

### Why it exists
The first real GPU attempt should prove the entire final execution route with minimum runtime expenditure. If candidate 1 cannot load, generate, normalize, register, and display correctly, there is no reason to spend time generating seeds 2–4.

### Verification
Tests confirm that:

- `--limit 1` executes only the first locked candidate;
- the manifest is not changed;
- invalid limits are rejected;
- the Colab notebook contains readiness, batch build, integrity verification, first-candidate batch execution, partial report handling, and the strict visual review stage.

---

## Architecture after Change Set 049

```text
Article
 -> Story Intelligence
 -> Fact / Identity / Sentiment / Neutrality
 -> Visual Family / Concept Director
 -> Generation Authorization
 -> Platform Profile / Layout / Assets
 -> Generation Package
 -> $0-local Policy
 -> SHA-256 Golden Handoff
 -> Four Deterministic Seeds
 -> Batch Integrity Verification
 -> FLUX-specific CUDA/Diffusers Readiness
 -> Sequential Batch Executor
 -> --limit 1 First GPU Smoke Proof
 -> Dedicated Executor Result JSON
 -> Native FLUX PNG
 -> Exact Platform Canvas Normalization
 -> Real Visual Proof + Provenance
 -> Full Four-Candidate Batch
 -> Semantic Publication Gates
 -> Human/Visual Golden Review
 -> Strict 8.5 Golden Floor / 9.0 Elite Target
 -> Quality-First Selection
 -> Deterministic PUL7SAR Post-Composition
 -> Typography / Final Export
```

## Production and cost safety
Through Change Set 049:

- `$0-local` remains mandatory for current development.
- No paid image API is connected.
- No payment method is required by Phase 18 code.
- No production secret is added.
- No username/password is stored in source code.
- No model weights are committed to GitHub.
- GitHub CPU CI does not pretend to have generated an image.
- `main.py` remains untouched.
- Existing publishing remains untouched.
- A missing or mediocre image is rejected rather than silently promoted.

## Current real-world blocker
The code path for the first proof is ready and tested, but a real PNG still requires execution on a compatible CUDA runtime. Until that happens, PUL7SAR must continue to report the first Golden Visual as **not yet generated**, even though the request, integrity, runtime, batch and quality-control paths are ready.
