# Architecture

**Status:** Phases 0–3 passed. Phase 4 implements the full content/UI release with explicit retained-slice support; final production verification passed. **Date:** 21 November 2026. See [full review](../curriculum/full-review.md) and [roadmap](phasewise_roadmap.md).

## 1. Architecture goals

- Preserve a real frontend/API/database boundary while staying within free quotas.
- Make grading, evidence eligibility, diagnosis, and recommendations independently testable and deterministic.
- Keep browser-controlled synthetic state separate from canonical curriculum data and future authenticated records.
- Keep research packages, data, and training outside runtime bundles.
- Make failures visible and recoverable without payment.

## 2. Deployment topology

| Unit | Planned technology | Boundary |
| --- | --- | --- |
| Learner UI | Next.js, TypeScript, Tailwind, accessible components | Vercel Hobby project rooted at `frontend/`. |
| Analysis API | Supported pinned Python, FastAPI, Pydantic, Postgres driver; NetworkX if useful | Second Vercel Hobby project rooted at `backend/`. |
| Canonical persistence/quota guard | Supabase Free Postgres | Transaction-pooled runtime access; separate migration/admin access. |
| Research | Local Python with NumPy/pandas/scikit-learn as needed | Offline environment; compact result artifacts only enter the public application. |

Two Vercel projects do not multiply shared quotas. Phase 1 verified native FastAPI packaging and the existing slice. Reviewed root-level curriculum/contracts are owner publication inputs, not implicit files inside the backend deployment root; Phase 2 verifies a compatible five-artifact byte package through Release; its offline loader reads owner publication inputs. Phase 3 wires that exact byte package to canonical storage and activated the API before releasing the frontend. Render is needed only if the preferred path fails its viability gate.

No microservices split, Redis, queue, graph database, hosted MLflow, AI gateway, LLM, or code-execution service is required. Add dependencies only for a concrete requirement and verified free capability.

## 3. Planned module ownership

### Frontend

| Area | Responsibility |
| --- | --- |
| `app/` | Routing, landing/demo pages, public methodology/evaluation views. |
| `components/dashboard/` | Estimates, evidence counts, timeline, consistent analysis display. |
| `components/graph/` | React Flow visualization and accessible list equivalent. |
| `components/diagnosis/` | Evidence IDs, paths, alternatives, abstention, and plan reasons. |
| `components/practice/` | Authored options, pending/feedback states, distinct reassessment. |
| `lib/api/` | Versioned contract client, bounded retries, safe error mapping. |
| `lib/sandbox/` | Local storage, revisions, event IDs, reset, cross-tab conflict handling. |
| `public/examples/` | Explicitly prerecorded, versioned synthetic result artifacts. |

The browser sends responses, not authoritative scores. It must not recompute an independent competing diagnosis implementation. Components consume one analysis bundle, so stale partial data cannot leak between views.

### Backend

| Area | Responsibility |
| --- | --- |
| `app/main.py` | FastAPI creation/lifecycle; verified deployment entrypoint. |
| `app/api/v1/` | Request/response boundary, route composition, status codes. |
| `app/contracts.py` | Implemented offline strict DTOs, normalization/hash helpers and storage-record validation; future handlers/services reuse them. |
| `app/core/` | Configuration, safe errors, time budgets, quota orchestration. |
| `app/db/` | Canonical repositories, small pooled connections, narrow quota operation. |
| `app/services/grading/` | Grade catalog options; derive authoritative metadata. |
| `app/services/replay/` | Normalize/deduplicate/order events, calculate digest, derive eligible evidence. |
| `app/services/estimates/` | Baseline counts, smoothing, evidence states. |
| `app/services/graph/` | DAG validation, bounded ancestor lookup, shortest paths/topological order. |
| `app/services/diagnosis/` | Evidence gates, target/upstream scoring, alternatives/abstention. |
| `app/services/recommendation/` | Assessment/remediation selection, hard constraints, ranking/exhaustion. |
| `app/services/explanation/` | Template wording from validated evidence only. |

These directories are intended responsibilities, not a mandate for dozens of empty packages. Start with small cohesive modules and extract boundaries when implementation warrants it.

### Source and research

- `curriculum/`: authored immutable concepts, edges, activities/options, and revision metadata.
- `data/synthetic/`: compact canonical seeds only; no personal records.
- `research/`: notebooks and separately locked offline dependencies.
- `evaluation/`: independent scenarios, split manifests, measured small result artifacts.
- `scripts/`: content/graph validation, repeatable seeding, generation, and evaluation entrypoints.

## 4. Dependency rules

```text
API routes -> application orchestration -> pure domain services
                                  |
                                  -> repository/quota interfaces -> Postgres

Local evaluators -> the same pure domain services + independent scenarios
Frontend -> versioned public API contracts; no direct privileged database access
```

