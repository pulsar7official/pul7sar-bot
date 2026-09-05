# PUL7SAR Phase 18 — Change Set 179

## Golden v6 handoff contract repair

### Goal

Remove deterministic CPU-side blockers that still prevented Golden Editorial v6 Candidate 1 from reaching genuine GPU execution, without relaxing any factual, identity, sentiment, zero-cost, semantic-publication, or visual-quality gate.

### Evidence reviewed

Story Intelligence Verification run `33001945155` completed with failure in `Syntax and discover validation` after running 1,246 Phase 18 tests. Companion Phase 18 visual workflows on the same branch head completed successfully.

The failure clustered around four migration boundaries:

1. Golden v6 composition-map metadata (`focal_anchor`, `copy_negative_space`, `brand_quiet_zone`) existed in the provider-neutral package but was dropped when compiling the local backend handoff, causing Golden batch/smoke/verifier cascades.
2. Provider positive reframes did not preserve two strict Golden prompt markers (`no specific identifiable real venue`, `approaching rather than already decided`) and one new v6 regression test correctly rejected wording that still contained `full playing surface`.
3. The Colab Golden v6 notebook omitted explicit `$0-local`, publication-blocked, and strict 8.5/9.0+ review statements required by the current contract.
4. The current Original Scene bridge already classifies the combined `no full-pitch master shot or central broadcast pitch framing` claim fail-closed into the approved contextual-turf and oblique-camera constraints; no relaxation was needed there.

### Implementation

#### Local handoff metadata continuity

`engine/intelligence/local_backend_execution.py` now propagates the locked Golden v6 composition-map fields into every local backend request:

- `focal_anchor`
- `copy_negative_space`
- `brand_quiet_zone`

This keeps Golden batch generation, smoke coordination, provenance, and later semantic continuation bound to the exact story-first composition selected before renderer execution.

#### Provider constraint compatibility

`engine/intelligence/provider_prompting.py` now:

- includes the exact fail-closed marker `No specific identifiable real venue is permitted` inside the approved non-identifying-venue reframe;
- describes PREVIEW state as `approaching rather than already decided` while still keeping the outcome unresolved;
- removes the phrase `full playing surface` from the contextual-turf positive reframe and instead states that turf must never become the primary subject.

No forbidden constraint is dropped. The compiler remains fail-closed for unknown translations.

#### Colab contract clarity

`notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb` now explicitly states:

- `$0-local` only;
- publication remains blocked until downstream gates pass;
- strict Golden floor remains `8.5`;
- `9.0+` is the elite target;
- exact branding and typography are deterministic downstream layers;
- semantic/runtime/integrity failures remain fail-closed for publication.

T4 FP16 remains engineering preview only and cannot satisfy Golden-reference precision.

### Added

- `docs/PHASE18_CHANGESET_179_GOLDEN_V6_HANDOFF_CONTRACT_REPAIR.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_179.md`

### Modified

- `engine/intelligence/local_backend_execution.py`
- `engine/intelligence/provider_prompting.py`
- `notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb`

### Deleted

- None.

### Gates preserved

Unchanged and fail-closed:

- Fact Lock / source consensus / sports-state integrity.
- Entity and Identity Verification.
- Sentiment, neutrality, and loser-respect rules.
- `$0-local`; no paid provider or hosted-GPU fallback.
- Pinned FLUX/Qwen revisions and runtime fingerprinting.
- Native BF16 Golden path and resource/offload qualification.
- Candidate/request/seed/canvas/SHA and execution-resource provenance locks.
- No generated platform branding, readable typography, exact facts/numbers, entity marks, or exact sport geometry.
- Golden Editorial v6 story-first composition map.
- PREVIEW remains `context_only`; deterministic pitch replacement remains false.
- Qwen semantic/layer-ownership gates.
- Golden `8.5` minimum / `9.0+` elite thresholds.
- Exact Brand Integrity, Typography Integrity, and SemanticPublicationGate.
- Seeds 2–4 remain unauthorized before genuine Candidate 1 visual acceptance.

### Genuine PNG status

No genuine Golden Editorial v6 Candidate 1 PNG is fabricated or claimed by this change set. Genuine generation still requires a compatible zero-cost CUDA host that satisfies the existing native-BF16, VRAM, RAM, offload, pinned-model, runtime-fingerprint, and semantic-verifier gates.
