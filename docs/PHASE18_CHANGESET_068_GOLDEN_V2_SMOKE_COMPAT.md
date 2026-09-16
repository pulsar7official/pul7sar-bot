# PUL7SAR Phase 18 — Change Set 068

## Golden v2 smoke-path compatibility and regression repair

Change Set 068 repairs the remaining v1 assumptions discovered by the full CPU CI after the Golden Visual benchmark moved to v2. The failure was a test/runtime compatibility regression, not a weakening of the new unified-scene Visual Intelligence policy.

### What CI exposed

GitHub Actions Run `32629494120` executed 374 Phase 18 tests. Most passed, including all new unified-scene and Change Set 067 SHA-binding tests, but the run ended with 3 failures and 5 errors because two older components still assumed `pul7sar-golden-batch-v1`:

- `engine/intelligence/golden_smoke.py` rejected the new v2 manifest before it could apply SHA/cost/request checks.
- `tests/test_phase18_golden_batch.py` still asserted the old v1 manifest version.
- `tests/test_phase18_golden_smoke.py` still expected the old v1 request ID.

### Modified

- `engine/intelligence/golden_smoke.py`
  - accepts the explicitly supported v1 and v2 Golden manifest versions;
  - requires `single_continuous_scene` for v2;
  - requires the v2 unified-scene prompt marker before candidate 1 can enter the durable smoke queue;
  - preserves SHA-256, request ID, seed, model identity and `$0-local` checks.
- `tests/test_phase18_golden_batch.py`
  - updates the expected manifest to `pul7sar-golden-batch-v2`;
  - verifies the v2 composition grammar and unified-scene prompt marker.
- `tests/test_phase18_golden_smoke.py`
  - updates the deterministic candidate-1 request ID to `golden-general-season-opener-v2-001`;
  - adds a fail-closed test for v2 composition-grammar drift;
  - retains SHA drift, cost drift, durable job identity and bounded terminal-failure coverage.
- `tools/phase18_colab_runner.py`
  - expands the default CPU-safe preflight to include Golden batch and Golden smoke regressions in addition to unified-scene, batch verification, handoff-integrity and Colab-runner checks.

### Added / deleted

- Added this documentation file.
- No runtime source file was deleted.
- No test file was deleted.

### Verification

GitHub Actions Run `32629634107` completed successfully after the core repair. The later Run `32629719529` also completed successfully after the expanded Colab preflight was committed. The final run passed:

- Phase 18 syntax checks;
- the complete Phase 18 intelligence test suite;
- production-isolation verification;
- Golden v2 single-handoff build;
- Golden v2 four-candidate batch build;
- Golden v2 batch-integrity verification;
- handoff and candidate artifact upload.

The visual-proof upload step remained skipped because this CPU CI run correctly does not fabricate a GPU PNG.

### Safety invariants preserved

- `main`, `main.py`, Telegram publishing and the legacy production image path remain untouched.
- No paid provider, paid API, secret or model-weight artifact is introduced.
- FLUX.2 Klein, BF16, locked canvases, deterministic seeds and `$0-local` remain unchanged.
- Fact, identity, sentiment, neutrality, semantic-publication and strict Golden-quality gates remain fail-closed.
- v1 compatibility is retained only for historical evidence; v2 requires the stricter unified-scene grammar.

### Remaining gap

The software path is now green for v2 preparation. The next irreducible step is a fresh v2 candidate-1 execution on the proven Colab Tesla T4 or another compatible CUDA/BF16 host. Until that happens, PUL7SAR has a genuine v1 technical PNG but no genuine v2 unified-scene Golden candidate PNG, and no v2 visual-quality claim is valid.
