# Reviewed draft artifacts

This directory is the Phase 0 source of truth for the next compatible release, **not** the currently published Phase 1 payload.

| Artifact | Reviewed content |
| --- | --- |
| graph.v1.json | Twelve assessed concepts, seventeen scoped prerequisite edges, entry assumptions and rationales. |
| catalog-slice.v1.json | Twelve questions at activity version 2 plus two lessons; sixty more questions remain for Phase 4. |
| profiles.v1.json | Four explicit synthetic seed definitions, nineteen total seed events. |
| model-config.v1.json | Initial evidence/scoring/plan policy; not empirically calibrated. |
| [review.md](review.md) | Engineering decisions, per-item review and fresh-loop limits. |

[Release manifest](../contracts/release-manifest.json) binds exact LF file bytes and generated schema. Publication remains Phase 2 work: validate and aggregate into a new immutable release, retain legacy routes/release, then activate compatible API/frontend code. Do not overwrite [phase1.json](../backend/data/phase1.json), its hash, or Supabase data during this review.

Verified local commands from backend/ using the existing Windows virtual environment:

```powershell
.\.venv\Scripts\python.exe -m scripts.freeze_phase0
.\.venv\Scripts\python.exe -m scripts.check_phase0
.\.venv\Scripts\python.exe -m pytest -q
```

From repository root, `node contracts/check-hashes.mjs` independently verifies canonical UTF-8, hashes and storage keys. CI runs equivalent checks with locked dependencies on Linux. The schema/manifest writer's --write option creates missing artifacts only; it refuses existing differences. Later changes require deliberate artifact/contract version review, not silent regeneration under an old version.

No service, secret, billing configuration, learner persistence, diagnosis engine, or model benchmark is created by these files. Original project content has no selected public license; educator/psychometric validation is not claimed.
