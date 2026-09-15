# Phase 18 Implementation Log — Change Set 218

## Branch isolation

Target branch: `phase18/story-intelligence` only.

State reviewed before writing:
- Phase 18 HEAD: `1f2de3c5da242d4acefd7d2bc48bf9f099d4cb0b`
- `main` HEAD: `813ef31d2647e4353ca604e60e48975c79d7d95e`
- compare state: `diverged`
- Phase 18 ahead of `main`: 1820 commits
- Phase 18 behind `main`: 208 commits

No file was written to `main`; no merge, force-update, or `main.py` modification was performed.

## Baseline CI evidence

Story Intelligence Verification run `33110446398` completed with `failure` on Phase 18 HEAD `1f2de3c...`.

The job reached `Syntax and discover validation`, ran 1,411 Phase 18 tests, and had exactly one failure:

`test_missing_safety_marker_fails_closed (test_phase18_remote_renderer_benchmark.RemoteRendererBenchmarkTests)`

All other remote-renderer isolation tests passed, including:
- platform-name leak rejection;
- non-PNG rejection;
- SHA-bound PNG evidence;
- canonical-Golden/publication authority closure; and
- `$0-remote-zerogpu-study` separation from `$0-local`.

### Root cause

The benchmark prompt contains lowercase `no sponsor mark`.

The failing test attempted:

`safe.replace("No sponsor mark", "Avoid commercial marks")`

Because `str.replace()` is case-sensitive, the fixture was not changed. `_validate_prompt()` therefore correctly found the required lowercase marker and did not raise. The test failed because its mutation was ineffective, not because the production safety validator had become permissive.

## Implemented change

Commit `e6387d74aed26e8cb550b3c922e8751edb2bb148` modified only:

`tests/test_phase18_remote_renderer_benchmark.py`

The repaired regression now:
- asserts the required lowercase marker exists in the canonical prompt;
- removes exactly `no sponsor mark` once;
- asserts the mutation actually changed the prompt;
- asserts the safety marker is absent after mutation; and
- then requires `REMOTE_RENDERER_SAFETY_MARKER_MISSING`.

Production runtime code was intentionally left unchanged because `_validate_prompt()` was already fail-closed and correct.

## Documentation

Added:
- `docs/PHASE18_CHANGESET_218_REMOTE_RENDERER_SAFETY_MARKER_REGRESSION_REPAIR.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_218.md`

Deleted:
- none

## Gates preserved

No policy or quality threshold changed. The following remain fail-closed:
- Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality and respectful loser treatment;
- canonical `$0-local` Golden execution policy;
- protected Generated Text / Branding / Exact Facts / Entity Marks / Exact Sport Geometry exclusions;
- pinned/model/runtime evidence on canonical paths;
- Semantic and Layer Ownership gates;
- byte-bound Visual Critic hard failures;
- explicit Human Review;
- Golden quality floor 8.5 and 9.0+ elite target;
- Exact Brand Integrity;
- Typography Integrity; and
- SemanticPublicationGate.

Remote renderer study authority remains explicitly closed:
- `$0-remote-zerogpu-study`;
- engineering benchmark only;
- not canonical-Golden eligible;
- no semantic approval;
- no Golden approval;
- no publication readiness.

## Test status for Change Set 218

The known single CI failure was repaired and pushed to `phase18/story-intelligence`. A new GitHub Actions cycle is expected/started by the branch update; final CI success must be verified from the resulting Story Intelligence Verification run before this change set is called CI-green.

No test result is fabricated in this log.

## Golden Visual progress / remaining blocker

No new accepted canonical Golden Visual PNG was generated in this change set.

The repository already contains genuine visual attempts that were rejected; the target remains the first **accepted** genuine Golden Visual PNG.

Canonical generation remains externally blocked until an approved `$0-local` execution host is available with the required combination of CUDA, supported precision, sufficient live VRAM and RAM, safe local offload/runtime, pinned model evidence, and the existing semantic/provenance gates.

The ZeroGPU remote-renderer benchmark remains useful only as an isolated visual research lane and cannot be promoted into canonical Golden evidence, regardless of visual quality.
