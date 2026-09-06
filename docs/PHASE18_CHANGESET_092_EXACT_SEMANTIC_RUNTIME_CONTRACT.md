# PUL7SAR Phase 18 — Change Set 092

## Exact semantic runtime contract and Pillow public-API regression lock

### Why this change exists
The latest Colab work exposed two separate failure classes around the semantic inspector: runtime version drift and an invalid `PIL.ImageText` import. The bootstrap had already moved to the public Pillow modules (`Image`, `ImageDraw`, `ImageFont`) and exact package pins, but the reusable `Qwen25VLReadinessProbe` still accepted any Transformers 4.x / Pillow 11.x build. That left a gap when the one-command path was invoked outside the bootstrap: a different minor/patch build could pass readiness even though it had never been qualified for the Golden path.

### Added / changed
- `engine/intelligence/semantic_inspector_readiness.py`
  - Declares the exact verified semantic runtime: Transformers `4.56.2`, Pillow `11.3.0`.
  - Fails closed on any version drift, even within the same major line.
  - Retains explicit major-version blockers as diagnostic evidence.
  - Uses only public Pillow imports: `Image`, `ImageDraw`, `ImageFont`.
  - Explicitly documents that `PIL.ImageText` is not a valid readiness probe.
- `tests/test_phase18_qwen_runtime_contract.py`
  - Replaces the previous weak `ImageText` substring assertion with regression checks that forbid importing it.
  - Locks the exact verified Transformers/Pillow versions in both requirements and readiness.
  - Verifies that the Colab bootstrap also uses only the public Pillow modules.

### Safety properties preserved
- No change to `main`, `main.py`, Telegram publishing, or the legacy production image path.
- No paid provider, secret, or network-dependent semantic verifier was introduced.
- FLUX.2 Klein, CUDA/BF16, seed/canvas locks, `$0-local`, Fact Lock, identity, sentiment/neutrality, SemanticPublicationGate, Golden 8.5/9.0 thresholds, deterministic geometry, and exact-brand integrity are unchanged.
- Runtime drift remains a blocker; it is never converted into a semantic pass.

### Why this materially reduces the remaining Golden-PNG gap
A future Candidate 1 run can now enter GPU generation only after the exact semantic runtime used by the bootstrap is also accepted by the reusable readiness gate. This removes a class of false-positive preflights where a merely same-major dependency build could pass before Qwen inference. It also permanently regression-locks the invalid Pillow symbol that caused the observed Colab failure.

### Remaining blocker
No new Golden PNG is claimed by this change set. The first genuine Candidate 1 under the latest hybrid/evidence/runtime architecture still requires a compatible CUDA/BF16 execution host and a successful exact-runtime Qwen preflight.