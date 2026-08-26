# PUL7SAR Phase 18 Implementation Log — Change Set 172

## Branch safety review

- Target repository: `pulsar7official/pul7sar-bot`.
- Target branch: `phase18/story-intelligence` only.
- Branch HEAD observed at start of run: `8ea4986d19c4898df8bdff567009a1f7da448d79`.
- `main` observed independently at `4aa036ebf00b175021f8302d0a79fdb8e9448c03` and was not modified, merged, force-updated, or used as a write target.
- All writes in this run targeted `phase18/story-intelligence` explicitly.

## Baseline verification result reviewed before new work

Change Set 171 Story Intelligence Verification Run `32965445031 / 2911` completed with **failure** while all visible companion Phase 18 visual workflows on the same branch head completed successfully.

The failing Story Intelligence job reached `Syntax and discover validation`, ran the Phase 18 test suite, and reported one regression-test failure:

`test_worker_binds_second_requalification_inside_leased_execution`

The assertion still expected `_requalify_execution_host(capabilities)` directly inside the `GenerationWorkerService(...)` constructor block. Change Set 171 had intentionally strengthened that path: the service now calls `_record_lease_bound_execution_evidence(...)`, and that helper performs `_requalify_execution_host(...)` then writes a tamper-evident receipt before FLUX. No production rollback was made. The regression test was aligned to the stronger implementation.

## Change Set 172 — First-PNG Resource Provenance Binding

### Goal

Close the remaining gap between lease-bound resource safety and first-PNG provenance. A succeeded Golden Candidate 1 must no longer be reusable based only on PNG/executor/metadata provenance; the exact post-lease/pre-FLUX GPU + host-RAM receipt for the same successful attempt must also replay successfully.

### Added behavior

`LeaseBoundExecutionResourceEvidenceStore.verify(...)` now replays a durable resource receipt against the final succeeded `GenerationJob` and fails closed on:

- wrong schema;
- wrong job/request/provider/model/payload identity;
- wrong attempt;
- unsafe worker ID;
- missing or invalid timezone-aware observation time;
- unproven native BF16;
- non-`$0-local` resource evidence;
- recorded live-free VRAM below the recorded requirement;
- recorded available system RAM below the recorded requirement;
- queue/generation/semantic/Golden/publication authority drift;
- evidence path outside the repository;
- missing/malformed evidence file.

`FirstPngProvenancePostflight.verify(...)` now requires this execution-resource receipt and binds its SHA-256, byte size, worker, attempt, timestamp, GPU evidence, and host-memory evidence into the first-PNG postflight result.

`tools/phase18_verify_first_png_provenance.py` now accepts `--execution-resource-receipt` and otherwise resolves the canonical attempt-bound receipt under `output/phase18_worker_results`.

### Regression repair included

Updated `tests/test_phase18_gpu_worker_live_requalification.py` to assert the actual Change Set 171 chain:

`pre_execute_guard -> _record_lease_bound_execution_evidence -> _requalify_execution_host -> evidence_store.write`

The previous test expected the older direct requalification call inside the service constructor and caused Run 2911 to fail despite the stronger implementation being present.

## Files added

- `docs/PHASE18_CHANGESET_172_FIRST_PNG_RESOURCE_PROVENANCE_BINDING.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_172.md`

## Files modified

- `engine/intelligence/execution_resource_evidence.py`
- `engine/intelligence/first_png_provenance_postflight.py`
- `tools/phase18_verify_first_png_provenance.py`
- `tests/test_phase18_execution_resource_evidence.py`
- `tests/test_phase18_first_png_provenance_postflight.py`
- `tests/test_phase18_gpu_worker_live_requalification.py`

## Files deleted

None.

## Gates preserved unchanged

- Fact Lock and factual integrity.
- Source consensus / stale-state checks.
- Entity and Identity Verification.
- Sentiment, neutrality, and loser-respect policy.
- `$0-local` only.
- Pinned FLUX.2 Klein 4B revision.
- Pinned Qwen revision.
- Native BF16 requirement.
- Total/live-free VRAM qualification.
- Safe local Diffusers offload qualification.
- Live host-RAM qualification.
- Cycle-level and lease-bound resource requalification.
- Runtime fingerprint stability.
- Candidate/request/seed/canvas/SHA locks.
- No generated platform branding, exact facts, entity marks, text, or code-owned sport geometry.
- Qwen `BASE_SCENE` and `HYBRID_SURFACE` gates.
- Deterministic football geometry.
- Provenance/evidence replay.
- Golden visual minimum 8.5 and elite 9.0+ thresholds.
- Exact Brand Integrity and Typography Integrity.
- SemanticPublicationGate and final publication readiness.

## Testing status

The previous branch head Run `32965445031 / 2911` was inspected in full and its single failing regression assertion was identified before new feature work.

Change Set 172 Story Intelligence Verification Run `32970990669 / 2927` completed with **success**. The full Phase 18 discover validation, completion/production-isolation checks, current visual-study handoffs, and Golden Hybrid v5 CPU build/integrity path all passed. Every visible companion Phase 18 workflow on the same head also completed successfully, including Composition Matrix, Data Monument, Verified Match Result, Event Editorial, Event Hybrid Context, Adaptive Brand, Result Statement, Tactical Intelligence, and Premium Hybrid Result.

This CI success verifies the stronger resource-to-first-PNG provenance contract on CPU. It is not a claim that GPU generation occurred.

## Genuine Golden Visual status / exact blocker

No genuine Golden Hybrid v5 Candidate 1 PNG exists from this run and none was fabricated.

The remaining external execution blocker is availability of a real host that proves, at the time of execution:

- NVIDIA CUDA;
- native BF16;
- sufficient total and live-free VRAM;
- safe local Diffusers offload/runtime;
- sufficient live system RAM through the lease/execution boundary;
- pinned FLUX and Qwen revisions;
- stable runtime fingerprint;
- `$0-local` execution.

The material gap reduced by Change Set 172 is that a future genuine Candidate 1 PNG will now be bound to the exact lease-bound physical resource receipt that immediately preceded its successful FLUX attempt, closing the resource-to-pixel provenance chain before semantic and Golden review.
