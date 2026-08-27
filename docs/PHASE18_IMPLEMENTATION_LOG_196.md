# PUL7SAR Phase 18 — Implementation Log 196

## Branch safety

- Repository: `pulsar7official/pul7sar-bot`
- Development branch: `phase18/story-intelligence`
- Baseline reviewed before this change: `153eafe17787b45fb85d7f0b8a448bcb16e7509f`
- Baseline `main` observed independently at review time: `813ef31d2647e4353ca604e60e48975c79d7d95e`
- `main` / `main.py` were not modified, merged, force-updated or used as a write target.

The reviewed Phase 18 baseline was already engineering-complete and its latest GitHub Actions suite showed successful Phase 18 companion workflows. The engineering-completion handoff explicitly records that the first real Golden Editorial v6 Candidate 1 exists but is rejected because of physically inconsistent partial goal/touchline geometry. That image is a regression example, not an accepted Golden visual.

## Change Set 196 — Canonical Real-Visual Validation Ledger

### Why this was the next safe step

Phase 18 engineering is no longer blocked on missing orchestration architecture. The remaining gap is real multi-family PNG validation and owner acceptance. Without a canonical evidence ledger, validation could become ad-hoc, allow seed cherry-picking, lose rejected-candidate evidence, or accidentally confuse a high aesthetic score with publication readiness.

This change establishes one fail-closed record format for all seven canonical visual benchmark families before more real candidates are evaluated.

### Added

1. `engine/intelligence/visual_validation_ledger.py`
   - derives the exact benchmark set from `PHASE18_VISUAL_BENCHMARKS`;
   - accepts only real PNG evidence with PNG signature, SHA-256 and byte count;
   - tracks `pending_real_visual`, `rejected`, and `accepted` states;
   - requires accepted candidates to pass factual integrity, identity integrity, sentiment/neutrality, sport geometry, protected zones, platform crop, semantic QA and provenance;
   - requires explicit owner visual acceptance;
   - requires Golden score >= `8.5`;
   - makes every hard blocker fatal to acceptance, including broken sport geometry;
   - never grants publication authority.
2. `tools/phase18_build_visual_validation_ledger.py`
   - initializes the canonical seven-case ledger;
   - validates existing ledgers without overwriting review evidence;
   - restricts ledger output to repository-local paths.
3. `tests/test_phase18_visual_validation_ledger.py`
   - seven-case canonical coverage;
   - genuine PNG signature enforcement;
   - accepted-case gate completeness;
   - explicit owner-acceptance requirement;
   - Golden 8.5 minimum;
   - 9.9 cannot override `broken_sport_surface_geometry`;
   - rejected candidates remain publication-closed;
   - even seven accepted cases do not grant publication authority.
4. `docs/PHASE18_CHANGESET_196_VISUAL_VALIDATION_LEDGER.md`
5. `docs/PHASE18_IMPLEMENTATION_LOG_196.md`

### Modified

`tools/phase18_completion_audit.py`

The audit now requires the validation-ledger engine and CLI, checks their fail-closed contract markers, reports the ledger schema explicitly, records that the ledger has zero publication authority, and changes the next target to binding every real benchmark PNG into the canonical ledger before publication assets are considered.

### Deleted

Nothing.

## Gate preservation

The following remain unchanged and fail-closed:

- Fact Lock and factual integrity;
- Entity / Identity Verification;
- Sentiment / Neutrality and respectful losing-side treatment;
- `$0-local` generation policy;
- pinned FLUX and Qwen identities/revisions;
- semantic inspection and SemanticPublicationGate;
- sport-geometry policy `exact_verified_or_visually_indeterminate`;
- partial / invented regulation geometry as a hard failure;
- Golden minimum `8.5`, elite target `9.0+`;
- exact brand and typography integrity;
- provenance/evidence replay;
- explicit final publication approval.

The new ledger itself is incapable of setting `publication_ready=true`.

## Testing state

The baseline head reviewed before Change Set 196 had successful Phase 18 GitHub Actions coverage. The new files and regression tests were committed to `phase18/story-intelligence`; a new Story Intelligence verification run is expected to be triggered by these commits. This log does not claim the new head is CI-green until a completed successful run is observed.

## Genuine Golden PNG status

No new PNG was fabricated in this change set.

A real Golden Editorial v6 Candidate 1 has already been produced by the project, but it remains **rejected** because of physically inconsistent partial football goal geometry. The immediate visual objective is therefore the first **accepted** Golden candidate, followed by real multi-family validation across the canonical benchmark set.

## Exact external blocker

Further genuine generation/validation still depends on a compatible execution environment and real outputs. The project must not fabricate CUDA/BF16, semantic-inspector or owner-review evidence. Real candidate generation requires a host that satisfies the established local execution gates (CUDA/native BF16 where Golden-reference execution is required, sufficient live GPU/RAM resources, pinned model snapshots, safe offload/runtime and `$0-local`) or another already-qualified real-output route.

## Next target

1. Run/obtain the next real Preview/General candidate under the repaired `exact_verified_or_visually_indeterminate` geometry contract.
2. Bind the genuine PNG and its provenance/semantic evidence into the canonical validation ledger.
3. Record rejection causes rather than seed-hunting if it fails.
4. Accept only when all mandatory integrity checks pass, owner visual review is explicit, no hard blocker exists, and Golden score is at least 8.5.
5. Keep publication closed until brand/typography/rights/semantic-publication/final-owner gates are separately satisfied.
