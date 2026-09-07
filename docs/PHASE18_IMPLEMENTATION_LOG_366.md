# Phase 18 Implementation Log 366

## Scope

Change Set 366 — CS336 Snapshot Lineage.

Branch-only work: `phase18/story-intelligence`.

Starting branch HEAD reviewed before implementation:

`78810f50ef0c92e936ee1520947d2cc548c39f39`

`main` was inspected read-only at `f8fa6cfc7660171d5702fa626813e01504e0e03f` and was not modified, merged, rebased, reset, force-updated, or used as a write target.

## Proven gap

CS365/CS272 already preserved and freshly reverified the exact Qwen-Image generator snapshot-byte lineage at composed-candidate byte admission. The existing CS336 continuation consumed and independently reverified CS271 and CS272, rebound the exact composed PNG, and stopped before post-composition authority; however, its own receipt dropped the five generator snapshot-lineage fields.

CS366 closes that specific branch-local gap inside CS336 itself rather than adding a parallel gate.

## Modified

- `engine/intelligence/qwen_image_precomposition_to_composed_byte_admission.py`
  - schema upgraded from v1 to v2;
  - added strict snapshot-lineage validation;
  - requires generator snapshot inventory verification;
  - compares fresh CS271 and fresh CS272 lineage field-by-field;
  - seals the five exact lineage fields in the CS336 receipt;
  - replays CS271 and CS272 during verification and compares both against the sealed CS336 lineage;
  - added policy declarations documenting the exact generator-lineage requirement.

- `tests/test_phase18_qwen_precomposition_to_composed_byte_admission.py`
  - updated success fixture for CS365 lineage;
  - verifies all five lineage fields survive the CS336 build;
  - rejects unverified snapshot inventory;
  - rejects snapshot-inventory digest drift;
  - rejects model-revision drift;
  - verifies recomputing the outer CS336 receipt digest does not hide snapshot-lineage tampering;
  - retains one-shot/no-retry, premature-authority, and static network/generation/publication isolation coverage;
  - after full-suite discovery exposed independent mocked lineage drift, the CS272 success fixture was corrected to inherit its five generator-lineage fields directly from the exact mocked CS271 value and an explicit pre-call equality assertion was added.

## Added

- `docs/PHASE18_CHANGESET_366_CS336_SNAPSHOT_LINEAGE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_366.md`

## Deleted

Nothing.

## Commits

- `0de901337bcfa2c140f27f1971c2b04ea59e579b` — production CS336 lineage preservation
- `21d74532ea078d99017167dfd8e214cf9a1429a0` — initial regression coverage / initial code-and-test SHA
- `eacc6bd4f03fbaec2457f76fb8cf9790385b5789` — Change Set contract documentation
- `d60be795e3565f7a0248f2cb2d4ea09748ed1379` — initial implementation log
- `532a42427aea4b6c15a881e8cead9072bae6e96b` — success-fixture lineage correction after full-suite CI discovery

The commit updating this log follows the commits above.

## Preserved snapshot lineage

CS336 now seals and freshly checks:

- `snapshot_byte_inventory_verified = true`
- `snapshot_inventory_sha256`
- `snapshot_file_count`
- `snapshot_total_bytes`
- `model_revision`

Verification does not trust the outer `receipt_sha256` alone. After checking that digest, it independently reopens and reverifies the exact CS271 and CS272 receipts and compares all five lineage fields against the sealed CS336 receipt. Recomputed outer-digest tampering therefore remains fail-closed.

## Authority boundary

Success may establish only the existing execution/admission facts:

```text
precomposition_execution_ready = true
cs271_attempt_consumed = true
composition_executed = true
composed_candidate_bytes_admitted_for_post_composition_qa = true
```

Success still requires:

```text
composed_visual_approved = false
semantic_approved = false
human_visual_review_approved = false
golden_quality_approved = false
genuine_golden_png_created = false
publication_ready = false
authoritative = false
```

No factual/freshness, Entity/Identity, sentiment neutrality/loser-respect, semantic, visual, Human Review, Golden, Brand/Typography, Final Composed, Final Semantic, SemanticPublicationGate, Genuine-Golden materialization, or publication authority was weakened or bypassed.

## Zero-cost / isolation boundary

No dependency was added. No model download, network-model fallback, paid inference fallback, synthetic inference, retry loop, upload/publish call, or downstream approval shortcut was introduced.

## Testing state

Initial code-and-test-bearing SHA:

`21d74532ea078d99017167dfd8e214cf9a1429a0`

The push **Phase 18 Story Intelligence Verification** run `34171371439` / #5143 reached full `unittest` discovery and failed one new CS366 success-fixture test. The production contract correctly detected a mismatch between the mocked CS271 and CS272 `snapshot_inventory_sha256` values and failed closed with:

`CS336_CS271_CS272_SNAPSHOT_LINEAGE_DRIFT:snapshot_inventory_sha256`

The failure was not suppressed. The success fixture was corrected so mocked CS272 inherits its generator snapshot lineage from the exact mocked CS271 value, matching the production relationship being modeled. An explicit equality assertion now verifies that fixture invariant before CS336 execution.

Current code-and-test-bearing SHA after that correction:

`532a42427aea4b6c15a881e8cead9072bae6e96b`

GitHub Actions verification must be observed on that exact SHA before any terminal-green claim is made. This log deliberately makes no terminal-green claim until the relevant workflow reports `completed/success`.

## Genuine Golden PNG status

No genuine Qwen-Image inference was performed and no production `canonical_candidate.png` or `genuine_golden_visual.png` is claimed.

The external generation blocker remains a zero-cost compatible host that provides together:

- NVIDIA CUDA GPU;
- CUDA-enabled PyTorch;
- native BF16;
- sufficient RAM/VRAM demonstrated under real Qwen-Image load/inference;
- approved Qwen-Image/Diffusers runtime;
- exact approved already-local pinned generator snapshot and verifier assets;
- no paid or network-model fallback.

## Remaining path

The exact generator snapshot-byte provenance now survives the existing CS336 wrapper boundary and accompanies the exact composed PNG into the post-composition side of the pipeline. First, the corrected exact code-and-test SHA must reach terminal-green CI. After that, the next safe engineering action is to identify the first existing post-composition consumer of CS336/CS272 on this branch and harden it only if it demonstrably drops this lineage. Genuine image generation remains blocked by the CUDA/BF16 host requirement above.
