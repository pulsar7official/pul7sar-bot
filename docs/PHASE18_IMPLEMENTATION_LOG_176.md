# PUL7SAR Phase 18 — Implementation Log 176

## Branch isolation

Reviewed the repository state before writing.

- Target repository: `pulsar7official/pul7sar-bot`
- Target branch: `phase18/story-intelligence`
- Branch HEAD at review start: `d14ea0d34dedf2748b674c55cba91b7c9654d31a`
- `main` was not used as a write, merge, force-update, or file-update target.
- No production publishing path was modified.

## Change Set 176

**Name:** Composition Map Provenance Lock

### Problem found

Golden Editorial v6 now carries an explicit story-first composition map through the generation handoff and Colab summary. The current semantic continuation still verified the v6 manifest, cost mode, BF16, context-only surface policy, camera preset, PNG SHA, semantic approval, and pixel identity, but it did not itself require the exact focal anchor / negative-space / brand-quiet-zone map.

That meant a stale or tampered canonical summary could theoretically preserve a valid PNG and generic semantic evidence while changing the editorial hierarchy that Candidate 1 was supposed to prove.

### Added

- `docs/PHASE18_CHANGESET_176_COMPOSITION_MAP_PROVENANCE_LOCK.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_176.md`

### Modified

- `tools/phase18_continue_hybrid_from_first_png.py`
  - added fail-closed validation for `visual_priority`, `focal_anchor`, `copy_negative_space`, and `brand_quiet_zone` before semantic review;
  - added independent validation of the same map on the semantic-review result;
  - upgraded the receipt schema to `pul7sar-first-png-editorial-semantic-continuation-v3`;
  - records `composition_map_locked=true` and the exact v6 map in the semantic proof.

- `tests/test_phase18_first_png_hybrid_semantic_continuation.py`
  - updated v6 fixtures;
  - tests every composition-map field for handoff drift before Qwen review;
  - tests every field for semantic-result drift;
  - verifies the final receipt preserves the map while keeping Golden/publication authority closed.

### Deleted

None.

## Gates preserved

No gate was weakened or bypassed:

- Fact Lock and factual accuracy remain fail-closed.
- Entity/Identity Verification remains unchanged.
- Sentiment/neutrality and loser-respect rules remain unchanged.
- `$0-local` remains required.
- FLUX/Qwen pinned revisions and BF16 locks remain unchanged.
- GPU/VRAM/RAM/offload/runtime-fingerprint gates remain unchanged.
- generated text, branding, exact facts, entity marks, and exact sport geometry remain forbidden where owned by deterministic layers.
- Qwen semantic inspection remains required for semantic approval.
- Golden `8.5 minimum / 9.0+ elite` remains downstream and unapproved here.
- Exact Brand/Typography and SemanticPublicationGate remain downstream.
- `publication_ready=false` remains mandatory.
- Seeds 2–4 remain unauthorized before Candidate 1 is genuinely produced and reviewed.

## Testing status

The new regression tests were committed to the Phase 18 branch. GitHub Actions must complete on the resulting HEAD before this Change Set is described as CI-green. No CI success is claimed in this log until a real completed run is available.

## Genuine Golden PNG status

No genuine Golden Editorial v6 Candidate 1 PNG was fabricated or claimed in this change set.

The remaining execution blocker is still a compatible real host that simultaneously proves:

- NVIDIA CUDA;
- native BF16;
- sufficient total and live-free VRAM;
- sufficient live system RAM through lease/execution;
- safe local Diffusers offload/runtime;
- pinned FLUX.2 Klein 4B and Qwen revisions;
- stable runtime fingerprint;
- `$0-local` execution.

Change Set 176 materially reduces the remaining gap by ensuring the first genuine PNG cannot reach semantic/human Golden review under a different composition hierarchy than the one approved in the v6 generation contract.