- Domain estimation/scoring functions do not import FastAPI, database clients, UI code, or notebooks.
- Repositories return typed versioned canonical data; services do not read arbitrary environment state during scoring.
- Time, random seeds, and model/configuration must be explicit where relevant. P0 scoring is deterministic; runtime wall-clock time is not an evidence feature.
- Research may call production domain functions; production must not import research pipelines or labels.
- No circular service dependencies. The orchestrator owns order and builds the final bundle.
- Cache immutable canonical data by full version identifier only. Cache loss must not change output or bypass quota checks.

## 5. Published versions and state

Every reproducible result identifies seed, graph, catalog, and model/configuration versions plus a semantic input digest. Preserve historical published versions needed by public examples. Do not modify a question's grading under an unchanged version.

Draft and published content are distinct. [Release manifest](../contracts/release-manifest.json) hashes LF artifact bytes and the compatible identity; [protocol](../contracts/protocol.md) defines activation. Owner publication can retain the bounded JSONB release table rather than creating every proposed logical table. A migration or local artifact freeze does not publish content. Keep the active Phase 1 release/routes alongside future analysis releases for older clients.

P0 stores no visitor events in shared learner tables. Later owned persistence is a separate design migration: auth, owner-scoped records, unique event IDs, consistent recomputation, retention/deletion, and mentor assignments must arrive together.

## 6. Decision records

| ID | Decision | Reason / reconsider only when |
| --- | --- | --- |
| ADR-001 | Next.js plus lightweight FastAPI | Preserves Python analysis and a polished UI; reconsider hosting only after measured free-path failure. |
| ADR-002 | Two Vercel projects, Supabase Free | Simple explicit boundaries; validate packaging/pooling/free eligibility before full development. |
| ADR-003 | Local anonymous sandbox, immutable seeds | Avoids shared-demo corruption and premature account complexity; reconsider for complete P1 ownership/sync. |
| ADR-004 | Pure deterministic baseline and templates | Explainable, testable, and no paid inference; research alternatives require benchmark evidence. |
| ADR-005 | Versioned DAG, no graph database | Twelve concepts need bounded traversal, not extra infrastructure. |
| ADR-006 | Shared Postgres quota counters | Cross-instance enforcement without another service; must be atomic and fail closed. |
| ADR-007 | Separate runtime/dev/research dependencies | Keeps builds and cold starts practical; measure every runtime addition. |
| ADR-008 | No arbitrary code execution or public account flow in P0 | Authored questions prove the loop without judge/email/security infrastructure. |
| ADR-009 | Honest static examples during outages | Portfolio remains inspectable while clearly disclosing live unavailability; does not replace a passing live release gate. |
| ADR-010 | Release-scoped future metadata, retained bootstrap routes | Prevent a new catalog/schema from breaking cached Phase 1 clients; activate full analysis separately. |
| ADR-011 | IndexedDB transactional revision checks; advisory BroadcastChannel | Atomic cross-tab updates and persisted pending snapshots without unsafe localStorage locks or another service. |
| ADR-012 | Frozen public synthetic audit, explicit exposure limits | Labels are separate from inference and never generated by diagnosis output; public cases do not establish blind generalization. |

Decision status is **accepted**; Phase 1 frontend/API builds, isolated PostgreSQL CI, hosted Supabase TLS/privileges/quotas, idempotent reseeding, and live browser grading passed. Pure domain services and offline evaluation are verified; HTTP/browser integration now passes; full disaster restoration/rollback and later features remain unverified. New decisions should record date, trigger/evidence, alternatives, requirement impact, cost impact, and corresponding changes to PROJECT/requirements.

## 7. Security boundaries

- Browser data is untrusted. Backend schema/grading validation is authoritative for the demo result.
- CORS does not provide authentication or stop non-browser abuse.
- RLS/grants protect exposed data; privileged roles can bypass RLS and require explicit API checks.
- Migration/admin secrets never enter runtime public responses or frontend builds.
- Public authored grading source is inspectable; this is not a confidential examination platform.
- Quota state is operational metadata, with rotating hashed identifiers and bounded retention.

## 8. Verification responsibilities

| Boundary | Required evidence |
| --- | --- |
| Browser → API | Live deployed happy path, pending/error states, stale-response handling, no forged grades. |
| API → Postgres | Pooling/TLS, published-version reads, denial of public canonical writes, atomic quota concurrency. |
| Replay → domain services | Deterministic fixtures and meaningful independent scenario tests. |
| Domain → UI | Same digest/versions across views, unknown/weak distinction, valid evidence paths. |
| Source → deployment bundle | Runtime-only dependencies, correct shared-source inclusion, measured bundle/cold behavior. |
| Research → published artifact | Manifest provenance, independent holdout, no future-answer leakage or fake metrics. |

Use [benchmark.md](benchmark.md), [performance_review.md](performance_review.md), and [deployment.md](deployment.md) for the actual validation procedures.

## 9. Implemented Phase 2 ownership

