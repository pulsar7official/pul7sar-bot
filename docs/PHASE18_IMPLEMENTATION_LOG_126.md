# PUL7SAR Phase 18 — Implementation Log 126

This log records work on `phase18/story-intelligence` only. `main` was not modified.

## Branch state reviewed

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence`
- Branch was reviewed as diverged from `main`; no merge, update or force-write to `main` was performed.
- PR #1 remained open, Draft and unmerged with `main` as base.
- Starting head for this pass was `7e9bd9f75415bad9d8b3cc697271c4cb765577b0`.
- Baseline GitHub Actions run `32747053259` / 1891 completed with `success` on that head.

## Current repository finding

The active `EmbeddedBrandMasterLoader` no longer consumes the previously diagnosed truncated ZIP/Base64 transport. It uses compact Base85+zlib fragments under `assets/brand/compact_v1`, with both transport SHA-256 and decoded raster SHA-256 values pinned. Its receipt remains self-contained, reference-derived, study-only and `publication_ready=false`.

The historical file `assets/brand/pul7sar_reference_master_v1.zip.b64` still exists in the repository, but it is not authoritative for the active loader. It remains unsuitable as an exact source because its historical truncation cannot be safely reconstructed.

## Progress made — Change Set 126

Implemented a CPU-only **Pre-GPU Repository Integrity Gate** so the next real Candidate 1 GPU window cannot begin while repository-side reference integrity is already broken.

### Added

- `engine/intelligence/pre_gpu_repository_integrity.py`
  - verifies protected Phase 18 branch identity;
  - replays the active compact study-brand transport/member integrity;
  - binds it to the approved source-reference SHA;
  - proves self-contained/no-network/no-generator/no-font-recreation study behavior;
  - proves `study_only=true` and `publication_ready=false`;
  - records the legacy truncated ZIP transport as explicitly non-authoritative;
  - grants no GPU, generation, queue, PNG or publication authority.

- `tools/phase18_preflight_repository_integrity.py`
  - emits the repository-integrity receipt as JSON;
  - performs no inference, model download, network access or GPU work.

- `tests/test_phase18_pre_gpu_repository_integrity.py`
  - current compact-master acceptance;
  - wrong-branch fail-closed behavior;
  - legacy transport non-authority;
  - publication-authority drift rejection;
  - missing/corrupt compact transport rejection without GPU fallback.

- `docs/PHASE18_CHANGESET_126_PRE_GPU_REPOSITORY_INTEGRITY.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_126.md`

### Modified

- `tools/phase18_first_png.py`
  - repository/reference integrity now executes after Golden batch verification and before GPU host qualification, Qwen/FLUX preparation and queue mutation;
  - first-PNG evidence now records the repository-integrity receipt and compact-brand SHA;
  - any attempt to re-authorize the legacy truncated transport or gain network/GPU/generation/publication authority fails closed.

- `tests/test_phase18_first_png_preflight.py`
  - locks the new preflight ordering;
  - verifies the full non-authorizing repository-integrity contract;
  - rejects legacy-transport authority drift.

### Deleted

Nothing.

### `main`

Untouched.

## Test status

- Baseline before Change Set 126: Run `32747053259` / 1891 = `success`.
- Code/test head `b931b994d0c7e317ffa0ea42f3ecdc19d7e3ca07` started Run `32748327053` / 1901. At the time this log was first written the run was still in progress; no CI success is claimed here until GitHub reports a completed successful conclusion.

## Invariants preserved

No changes were made to:

- Fact Lock, source consensus or story-state integrity;
- identity verification and verified-subject rules;
- sentiment and winner/loser neutrality;
- `$0-local` policy;
- FLUX.2 Klein 4B;
- native BF16 requirement;
- seed/canvas locks;
- generated PUL7SAR branding/text/score/crest/exact sport-geometry exclusions;
- Qwen Base/HYBRID_SURFACE semantic inspection;
- deterministic football geometry and integrity receipts;
- SemanticPublicationGate;
- Golden visual thresholds (`8.5` minimum / `9.0+` elite target);
- exact final brand and typography integrity requirements.

The compact reference-derived master remains a study asset, not a publication master. No Fake PNG, paid provider, hosted-GPU fallback, precision downgrade, semantic bypass, brand-integrity bypass or publication shortcut was introduced.

## Exact remaining blocker to the first genuine Golden Hybrid v5 PNG

The available automation/tool environment does not expose a compatible NVIDIA CUDA/BF16 execution host for FLUX.2 Klein 4B. Therefore no new Candidate 1 PNG is fabricated or claimed.

When a compatible host is available, the one-command order is now:

`Golden batch integrity → CPU repository/reference integrity → CUDA/BF16 host qualification → exact Qwen semantic/model preflight → exact FLUX cache/readiness → Candidate 1 durable queue → genuine FLUX PNG → provenance → Base semantic/layer gate → deterministic football geometry → receipt-backed Hybrid QA → Qwen HYBRID_SURFACE → SHA-bound Golden review`

Seeds 2–4 should remain unspent until Candidate 1 is visually reviewed.

Final publication remains independently blocked until the exact user-approved PUL7SAR logo/geometry/font assets are SHA-locked and pass the existing exact brand/typography/publication gates.
