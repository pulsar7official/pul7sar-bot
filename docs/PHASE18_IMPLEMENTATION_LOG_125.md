# PUL7SAR Phase 18 — Implementation Log 125

This log records work on `phase18/story-intelligence` only. `main` was not modified.

## Branch state reviewed

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence`
- Branch was reviewed as diverged from `main`; no merge, update, or force-write to `main` was performed.
- PR #1 remained open, Draft and unmerged with `main` as base.
- The first genuine Golden Hybrid v5 FLUX.2 Klein Candidate 1 is still not generated in the current tool environment because no compatible CUDA/BF16 host is attached.

## Progress made in this automation pass

### Change Set 123 — First-PNG Semantic Preflight Lock

Modified `tools/phase18_first_png.py` so the one-command Candidate 1 path now requires the same exact local Qwen runtime/model semantic preflight already enforced by the self-hosted GPU workflow.

Direct first-PNG order is now:

`Golden batch integrity → CUDA/BF16 host qualification → Qwen semantic/model preflight → FLUX model cache → FLUX/BF16 readiness → durable Candidate 1 queue → GPU worker → genuine PNG`

The semantic preflight must prove the exact Qwen model, `$0-local`, CUDA, runtime/model readiness, and zero generation/queue/PNG/publication authority before FLUX preparation or queue mutation.

Updated `tests/test_phase18_first_png_preflight.py` verifies the ordering and fail-closed contract.

Added:

- `docs/PHASE18_CHANGESET_123_FIRST_PNG_SEMANTIC_PREFLIGHT_LOCK.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_123.md`

All new Change Set 123 tests passed in subsequent full CI runs.

### CI blocker encountered while validating Change Set 123

Run `32741891562` / 1830 failed only in two existing embedded-brand tests. New first-PNG semantic-preflight tests passed.

An initial safe transport-recovery attempt was recorded as Change Set 124. It deliberately kept the existing binary/member SHA locks unchanged.

Run `32742363762` / 1841 still failed because the recovered bytes did not match the pinned approved bundle SHA. The repair was therefore not accepted as successful.

### Exact diagnosis

A bounded diagnostic was added without changing acceptance behavior. Run `32742612700` / 1855 then proved the actual root cause in the repository-carried study bundle:

`assets/brand/pul7sar_reference_master_v1.zip.b64`

contains a literal:

`[...ELLIPSIZATION...]`

at character index `10000`.

CI evidence:

- encoded length: `20021`
- invalid character count: `8`
- permissively decoded SHA: `6d52edb21cccad78545f54a0be3d129e22721a43ab4b5deb1e8a3c1ee60e451a`
- expected approved bundle SHA remains `49ed35398dbb3a62460ff4ee52b7eea7b0db295b165271cef1126484d3d15d62`

This is destructive truncation, not whitespace/separator noise. The missing source bytes cannot be inferred safely.

### Change Set 125 — Exact Brand Asset Truncation Diagnosis

Modified `engine/intelligence/brand_embedded_master.py`:

- known ellipsization/truncation markers are rejected before Base64 decode;
- failure is explicit: `PUL7SAR_EMBEDDED_BRAND_TRANSPORT_TRUNCATED`;
- permissive Base64 fallback remains limited to non-destructive separator noise;
- exact bundle SHA and all member SHA locks remain unchanged.

Modified `tests/test_phase18_brand_embedded_master.py`:

- added a regression test proving literal ellipsization is irrecoverable and fail-closed.

Added:

- `docs/PHASE18_CHANGESET_125_EXACT_BRAND_ASSET_TRUNCATION_DIAGNOSIS.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_125.md`

## Files changed in this pass

### Modified

- `tools/phase18_first_png.py`
- `tests/test_phase18_first_png_preflight.py`
- `engine/intelligence/brand_embedded_master.py`
- `tests/test_phase18_brand_embedded_master.py`

### Added

- `docs/PHASE18_CHANGESET_123_FIRST_PNG_SEMANTIC_PREFLIGHT_LOCK.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_123.md`
- `docs/PHASE18_CHANGESET_124_SHA_LOCKED_BRAND_BUNDLE_TRANSPORT_RECOVERY.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_124.md`
- `docs/PHASE18_CHANGESET_125_EXACT_BRAND_ASSET_TRUNCATION_DIAGNOSIS.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_125.md`

### Deleted

Nothing.

### `main`

Untouched.

## Test status

- Prior baseline run `32741694496` / 1820: `success`.
- Run `32741891562` / 1830: failed only on the corrupted embedded brand study bundle; Change Set 123 tests passed.
- Run `32742363762` / 1841: same underlying asset blocker after integrity-preserving transport recovery attempt.
- Run `32742612700` / 1855: same two brand tests failed, but bounded diagnostics conclusively identified literal `[...ELLIPSIZATION...]` corruption at index 10000. All first-PNG semantic-preflight tests passed.
- Change Set 125 intentionally does not pretend the missing brand bytes have been restored. A subsequent CI run is expected to remain blocked on the two real-bundle tests until a verified original bundle is restored.

## Invariants preserved

Unchanged:

- `main`, `main.py`, Telegram and production publishing;
- Fact Lock, source consensus, story-state integrity;
- identity verification and verified subject rules;
- sentiment and winner/loser neutrality;
- `$0-local` execution;
- FLUX.2 Klein 4B;
- native BF16 requirement;
- seed/canvas locks;
- generated brand/text/score/crest/exact sport-geometry exclusions;
- Base semantic/layer ownership;
- Qwen semantic and HYBRID_SURFACE inspection;
- deterministic football geometry/integrity receipts;
- SemanticPublicationGate;
- Golden visual thresholds (`8.5` minimum / `9.0+` elite target);
- exact publication brand and typography integrity requirements.

The pinned embedded-brand bundle/member SHA values were not changed. No corrupt bytes were accepted as the approved bundle.

No Fake PNG, paid provider, hosted-GPU fallback, precision downgrade, semantic bypass, brand-integrity bypass or publication shortcut was introduced.

## Exact remaining blockers

### 1. Embedded study brand bundle restoration

Current repository text has destructive ellipsization. Safe recovery requires the exact original archive/Base64 bytes from a verified historical source or artifact that reproduce the already pinned bundle and member SHA-256 values. `main` and `claude-test` do not contain this asset. A prior successful editorial visual-study artifact was inspected and contains the rendered study PNG/manifest but not the missing original ZIP members, so it cannot safely reconstruct the exact bundle.

Until the exact original bytes are found/restored, the two real embedded-brand tests must remain failing rather than accept substituted bytes.

### 2. Genuine Golden Hybrid v5 Candidate 1

The current execution environment still does not provide a compatible CUDA/BF16 host. Therefore no new FLUX.2 Klein Candidate 1 PNG is fabricated or claimed.

When a compatible host becomes available, the first-PNG path is now more robust because it proves Qwen semantic runtime/model readiness before any FLUX work or queue mutation.

## Immediate next work

1. Search verified historical artifacts/commits/backups for the exact pre-truncation embedded brand archive and restore only if the pinned archive/member SHAs reproduce exactly.
2. Keep the study bundle publication-blocked even after restoration; it is not the final publication master.
3. Run Candidate 1 only on compatible CUDA/BF16 after semantic preflight.
4. Review Candidate 1 before spending GPU on Seeds 2–4.
5. Preserve provenance → Base semantic/layer gate → deterministic football geometry → receipt-backed Hybrid QA → Qwen HYBRID_SURFACE → SHA-bound Golden review.
6. Final publication remains blocked until the exact user-approved PUL7SAR logo/geometry/font assets are separately SHA-locked and pass publication integrity gates.
