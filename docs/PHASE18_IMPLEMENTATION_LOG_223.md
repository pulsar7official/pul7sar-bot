# Phase 18 Implementation Log 223

## Scope

Repository: `pulsar7official/pul7sar-bot`

Write branch: `phase18/story-intelligence` only.

`main` remained read-only. No merge, force-update, or direct write to `main` or `main.py` was performed.

## Starting point

Change Set 222 introduced an explicit research-to-local candidate declaration and deliberately left the Qwen Image 2512 candidate without an approved immutable local-execution revision.

That was the next safe gap to close before measured runtime work.

## External model evidence reviewed

Official Hugging Face material for `Qwen/Qwen-Image-2512` was reviewed before pinning:

- model repository: `Qwen/Qwen-Image-2512`
- license: Apache-2.0
- reported repository size: approximately 57.7 GB
- tensor type: BF16
- official pipeline family: Qwen Image / Diffusers
- verified model upload commit: `2ce1c28560fbc62c9f5531e076b237d3575330a9`

The commit is used as an immutable snapshot target. This is a model-identity decision only, not a claim of runtime compatibility.

## Change Set 223 implemented

### 1. Approved revision registry

Modified:

`engine/intelligence/approved_model_revisions.py`

Added:

- `QWEN_IMAGE_2512_MODEL_ID = "Qwen/Qwen-Image-2512"`
- `QWEN_IMAGE_2512_REVISION = "2ce1c28560fbc62c9f5531e076b237d3575330a9"`

The existing full-SHA and snapshot-revision helpers remain unchanged and continue to fail closed on mutable or malformed revisions.

### 2. Explicit candidate declaration upgraded

Modified:

`engine/intelligence/remote_renderer_local_candidate.py`

Contract upgraded to:

`pul7sar-phase18-remote-renderer-explicit-local-candidate-v2-pinned-revision`

The builder now requires an approved immutable revision for the explicitly selected exact local candidate. A Qwen Image 2512 declaration records the pinned revision and proves it is a full 40-character SHA.

It still refuses to authorize runtime or generation because the curated Qwen Image 2512 profile retains:

`runtime_floor_proven = false`

The following remain false:

- `local_runtime_qualified`
- `local_generation_authorized`
- `canonical_golden_eligible`
- `semantic_approved`
- `golden_quality_approved`
- `publication_ready`

Remote research pixels remain non-canonical.

### 3. Regression coverage updated

Modified:

`tests/test_phase18_remote_renderer_local_candidate.py`

The success case now proves:

- exact Qwen model identity;
- exact pinned upstream SHA;
- 40-character immutable revision form;
- `pinned_model_revision_proven = true`;
- runtime floor remains unproven;
- local generation remains unauthorized.

The existing tests still reject:

- FLUX.2-dev → FLUX.2-klein substitution;
- other wrong-model substitutions;
- unknown candidate IDs;
- docket authority drift;
- docket SHA tampering;
- path escape.

## Files modified

- `engine/intelligence/approved_model_revisions.py`
- `engine/intelligence/remote_renderer_local_candidate.py`
- `tests/test_phase18_remote_renderer_local_candidate.py`

## Files added

- `docs/PHASE18_CHANGESET_223_PINNED_QWEN_IMAGE_2512_REVISION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_223.md`

## Files deleted

None.

## Commits created for Change Set 223

- `e541edd8140a34bf4530591b4b0d36f2c739c52d` — pin Qwen Image 2512 revision in the approved revision registry
- `75178e9bb770fed930b7bc129585dfdec42e40e6` — bind explicit local candidate declaration to the pinned revision
- `9653ea0ff05e8f5c5795e91ff4aa6c073f7eabd3` — update regression coverage for revision pinning
- `099bb21f91613b501049db83236a10519ed72d04` — Change Set 223 documentation
- `e44398c3f0048210963a922f1164c044846ff6b5` — initial implementation log

## Gates preserved

No relaxation was made to:

- Fact Lock
- Entity/Identity Verification
- Sentiment/Neutrality
- canonical `$0-local`
- generated text/branding/exact facts/entity marks/exact sport geometry exclusion
- CUDA/precision/VRAM/RAM/offload/runtime qualification
- Semantic and Layer Ownership
- Visual Critic hard failures
- Human Review
- Golden 8.5 minimum / 9.0+ elite
- Exact Brand Integrity
- Typography Integrity
- SemanticPublicationGate

## Remaining blocker toward a new accepted Genuine Golden PNG

Pinning the Qwen Image 2512 snapshot removes mutable-model ambiguity but does not create a runnable host.

The exact remaining Qwen-specific blocker is **measured `$0-local` runtime compatibility**. The curated Qwen Image 2512 profile is approximately 57.7 GB and its PUL7SAR runtime floor remains intentionally unproven. No canonical generation can be authorized until compatible hardware proves CUDA/precision/VRAM/RAM/offload/runtime readiness for the pinned snapshot.

The broader environment available to this automation still does not provide an approved local GPU host for canonical generation, so no new Golden PNG is fabricated or claimed.

## CI results

Change Set 222:

- Story Intelligence Verification Run `33131011178`
- head SHA: `a9fdc17cfd086fc3b848492ecafe93b5456d3671`
- conclusion: `success`

Change Set 223:

- Story Intelligence Verification Run `33131139158`
- head SHA: `e44398c3f0048210963a922f1164c044846ff6b5`
- conclusion: `success`

Both runs completed successfully. The final write after those runs is documentation-only and records the verified results above.
