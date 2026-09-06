# PUL7SAR Phase 18 — Change Set 093: Qwen Process Isolation

## Purpose
The latest Colab work showed that semantic QA could fail inside the Qwen runtime after FLUX had already produced a genuine base image. Python exceptions were recoverable, but a native CUDA/process kill or low-level model crash could still terminate the Golden orchestration process before it had a chance to report a controlled blocker or display a fail-closed engineering proof.

Change Set 093 isolates each Qwen semantic inspection stage in a fresh spawned Python process. This is a runtime-hardening change only; it does not weaken semantic-publication, layer-ownership, identity, factual, neutrality, zero-cost or Golden visual-quality gates.

## Added
- `tests/test_phase18_qwen_process_isolation.py`
  - proves verdict evidence can cross the process boundary without changing state/confidence/detail;
  - proves process isolation is enabled by default;
  - proves direct in-process inference requires an explicit configuration override.

## Modified
- `engine/intelligence/qwen25_vl_inspector.py`
  - Qwen inference now runs in a fresh `multiprocessing` spawn by default;
  - each stage writes a bounded normalized JSON receipt to a temporary local file;
  - parent orchestration detects timeout, abnormal exit, missing receipt, malformed receipt and child-side Python failure as `Qwen25VLInspectionError`;
  - the child uses the same model, image limit, deterministic generation, semantic schema and evidence contract as before;
  - model/CUDA memory is reclaimed when the child exits, so base-scene and hybrid-surface inspection do not retain one long-lived Qwen pipeline on a T4;
  - verifier ID advanced to `qwen2.5-vl-3b-local-v5-isolated-t4` so evidence from the isolated runtime cannot be confused with earlier verifier builds;
  - after CI detected semantic-equivalent prompt wording drift, the existing regression-locked phrases for `model-generated` exact `pitch/court/rink` markings and `Deterministic pitch markings are expected` were restored without weakening inspection logic.

## Tested
- Initial CI Run `32653096283` passed syntax and all new process-isolation tests but exposed regression-locked Qwen prompt wording drift.
- Follow-up Run `32653213680` reduced the issue to one remaining legacy `model-generated` wording marker; the new process-isolation tests continued to pass.
- Final code verification Run `32653277453` (run 1276): **SUCCESS**. All 649 discover-based Phase 18 tests passed, followed by completion audit, production isolation, Golden Hybrid v5 handoff/batch build, batch integrity verification and current-contract assertions. CPU CI correctly produced no fake visual proof.

## Deleted
Nothing.

## Safety invariants preserved
- `main` and `main.py` are untouched.
- FLUX.2 Klein 4B, BF16, Golden seeds/canvases and `$0-local` are unchanged.
- Semantic evidence remains mandatory for publication and Golden approval.
- A Qwen subprocess crash is an inspection failure, never a semantic pass.
- Identity remains separate and fail-closed.
- Deterministic football geometry, exact branding, typography and final publication gates are unchanged.
- No paid provider, secret, fake PNG, fake benchmark or fabricated GPU result is introduced.

## Why this materially reduces the remaining gap
A Python-level try/except cannot recover when the semantic model process is killed by CUDA/runtime/native failure. Process isolation gives the Golden controller a stable boundary: a failed child becomes evidence of unavailable semantic QA instead of destroying the entire orchestration process. This allows the existing development-only engineering-proof fallback to remain observable while publication stays blocked, and it prevents Qwen model memory from accumulating across the two semantic stages.

## Remaining blocker
No new Golden Hybrid v5 Candidate 1 PNG is claimed by this change set. A compatible CUDA/BF16 Colab or other GPU host is still required to execute the real FLUX -> Qwen base inspection -> deterministic football composition -> Qwen hybrid inspection path. The next genuine run should use Candidate 1 only before any GPU time is spent on seeds 2–4.
