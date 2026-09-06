# Phase 18 Implementation Log 222

## Scope

Repository: `pulsar7official/pul7sar-bot`

Write branch: `phase18/story-intelligence` only.

`main` was reviewed read-only and was not modified, merged, force-updated, or used as a write target.

## Branch state at start

- Phase 18 HEAD: `ba936d6ec0829efa122fdf149bc251ba4cdf0de2`
- `main` HEAD: `2a6dee5bb64895a1658be84d7ce018cd71a08dff`
- compare status: `diverged`
- Phase 18 ahead of `main`: 1842 commits
- Phase 18 behind `main`: 226 commits

The `main` head movement was an independent posted-history update and was not touched by this change set.

## Baseline verification

Change Set 221 is confirmed green:

- Phase 18 Story Intelligence Verification Run `33127939947`
- conclusion: `success`
- head SHA: `ba936d6ec0829efa122fdf149bc251ba4cdf0de2`

## Gap found

Change Set 221 correctly produces a research-to-local qualification docket only when a remote renderer leader is blocker-free and strong enough to justify scarce local measurement time. The docket deliberately leaves:

- `local_model_candidate_id = null`
- `local_runtime_qualified = false`
- `canonical_generation_authorized = false`

The next gap was that no fail-closed contract existed for turning that recommendation into an **explicitly named curated local model candidate** without accidentally treating a related but different local model as equivalent.

Example risk: a `flux2-dev` research leader must not be silently converted into `FLUX.2-klein-4B` simply because both are FLUX.2 models.

## Change Set 222 implemented

### 1. Explicit local candidate declaration engine

Added:

`engine/intelligence/remote_renderer_local_candidate.py`

Contract:

`pul7sar-phase18-remote-renderer-explicit-local-candidate-v1`

The builder:

1. constrains the docket path to the repository;
2. validates the Change Set 221 docket contract and non-authoritative state;
3. replays the docket SHA-256;
4. requires a non-empty caller-supplied `local_model_candidate_id`;
5. resolves that ID only from `ZERO_COST_LOCAL_CANDIDATES`;
6. proves the candidate is local/free by policy and requires no payment method;
7. requires an exact curated upstream-model match for the remote renderer;
8. keeps remote pixels non-canonical;
9. keeps local runtime, generation, Semantic, Golden and Publication authority closed.

Current exact mapping is intentionally narrow:

- `qwen-image-2512` → `local-qwen-image-2512` / `Qwen/Qwen-Image-2512`

There is deliberately no mapping from `flux2-dev` to `FLUX.2-klein-4B`.

### 2. Candidate declaration CLI

Added:

`tools/phase18_build_remote_renderer_local_candidate.py`

The CLI is CPU-only and writes a declaration receipt. It does not run FLUX/Qwen, does not touch the generation queue, and cannot grant canonical generation or publication authority.

### 3. Regression coverage

Added:

`tests/test_phase18_remote_renderer_local_candidate.py`

Coverage includes:

- successful explicit Qwen Image 2512 declaration;
- proof that the Qwen profile still has `runtime_floor_proven = false`;
- proof that no pinned revision is claimed;
- rejection of FLUX.2-dev → FLUX.2-klein substitution;
- rejection of any wrong exact-model substitution;
- rejection of unknown/unreviewed candidate IDs;
- explicit ID requirement;
- docket authority drift rejection;
- docket digest tampering detection;
- repository path-escape rejection.

### 4. Documentation

Added:

- `docs/PHASE18_CHANGESET_222_EXPLICIT_REMOTE_TO_LOCAL_MODEL_CANDIDATE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_222.md`

## Commits created during this run

- `8cedde9cb27ed447250f298b47044f90d845aba5` — explicit candidate declaration engine
- `17f1bad43253b562b1e975af022ca9a2a26176bf` — declaration CLI
- `4868a5cec45d52ffa0299281a584b5135901b002` — regression suite
- `642c7ff300ac363e4a26115353235618f988a681` — Change Set 222 documentation

This log itself is the final documentation write for the change set.

## Files added

- `engine/intelligence/remote_renderer_local_candidate.py`
- `tools/phase18_build_remote_renderer_local_candidate.py`
- `tests/test_phase18_remote_renderer_local_candidate.py`
- `docs/PHASE18_CHANGESET_222_EXPLICIT_REMOTE_TO_LOCAL_MODEL_CANDIDATE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_222.md`

## Files modified

None of the existing generation/runtime/publication modules.

## Files deleted

None.

## Gate preservation

Unchanged and still fail-closed:

- Fact Lock
- Entity/Identity Verification
- Sentiment/Neutrality
- canonical `$0-local` policy
- generated text/branding/exact facts/entity marks/exact sport geometry exclusion
- pinned-model/runtime evidence requirements
- Semantic and Layer Ownership review
- byte-bound Visual Critic hard failures
- explicit Human Review
- Golden 8.5 minimum / 9.0+ elite target
- Exact Brand Integrity
- Typography Integrity
- SemanticPublicationGate

The Change Set 222 declaration explicitly records:

- `research_pixels_reusable_as_canonical_evidence = false`
- `pinned_model_revision_required = true`
- `pinned_model_revision = null`
- `measured_runtime_readiness_required = true`
- `local_runtime_qualified = false`
- `local_generation_authorized = false`
- `canonical_golden_eligible = false`
- `semantic_approved = false`
- `golden_quality_approved = false`
- `publication_ready = false`

## Exact remaining blocker toward a new accepted Genuine Golden PNG

No new canonical GPU image was produced in this run.

The execution environment available to this automation still does not provide an approved `$0-local` host that proves the required CUDA/precision/VRAM/RAM/offload/model/runtime evidence for a new canonical generation.

Change Set 222 additionally makes the research-to-local gap explicit:

- if Qwen Image 2512 becomes the research leader, a curated exact local profile exists, but its PUL7SAR runtime floor is not yet proven and an immutable local-execution revision is not yet pinned;
- if FLUX.2-dev becomes the research leader, no exact curated local candidate currently exists, so it cannot advance canonically by substituting FLUX.2 Klein.

The next safe canonical step is therefore to pin/declare the exact upstream revision for an explicitly selected local candidate and measure `$0-local` runtime readiness on compatible hardware before any canonical generation authorization.

## CI status for Change Set 222

Pending at the time this log was created. No CI success is claimed until GitHub Actions completes on the new Phase 18 head.
