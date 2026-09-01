# Phase 18 Change Set 305 — Candidate-Lineage-Bound Identity Requirement

## Purpose

CS305 removes the last independent CS257 evidence selector from the production canonical-candidate identity-requirement edge.

Before CS305, CS265 accepted both a verified CS264 semantic-base-QA receipt and a caller-selected `cs257_run_dir`. The selected CS257 run was checked for the same story snapshot and valid identity evidence, but it was not required to be the exact CS257 evidence directory already sealed into the candidate's generation launch manifest. Two independently valid CS257 runs for the same story could therefore be substituted at this downstream edge.

CS305 makes the generated candidate's own lineage authoritative.

## Required lineage

The identity requirement now derives evidence only through:

1. CS304 semantic-base-QA receipt.
2. CS303 candidate byte-admission receipt bound by CS304.
3. CS301/302 canonical-candidate handoff bound by CS303.
4. CS293 launch-to-output attestation bound by the handoff.
5. GPU host launch manifest bound by the attestation.
6. The exact CS257 evidence directory and file set recorded in that launch manifest.

Every intermediate file is reopened from a repository-relative byte binding and replayed with its canonical verifier. Story SHA, handoff SHA, receipt digests, path canonicalization, zero-cost mode, local-only execution, and the launch-manifest CS257 directory are checked fail-closed.

## Production API change

`run_identity_requirement(...)` no longer accepts `cs257_run_dir`.

The production CLI `tools/phase18_classify_canonical_candidate_identity_requirement.py` no longer exposes `--cs257-run-dir`.

The only production input that selects the evidence lineage is the CS304 receipt itself; the evidence run is derived from the candidate's sealed launch history.

## Receipt contract

The identity-requirement schema is upgraded to:

`pul7sar-phase18-qwen-image-canonical-candidate-identity-requirement-v2`

The receipt adds `lineage_bound_identity_source`, containing the handoff digest, launch-manifest byte binding, and launch-bound CS257 directory/file binding. Verification re-derives these values from the upstream candidate lineage and rejects drift.

## Authority boundary

CS305 does not perform face recognition and does not approve identity. It only determines whether pixel-identity review is mandatory and binds the review targets to the exact identity evidence that authorized the candidate's generation lineage.

The following remain false:

- `identity_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `genuine_golden_png_created`
- `publication_ready`

Fact/freshness, entity identity, sentiment neutrality, loser-respect, zero-cost/local-only execution, semantic-publication, generated-layer/composition QA, visual-quality adjudication, Human Review, exact brand/typography, Genuine Golden materialization, and publication-readiness gates are not bypassed or weakened.

## Genuine Golden status

CS305 is control-plane hardening only. It does not load Qwen-Image, execute CUDA/BF16 inference, create a canonical candidate, compose a production visual, or create a Genuine Golden PNG.
