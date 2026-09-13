# Phase 18 Change Set 271 — One-Shot Composition Execution

## Purpose

CS271 closes the execution gap after CS270. A READY CS270 receipt proves that the deterministic composition inputs are byte-bound and executable, but it does not consume an execution attempt or bind the composed pixels that a renderer produces.

CS271 introduces a one-shot execution boundary that:

1. re-verifies the exact CS270 receipt;
2. reopens the exact candidate PNG;
3. binds the project-native runner source file by repository path, SHA-256, and byte size;
4. consumes the composition attempt **before** the runner is called;
5. allows a maximum of one render attempt for that output directory/preflight use;
6. requires a PNG output and preserves the candidate canvas dimensions when dimensions are known;
7. binds the composed PNG by repository path, SHA-256, byte size, width, and height;
8. keeps all semantic, human-review, Golden, brand-quality, and publication authorities closed.

## Authority model

A successful CS271 receipt may state only:

- `composition_executed = true`

It must continue to state:

- `composed_visual_approved = false`
- `semantic_approved = false`
- `human_visual_review_approved = false`
- `genuine_golden_png_created = false`
- `golden_quality_approved = false`
- `publication_ready = false`

Therefore a composed PNG is only a byte-bound post-composition candidate. It is not a Golden Visual.

## One-shot failure semantics

The consumption receipt is written and fsynced before the runner is invoked. If the runner raises, emits no file, emits a non-PNG, or changes the canvas dimensions, the attempt remains consumed. The same output directory cannot be silently reused for retries.

This mirrors the one-shot generation philosophy already used upstream: retries require a new explicitly authorized attempt rather than an invisible loop until an aesthetically preferred result appears.

## Runner boundary

CS271 intentionally accepts a runner callable at the Python library boundary while requiring its source file to be repository-byte-bound. This lets the existing PUL7SAR renderer/composition stack be integrated without duplicating rendering business logic inside the intelligence gate.

The included CLI is verifier-only. It does not invent or dynamically import a renderer from an arbitrary user-supplied module path.

## Verification

`verify_one_shot_composition_execution()` reopens and re-verifies:

- the exact CS270 receipt;
- the exact original candidate bytes;
- the exact runner source bytes;
- the exact attempt-consumption bytes;
- the exact composed PNG bytes and dimensions.

Any byte drift invalidates the receipt.

## Remaining path

After a genuine CS271 execution, the next safe stages are:

1. exact composed-PNG admission;
2. post-composition semantic/layer QA;
3. identity continuity check where required;
4. Visual Critic;
5. Human Review;
6. Golden threshold enforcement;
7. exact Brand/Typography verification;
8. SemanticPublicationGate.

The upstream Qwen generation path remains blocked in environments without compatible CUDA/BF16 execution. CS271 does not fabricate a candidate or composed image in that situation.
