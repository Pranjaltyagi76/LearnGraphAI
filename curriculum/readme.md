# Reviewed versioned artifacts

This directory is the Phase 0 source of truth now published in the separate immutable Phase 3 analysis package. The legacy Phase 1 payload is retained unchanged.

| Artifact | Reviewed content |
| --- | --- |
| graph.v1.json | Twelve assessed concepts, seventeen scoped prerequisite edges, entry assumptions and rationales. |
| catalog-slice.v1.json | Twelve questions at activity version 2 plus two lessons; sixty more questions remain for Phase 4. |
| profiles.v1.json | Four explicit synthetic seed definitions, nineteen total seed events. |
| model-config.v1.json | Initial evidence/scoring/plan policy; not empirically calibrated. |
| [review.md](review.md) | Engineering decisions, per-item review and fresh-loop limits. |

[Release manifest](../contracts/release-manifest.json) binds exact LF file bytes and generated schema. Phase 2 now validates compatible package bytes offline. Phase 3 publication/activation is complete: the new immutable byte package and compatible API/frontend are verified, while legacy routes/release remain available. Do not overwrite [phase1.json](../backend/data/phase1.json), its hash, or Supabase data during this review.

Verified local commands from backend/ using the existing Windows virtual environment:

```powershell
.\.venv\Scripts\python.exe -m scripts.freeze_phase0
.\.venv\Scripts\python.exe -m scripts.check_phase0
.\.venv\Scripts\python.exe -m pytest -q
```

From repository root, `node contracts/check-hashes.mjs` independently verifies canonical UTF-8, hashes and storage keys. CI runs equivalent checks with locked dependencies on Linux. The schema/manifest writer's --write option creates missing artifacts only; it refuses existing differences. Later changes require deliberate artifact/contract version review, not silent regeneration under an old version.

These authored files alone create no service, secret, billing configuration or learner persistence. Phase 2 now consumes them in an implemented offline engine and measured public synthetic audit; see the [model card](../evaluation/model_card.md). Original project content has no selected public license; educator/psychometric validation is not claimed.

The file manifest keeps its original reviewed-draft status as freeze provenance. Database publication is a separate immutable row with a recorded publication timestamp and wrapper hash; it does not edit any frozen source file. [Published release proof](../context/evidence/phase3_release.json) records both hashes, runtime verification and the unchanged legacy row. The remaining sixty questions and educator validation remain open.
