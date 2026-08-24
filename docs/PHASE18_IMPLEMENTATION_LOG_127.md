# PUL7SAR Phase 18 — Implementation Log 127

This log records work on `phase18/story-intelligence` only. `main` was not modified.

## Branch state reviewed

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence`
- Branch state at the start of this pass: `diverged` from `main`, 1052 commits ahead and 101 commits behind.
- No merge, update, force-write or direct modification to `main` was performed.

## Progress made — Change Set 127

Implemented a **GPU Smoke Repository Integrity Gate** so the self-hosted Golden GPU workflow cannot begin CUDA-side work while Phase 18 repository/reference integrity is already invalid.

### Added

- `docs/PHASE18_CHANGESET_127_GPU_SMOKE_REPOSITORY_INTEGRITY_GATE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_127.md`

### Modified

- `.github/workflows/phase18-gpu-smoke.yml`
  - requires `engine/intelligence/pre_gpu_repository_integrity.py` and `tools/phase18_preflight_repository_integrity.py` during branch isolation;
  - runs the CPU-only repository/reference integrity receipt immediately after checkout/branch isolation;
  - executes that gate before CUDA probing, GPU dependency installation, Qwen preparation, FLUX model work, queue mutation or Candidate 1 generation;
  - fails closed unless the compact reference master is member-SHA-pinned, self-contained and study-only, the legacy truncated transport remains non-authoritative, `$0-local` is preserved, and the preflight grants no network/GPU/generation/queue/PNG/publication authority;
  - adds `repository-integrity.json` to the tamper-evident Golden GPU evidence manifest for later replay verification.

- `tests/test_phase18_gpu_smoke_workflow.py`
  - locks repository-integrity ordering ahead of CUDA, dependencies, semantic preflight and generation;
  - locks fail-closed receipt fields;
  - verifies `repository-integrity.json` participates in evidence-manifest construction;
  - preserves existing manual/self-hosted/CUDA/BF16/$0-local/no-provider-secret workflow assertions.

### Deleted

Nothing.

### `main`

Untouched.

## Test status

- Code changes were committed to `phase18/story-intelligence`.
- GitHub Actions result for the new code/test head is pending at the time this log entry is created; no CI success is claimed until a real workflow run completes.
- CPU CI must not fabricate a Golden GPU PNG; any successful CI result is software/integrity verification only.

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
- deterministic football geometry or receipt-backed Hybrid QA;
- SemanticPublicationGate;
- Golden visual thresholds (`8.5` minimum / `9.0+` elite target);
- exact final brand and typography integrity requirements.

No Fake PNG, paid provider, hosted-GPU fallback, secret, precision downgrade, semantic bypass, brand-integrity bypass or publication shortcut was introduced.

## Exact remaining blocker to the first genuine Golden Hybrid v5 PNG

The current tool environment still does not expose a compatible NVIDIA CUDA/BF16 execution host for FLUX.2 Klein 4B. Therefore no new Candidate 1 PNG is fabricated or claimed.

When a compatible self-hosted GPU is available, the protected order is now:

`explicit confirmation → Phase 18 checkout/isolation → CPU repository/reference integrity → CUDA/BF16 proof → Qwen semantic/model preflight → exact FLUX cache/readiness → Candidate 1 → genuine PNG → tamper-evident evidence/replay → provenance → Base semantic/layer ownership → deterministic football geometry → receipt-backed Hybrid QA → Qwen HYBRID_SURFACE → SHA-bound Golden review`

Seeds 2–4 remain unspent until Candidate 1 is visually reviewed.

Final publication remains independently blocked until the exact user-approved PUL7SAR logo/geometry/font assets are SHA-locked and pass the existing brand/typography/publication gates.
