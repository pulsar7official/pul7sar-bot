# PUL7SAR Phase 18 — Pre-Mortem, Artifact Integrity & Semantic QA

## Goal
Phase 18 must anticipate predictable failures before they become published visuals. A generated PNG is engineering evidence only; publication requires independent proof across facts, composition ownership, artifact identity, semantic visual quality, branding, typography and final export.

## New safeguards

### `SportsStoryIntegrityGuard`
Catches contradictions between individually plausible fact slots, including:
- winner not participating in the match,
- draw with a winner,
- subject-win status conflicting with explicit winner,
- same transfer origin/destination,
- confirmed-transfer story with pending status,
- rumour with final-transfer status,
- eliminated entity eliminating itself,
- conflicting qualification/champion identities,
- duplicate schedule opponents.

### `VisualPremortemGate`
Converts known risks into explicit actions:
- `PROCEED`
- `ENGINEERING_PROOF_ONLY`
- `REPLAN_TO_SAFE_FALLBACK`
- `BLOCK`

GPU is blocked for errors generation cannot repair, such as unverified identity, missing deterministic geometry, non-final winner state, or exact-data stories incorrectly routed to unconstrained generation. Missing final brand recipe or semantic visual inspection still permits an engineering proof but never publication.

### Dynamic brand entity integrity
Contextual `7 + pulse` color now requires palette evidence for the exact dominant entity. A palette record belonging to a different club cannot color the brand and falls back to PUL7SAR red.

### Hybrid artifact SHA receipts
`FootballHybridCompositionReceipt` records SHA-256 for input and output PNGs. `HybridArtifactIntegrityGate` re-hashes the live files so a stale/tampered image or stale receipt cannot masquerade as current deterministic geometry evidence.

`HybridVisualEvidenceBuilder` now counts deterministic football geometry as complete only when the receipt and live files still pass artifact-integrity validation.

### Semantic visual verdict
`SemanticVisualVerdict` distinguishes three states:
- `PASS`
- `FAIL`
- `NOT_INSPECTED`

This prevents missing inspection from being interpreted as a clean image.

Required non-identity checks:
- readable generated text absent,
- generated platform branding absent,
- fake entity marks absent,
- one continuous scene,
- severe visual defects absent,
- usable subject/focal framing.

Identity is separate and required only for identity-sensitive stories.

### Optional local Qwen2.5-VL inspector
`Qwen25VLSemanticInspector` is lazy-loaded and optional. It uses the local `Qwen/Qwen2.5-VL-3B-Instruct` model through the Transformers image-text-to-text pipeline and requests one strict JSON QA schema. FLUX and the visual inspector are intended to run sequentially so GPU memory is released between models.

The model is a semantic QA component, not a source-of-truth extractor. Low-confidence or malformed responses fail closed through `SemanticVisualVerdictGate`.

### Deterministic typography renderer
`PillowTypographyRenderer` renders already-approved `TextLayout` objects with an approved local font reference. It can verify font SHA-256 and checks actual Pillow text metrics before rendering. It refuses clipping or silent resizing.

### Publication readiness
`PublicationReadinessGate` requires all independent approvals:
1. pre-mortem publication permission,
2. hybrid artifact integrity,
3. semantic visual-inspection readiness,
4. HybridVisualQualityGate approval,
5. semantic publication approval,
6. Golden visual-quality approval,
7. final export authorization.

Any single failure returns `PUBLICATION_BLOCKED`.

## Colab one-command progression
`tools/phase18_colab_one_command.py` now supports optional semantic inspection:

```python
%cd /content/pul7sar-bot
%run tools/phase18_colab_one_command.py --candidate 1 --force --semantic-inspection qwen
```

The flow updates the branch, runs all CPU Phase 18 tests, generates one atmosphere base, applies deterministic football geometry, verifies artifact hashes, optionally runs semantic inspection, runs receipt-backed Hybrid QA and displays the hybrid proof.

Even with semantic inspection enabled, the current Golden v5 proof remains `publication_ready=false` until approved deterministic brand geometry and deterministic typography are composed and Golden/final publication gates are satisfied.

## Principle
When a risk can be predicted, PUL7SAR should change ownership or production mode instead of simply adding more prompt text.
