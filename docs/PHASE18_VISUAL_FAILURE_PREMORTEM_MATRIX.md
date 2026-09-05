# PUL7SAR Phase 18 — Visual Failure Pre-Mortem Matrix

This is a design-time failure catalog for Story-to-Visual production. The goal is not to wait for a bad image and then patch its prompt. The pipeline should predict the failure class, prove the required capability, choose a safe fallback, or block the path before publication.

## 1. Source / fact failures

| Failure | Prevention | Safe fallback |
|---|---|---|
| Missing required event fact | EventFactSchema + Fact Lock | Do not create visual plan |
| Contradictory facts | SportsStoryIntegrityGuard | Block and re-resolve source |
| Winner is not a participant | Cross-field integrity | Block |
| Draw carries a winner | Cross-field integrity | Default red; remove winner framing |
| Final transfer classified while status is pending | Event/status consistency | Downgrade to transfer-rumour treatment |
| Rumour carries final-signing status | Event/status consistency | Reclassify before visual planning |
| Eliminated side accidentally becomes the visual winner | Dominant-entity semantics | Require explicit eliminating entity |
| Exact score/date/amount is absent | Exact slot policy | Omit exact value; never invent it |

## 2. Editorial-angle failures

| Failure | Prevention | Safe fallback |
|---|---|---|
| Strongest text angle is visually unsafe | VisualAwareEditorialAngleSelector | Choose slightly weaker but reliable visual angle |
| Too many important subjects | SceneComplexityPolicy + pre-mortem | One hero + one secondary subject |
| Story requires invented ceremony/moment | Angle hard blocker | Verified-asset editorial composition |
| Sensitive injury/controversy becomes sensational | Event-specific production mode | Restrained verified-asset treatment |
| Exact-data story routed to diffusion | Production-mode blocker | Deterministic composition |

## 3. Dynamic-brand failures

| Failure | Prevention | Safe fallback |
|---|---|---|
| Two clubs exist and wrong club colors 7/pulse | StoryDominantEntityResolver | Use objective winner/destination/champion |
| Match is live but winner color is applied | Final-state guard | Default PUL7SAR red |
| Transfer destination is used before deal is final | Confirmation-state guard | Default red / rumour treatment |
| Entity palette is unverified | EntityThemeResolver | `#E10600` default red |
| Palette belongs to another entity | Explicit entity-palettes map | Reject contextual color |
| Weak contrast makes contextual color unreadable | DynamicBrandContrastResolver | Preserve color + minimal keyline |
| AI invents platform wordmark | Brand-name redaction + post composition | Generator receives no protected platform token |
| Wrong logo structure is used | DynamicBrandGeometryRegistry | publication_ready=false until approved recipe |

## 4. Identity failures

| Failure | Prevention | Safe fallback |
|---|---|---|
| Wrong athlete likeness | Verified identity asset / similarity evidence | Non-identifying composition |
| Two similar players are swapped | Identity lock per subject | Simplify to one verified hero |
| Generic generated face is mistaken for real subject | Hybrid layer ownership | Verified asset layer only |
| Identity verification capability unavailable | Pre-mortem hard block | Engineering proof only or non-person scene |

## 5. Sport-geometry failures

| Failure | Prevention | Safe fallback |
|---|---|---|
| Model invents football markings | Deterministic 105m × 68m renderer | Opaque surface replacement |
| Pitch width/length perspective is implausible | Projective placement presets | Validated camera preset |
| Surface renderer is not implemented for sport | GeometryCapabilityRegistry | Remove surface or block exact tactical visual |
| Generated old markings remain visible underneath | Opaque alpha=255 replacement | Reject receipt if not opaque |
| Geometry receipt is stale or tampered | SHA-256 artifact integrity | Recompose from verified base |

## 6. Generation failures

| Failure | Prevention | Safe fallback |
|---|---|---|
| Collage / split scene | Unified-scene contract | Reject candidate |
| Pseudo text appears | Generic unbranded prompt + semantic inspection | Reject candidate |
| Fake crest/logo appears | Layer ownership + semantic inspection | Reject candidate |
| Severe anatomy/object defect | Semantic visual inspection | Regenerate / switch verified-asset mode |
| Base scene ignores reserved clean area | Protected-region inspection | Regenerate with simpler composition |
| Base scene includes exact sport surface | Hybrid contract | Opaque deterministic replacement where supported |
| Model result is aesthetically weak but technically valid | Golden visual quality gate | Select another candidate / re-angle |

## 7. Typography / exact-data failures

| Failure | Prevention | Safe fallback |
|---|---|---|
| Misspelled name or score | Deterministic typography only | Never allow image model to write it |
| Headline overflows | DeterministicTypographyEngine | Reduce size within approved bounds or block |
| Silent truncation changes meaning | No silent truncation policy | Rephrase approved short headline |
| Text placed outside safe box | FinalExportGate geometry check | Block export |
| Wrong font reference | FontReference integrity | Block export |

## 8. Artifact / runtime failures

| Failure | Prevention | Safe fallback |
|---|---|---|
| Old candidate is displayed as new | request/seed/model/SHA identity matching | Never reuse legacy result without hash match |
| Hybrid PNG changed after composition | output SHA-256 receipt validation | Reject artifact |
| Base PNG changed after receipt | input SHA-256 validation | Reject and recompute |
| Wrong Git branch | protected branch assertion | Stop before changes/GPU |
| CPU regression exists | discover-based Phase 18 validation | Block GPU |
| Wrong manifest version | Golden contract assertion | Block stale run |
| Paid provider accidentally selected | `$0-local` cost lock | Block request |
| Incompatible GPU/dtype | readiness + BF16 lock | Stop before model load |

## 9. Publication failures

Publication readiness is deliberately conjunctive. A PNG cannot be called ready because one gate passed.

Required independent approvals:

1. pre-mortem publication permission,
2. automatic semantic visual inspection capability and result,
3. HybridVisualQualityGate,
4. semantic publication verification,
5. Golden visual-quality approval,
6. final export authorization.

`PublicationReadinessGate` returns `PUBLICATION_READY` only when all six agree.

## Principle

When a failure is predictable, PUL7SAR should not ask a generative model to be more careful. It should change ownership, simplify the scene, use a verified/deterministic layer, choose another editorial angle, or block the output.
