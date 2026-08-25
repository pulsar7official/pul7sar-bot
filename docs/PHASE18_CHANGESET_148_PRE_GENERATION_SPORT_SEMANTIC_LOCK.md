# PUL7SAR Phase 18 — Change Set 148
## Pre-Generation Sport Lock + Semantic Lock

Status: benchmark-only / publication-ready = false.

### Why this change exists
The first successful zero-cost CPU cross-family synthesis proved that the new image path can produce materially richer photographic worlds than the deterministic Blender studies. Visual inspection also exposed a critical semantic failure mode: a RESULT_STATEMENT scene could drift into American football, and DATA_MONUMENT could drift into a natural rocky/sports landscape. A visually attractive image is still a failed editorial image when the sport or family meaning is wrong.

### Architectural decision
The generative backend no longer owns either:
1. the sport identity; or
2. the editorial-family meaning.

Before text-to-image inference, PUL7SAR now constructs a fail-closed `PreGenerationSceneLock` containing:
- exact sport lock (`association_football` for the current benchmark),
- family-specific semantic anchor,
- required visual cues,
- forbidden visual cues,
- exact layers reserved for deterministic/verified post-composition.

The locked contract is prepended to the atmosphere prompt. This is not a claim that prompting alone guarantees correctness; it is the first enforcement layer. Generated output remains `publication_ready=false` and must later pass visual/semantic inspection and deterministic composition gates.

### Family locks
- RESULT_STATEMENT: completed association-football match atmosphere; forbids gridiron/American-football semantics and invented score digits.
- TRANSFER_SIGNATURE: football transfer-arrival world without inventing a player or signing ceremony.
- VERIFIED_SUBJECT_NEWS: football editorial environment with an empty hero zone; verified person remains a separate verified layer.
- DATA_MONUMENT: architectural information pedestal/monument with blank exact-data surfaces; natural rock formations and generic outdoor landscapes are explicitly forbidden.
- EVENT_EDITORIAL: pre-event association-football anticipation with no implied outcome.
- TACTICAL_BOARD: remains deterministic-first and cannot enter the generative lock path.

### Benchmark integration
`tools/phase18_cpu_cross_family_synthesis.py` now uses the lock for every generative family and records sport lock, semantic anchor, required cues and forbidden cues in the v2 manifest.

### Tests
`tests/test_phase18_pre_generation_scene_lock.py` protects:
- association-football lock across all five generative families,
- American-football/gridiron rejection,
- Data Monument anti-rock/anti-landscape semantics,
- verified-subject empty hero-zone ownership,
- deterministic-only Tactical Board behavior.

### Scope / invariants
- No `main` or `main.py` modification.
- No production publishing path modification.
- No paid service introduced.
- No exact score/statistic/person/crest/logo is delegated to the image model.
- This change does not authorize additional Golden seeds/candidates.
- Human visual acceptance remains mandatory before promotion.
