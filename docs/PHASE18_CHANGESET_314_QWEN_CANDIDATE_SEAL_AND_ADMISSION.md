# Phase 18 Change Set 314 — Qwen Candidate Seal and Admission

## Goal

Close the procedural gap between a genuinely executed, launch-attested Qwen canonical candidate and the existing CS303 exact-byte post-generation QA admission edge.

CS313 established the branch-safe canonical Qwen GPU workflow, but stopped after replaying `launch_to_output_attestation.json`. The same workflow now seals the already-generated candidate into the existing CS301 canonical-candidate handoff and immediately replays CS303 exact-byte admission. No second inference is performed.

## Scope

Branch: `phase18/story-intelligence` only.

`main` remains read-only.

## Execution chain added

After a genuine manifest-bound Qwen inference and independent launch-to-output attestation replay, the workflow now executes:

1. `phase18_qwen_image_canonical_candidate_handoff.py build` against the exact canonical inference output directory;
2. `phase18_qwen_image_canonical_candidate_handoff.py verify` against the newly sealed handoff;
3. `phase18_admit_canonical_candidate_bytes.py` against that exact handoff;
4. explicit workflow assertions that the handoff is sealed and the exact bytes are admitted for downstream QA while Genuine-Golden and publication authorities remain false.

## Authority boundary

CS314 does not grant or synthesize:

- semantic approval;
- identity approval;
- generated-layer approval;
- composition approval;
- Golden visual-quality approval;
- human visual-review approval;
- brand/typography approval;
- final semantic approval;
- `SemanticPublicationGate` approval;
- Genuine Golden PNG materialization;
- publication readiness.

The candidate remains only a genuine, replay-attested, sealed, byte-admitted Qwen candidate until the existing downstream gates independently approve it.

## Zero-cost and provenance guarantees

The existing CS313 `$0-local`, offline, self-hosted CUDA/BF16 and local-snapshot requirements are unchanged.

The CS301 handoff replays the launch-to-output attestation and byte-binds the canonical PNG, canonical inference receipt, local inference provenance, and launch attestation. CS303 then replays the handoff, canonical inference receipt and PNG bytes before admitting them for post-generation QA.

## Deleted behavior

None. No legacy path was removed, and no quality or publication gate was weakened.