`app/release.py` verifies compatible identity/artifact hashes, schema/policy bytes, catalog/seed references and graph validity; `load_release` is the offline file adapter. A future repository can supply the same exact byte mapping without domain filesystem access. `graph.py`, `replay.py`, `diagnosis.py`, `recommendation.py`, `analysis.py`, `validation.py` and `explanation.py` are small implemented modules rather than the proposed empty package tree above. Domain functions take explicit data/configuration/time, with no provider, environment, HTTP or scenario-label dependency.

`backend/evaluation/` owns offline metrics, independent plan checks and split orchestration. Production does not import it. CLI entrypoints are `scripts.analyze` and `scripts.evaluate`. No runtime/dev dependency was added. [Measured source and output hashes](../evaluation/results/phase2-v2/manifest.json) bind this implementation; CI reproduces the saved results. Live publication and repository/route composition now pass the Phase 3 integration gate; Phase 1 data and routes retain their existing contract.

## 10. Implemented Phase 3 boundary

`app/published.py` verifies a bounded JSONB wrapper containing the frozen manifest, five base64 raw-file byte strings and an optional validated measured evaluation summary. `Database.fetch_release` verifies stored semantic content hashes; `analysis_release` caches only the configured immutable package after validation. Public projections include four synthetic profiles, their selected seed and safe activities; no future question key/explanation is returned. `main.py` composes the pure engine with bounded receive/schema checks, the existing shared quota operation and explicit receipt time. Unknown release tuples fail with 409. Legacy routes and RELEASE_ID retain their contracts; ANALYSIS_RELEASE_ID independently activates the new row.

`frontend/lib/generated/` comes from the frozen schema, not hand-maintained competing types. `protocol.ts` checks structures/references and canonical request identity; `sandbox.ts` owns IndexedDB transactions, complete observed-record comparisons, pending snapshot recovery, cache verification and explicit session fallback. All hashing/validation completes before write transactions. BroadcastChannel carries only hints; transaction checks and focus reads retain correctness without it. `learning-workspace.tsx` orchestrates one submission per tab and generation guards; `learning-evidence.tsx` renders server evidence without another diagnosis/grading model. The original connection preview remains available on the landing page; /learn exposes the completed bounded learning loop.

[Live verification](evidence/phase3_live.json) proves browser → production API → canonical database → response rendering in two fresh browser processes; [release evidence](evidence/phase3_release.json) records exact source/deployments and runtime privileges. Twenty-three local browser checks cover transactional recovery; the CI API fixture is explicitly separate from hosted verification. The full curriculum, comprehensive UI/accessibility coverage and release/recovery gates remain later work.

## 11. Implemented Phase 4 boundary

`release.py` now has a fixed allowlist for the reviewed and full manifests/catalog/profile files. Offline selection is explicit; untrusted manifest paths are never followed. The database adapter's validated immutable cache is keyed by release ID and bounded to two configured releases: `ANALYSIS_RELEASE_ID` plus `RETAINED_ANALYSIS_RELEASE_IDS`. Readiness checks both. New content is inserted as a new immutable row, without changing schema, graph, scoring policy, frozen protocol, runtime dependencies or old package bytes. Production reads canonical bytes from SQL, independent of root-level curriculum files.

`build_full_curriculum` deterministically builds original full-v1 inputs and refuses edits to an existing differing artifact. `check_full_curriculum` checks coverage, preserved slice values, trusted authored traces, contrasting seed outputs and reproducible examples. Domain tests independently exercise every concept's fresh practice/reassessment workflow. These are engineering checks; the existing quality runner still loads the original slice.

`curriculum-overview.tsx` renders the native SVG and equivalent concept list from public metadata/server estimates. `evidence-timeline.tsx` presents server grades with their original event metadata. Neither implements grading or diagnosis. `/examples/[profile]` statically renders generated safe seed/bundle snapshots; no live controller or submission handler is present. The only new direct dependency is development-only axe-core, already transitive in the lockfile.

Final Phase 4 [release evidence](evidence/phase4_release.json), [public browser proof](evidence/phase4_live_v2.json) and [targeted accessibility review](evidence/phase4_graph_accessibility.json) bind actual source/deployments. The roadmap owns current phase status.

## Phase 5 engineering release boundary

All runtime contracts/policy/content hashes remain unchanged. Owner, evaluation, migration, data and test inputs are explicitly excluded from the deployed Python source package; dependencies remain pinned and lightweight. Actual clean isolated source restore, missing-quota 503/recovery, real remote pause/resume, exact pending retry, HTTP quota exhaustion and compatible alias rollback/promotion now have evidence in [acceptance](release_acceptance.md), [release record](evidence/phase5_release.json) and the [operator runbook](recovery_runbook.md). The full-track synthetic audit publishes unfavorable proper-loss results without tuning; it is not student/educator validation. Formal content-review scope is an explicit owner decision, not an inferred human sign-off.
