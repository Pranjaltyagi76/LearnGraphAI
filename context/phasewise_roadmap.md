# Phasewise roadmap

**Updated:** 20 November 2026. **Current stage:** Phase 1 scaffold/verification in progress at the user’s request; remaining Phase 0 contract/content review is not marked complete. **Scope:** [requirement.md](../requirement.md); full phase rationale is in [PROJECT.md](../PROJECT.md), Section 18.

This is the operational handoff/status document. Check an item only after its stated artifact or verification exists. Drafting this context does not create the application, validate a model, provision a service, or pass a release gate.

## 1. Current state

| Area | Actual state |
| --- | --- |
| Git | Local `main`, origin points to the owner's LearnGraphAI repository; configured owner author/committer identity. Delivery evidence is Git history and the remote branch, not an invented hash here. |
| Specification | Revised PROJECT.md plus requirements and context references. |
| Code/dependencies | Next.js/FastAPI scaffold and pinned lockfiles exist; full diagnosis/replay remains Phase 2. |
| Curriculum | Proposed 12 concepts/17 edges and an authored two-concept, 12-question feasibility slice; complete 72-item catalog pending. |
| Services | Frontend/API deployed and READY on Vercel Hobby. Supabase account connected; Free Nano project `qnboukxsaczidpwtnadl` is Healthy in `us-east-1`. Private owner connection, migration/seeding, runtime provisioning, and live readiness remain pending. |
| Benchmarks/performance | Ten local API tests and four local browser tests pass; remote frontend/backend CI jobs pass, including isolated PostgreSQL. No model-quality benchmark or hosted DB timing. |
| Next action | Finish Phase 1 using the private owner connection, then verify the real deployed database path. Remaining Phase 0 contract/content review is still open. |

## 2. Resolved content-budget decision — OPEN-01

On 20 November 2026 the accepted direction changed the target from 48 to **72 questions**: six per concept (one diagnostic, four practice, one reassessment). The supported-evidence minimum stays at three distinct eligible first responses. Three initial observations can therefore leave two unused practice items and a distinct unused reassessment.

- [x] Record the budget decision consistently in PROJECT, requirements, and context.
- [x] Author 12 questions across `function_calls` and `base_cases`, with three initial responses and three unused items per concept.
- [x] Pass the catalog feasibility test in `backend/tests/test_api.py` proving two remaining practice questions and one reassessment per authored concept.
- [ ] Author/review the complete 72-item catalog and demonstrate the complete learning loop in its implementation phase.

This closes the item-budget conflict for the proposed design and authored slice, not the full Phase 0 gate, full curriculum, or diagnosis/reassessment implementation. More questions do not guarantee learning or readiness-threshold crossing.

## 3. Documentation foundation

- [x] Consolidate the approved project specification as PROJECT.md.
- [x] Initialize local Git and configure the owner's identity/origin.
- [x] Add root requirements, README, context-loading instructions, and secret/build ignore rules.
- [x] Document system design, architecture, phase gates, free deployment, performance review, and benchmarking.
- [ ] Complete the actual product/content/schema validation required by Phase 0 below.

Checkmarks above mean documentation/configuration exists. They do not mean proposed services/features have been implemented. The Git delivery status can be checked against the remote; no application phase is marked complete by the documentation push.

## 4. Implementation sequence

### Phase 0 — Product, curriculum, and contract freeze

Requirements: FR-02/03/06–11/18, NFR-01/03/09.

- [x] Resolve OPEN-01 and update the target budget; verify item availability in the authored two-concept slice.
- [ ] Review canonical concepts, prerequisite rationale, entry assumptions, and DAG validation rules.
- [ ] Author/review a small content slice with valid primary tags, grading, roles, and provenance.
- [ ] Freeze event envelopes, strict schemas, version manifest, digest canonicalization, timestamp policy, and error contracts.
- [ ] Review evidence eligibility, supported/unknown states, gap scoring, plan locks, and exhaustion behavior.
- [ ] Define synthetic profiles and independent benchmark scenarios/splits, without creating ground truth from the diagnosis function.
- [ ] Define local sandbox keys/revisions, pending recovery, reset, and cross-tab conflict rules.
- [ ] Document actual design choices in system design/architecture; keep proposed values distinguishable from measurements.

**Gate:** Reviewed graph/content slice/data dictionary/contracts exist; a feasible fresh-item loop is demonstrated; no unresolved contradiction is hidden by code.

### Phase 1 — Prove the free deployment path

Requirements: FR-19, NFR-01–06/08/10/11.

- [x] Create minimal frontend/backend scaffolds with verified supported pinned versions and lockfiles.
- [x] Add verified local setup commands and placeholder-only environment documentation.
- [ ] Configure two Vercel Hobby projects and Supabase Free without paid billing, using correct repository roots.
- [ ] Apply minimal canonical/quota migrations; verify least-privilege reads and atomic guard behavior.
- [ ] Finish live database pooling/TLS and runtime ownership verification; FastAPI packaging, public aliases, project ownership, and production CORS are verified.
- [ ] Exercise browser → API → database → response; measure bundle/cold/warm behavior.
- [x] Implement health/readiness and clear unavailable/example states; hosted database readiness still pending.
- [ ] Record actual runtime/limits/URLs/checks in deployment and performance documents.
- [ ] Test Render Free only if the preferred free API path fails its measured viability gate.

**Gate:** A real public round trip works within verified free eligibility and constraints. Prerecorded examples alone cannot pass.

### Phase 2 — Deterministic baseline and offline evaluation

Requirements: FR-06–11/14/18, NFR-03/09/10.

- [ ] Implement grading, deduplication, ordering validation, semantic digests, and evidence eligibility.
- [ ] Implement smoothed estimates/evidence states and bounded graph candidate traversal.
- [ ] Implement evidence-gated diagnosis/abstention, assessment requests, and constrained plan ranking.
- [ ] Create immutable synthetic fixtures and independent holdout scenarios with frozen manifests.
- [ ] Evaluate predictions before outcomes; compare the required P0 baselines and report actual metrics.
- [ ] Test retries/conflicts, hints/missing data, sparse/no-gap/ambiguous cases, ties, exhaustion, and graph errors.

**Gate:** CLI analysis and evaluation are reproducible from versioned inputs. No BKT or LLM is needed.

### Phase 3 — One complete deployed learning loop

Requirements: FR-01/04/05/12–17/19, NFR-02/07/12.

- [ ] Implement profile/seed/analyze routes and one coherent response bundle.
- [ ] Add anonymous local sandbox with pending/acknowledged states, refresh, reset, and stale-response protection.
- [ ] Ship a feasible question → supported gap/evidence request → fresh practice → different reassessment path.
- [ ] Show evidence counts, alternatives, and before/after results without inventing improvement.
- [ ] Test independent browsers and concurrent tabs in the completed loop; Phase 1 recorded/dependency failure and grading-contract cases already pass.

**Gate:** The actual live loop completes without developer intervention and without modifying another sandbox/canonical seed.

### Phase 4 — Complete curriculum and learner UI

Requirements: FR-01–05/09–17, NFR-12.

- [ ] Complete the resolved content budget/roles from Phase 0 and all four contrasting profiles.
- [ ] Build learner overview, graph/list, timeline, evidence detail, readiness locks, and reassessment display.
- [ ] Cover not-assessed/early/ambiguous/no-gap/exhausted/invalid/unavailable states.
- [ ] Verify mobile/desktop, keyboard/focus/contrast, non-color alternatives, and reduced motion.
- [ ] Publish labeled versioned examples and methodology/limitations pages.

**Gate:** The complete P0 content/UI works honestly; no unresolved OPEN-01 assumption remains.

### Phase 5 — Release, measured evaluation, and recovery

Requirements: all P0 FR/NFR; PROJECT Section 19.

- [ ] Run meaningful backend/frontend/browser checks on the actual release candidate.
- [ ] Confirm atomic shared limits, bounded payload/work, retries, version conflicts, and concurrent behavior.
- [ ] Test quota exhaustion, missing quota storage, paused database, cold/restarted API, and example fallback.
- [ ] Review secrets, privileges, logs, bundle contents, browser response projection, and production dependencies.
- [ ] Publish reproducible frozen-test metrics/model card and measured performance with sample counts.
- [ ] Exercise restore/reseed and compatible-version rollback; recheck free terms/settings/allowances.
- [ ] Verify public live URLs and the entire clean-browser loop; complete the acceptance checklist.

**Gate:** All required behavior passes; failed checks remain recorded and resolved. No paid dependency is introduced to make a gate pass.

### Phase 6 — Portfolio and optional P1 features

- [ ] Publish accurate screenshots, walkthrough, architecture, setup, and limitations.
- [ ] Add export/feedback/read-only synthetic mentor or evaluation views in complete slices.
- [ ] Treat CSV import as a provenance/privacy/schema feature, not unrestricted file ingestion.
- [ ] Before accounts, implement verified free auth/recovery, ownership, deletion/export, and durable idempotency together.
- [ ] Before real mentors, implement explicit assignments, audits, and cross-user denial tests.

**Gate:** P0 remains usable and reproducible; P1 is complete where exposed and does not weaken the ₹0/privacy boundaries.

### Phase 7 — Optional P2 research

- [ ] Compare offline BKT to the frozen baseline with matched response-prediction semantics.
- [ ] Keep any licensed EdNet study separate from DSA diagnosis claims.
- [ ] Evaluate recency/difficulty changes before promotion; use DKT only with sufficient local resources/data.
- [ ] Add free Gemini wording only if available, disabled by default, bounded, schema-checked, and template-backed.
- [ ] Expand domains/cohorts only when justified and compatible with free deployment.

**Gate:** Independent reproducible report for each experiment; no automatic runtime model switch or paid service.

## 5. Session handoff protocol

At meaningful milestones record: date, phase/task IDs, changed behavior, commit reference, actual checks/artifacts, unresolved blockers, and next action. Use `not run` for missing checks. Git hashes are recorded after commits exist; do not invent self-referential hashes in a pending commit.

| Date | Work | Evidence/status | Next step |
| --- | --- | --- | --- |
| 2026-11-20 | Specification and development context foundation | Documentation only; Git history records delivery. OPEN-01 identified; no runtime/benchmark evidence. | Complete Phase 0 review and the Phase 1 live database gate. |

Before a future batch, read [AGENTS.md](../AGENTS.md), inspect working-tree/remote state, and select a coherent slice. Preserve user changes. Deliver authorized work in 4–6 meaningful commits where the scope supports it, using the owner's configured author/committer and no assistant co-author trailers.


### Phase 1 delivery evidence — 20 November 2026

- Source/verification commit: `daef1171bdf2608911dba09ea6d658a5f19c5dfb`; final documentation-only delivery records these observations.
- [Frontend preview](https://learngraph-ai-web.vercel.app) and [API health](https://learngraph-ai-api.vercel.app/health) are public. Vercel reports both deployments READY; deployment IDs and environments are in deployment.md.
- Local: ten API contract/content tests passed; four SQL tests skipped because no local PostgreSQL was configured. Four production-build browser tests passed, including mobile, recorded, unavailable, and grading-contract behavior. Lint/typecheck/build and content/DAG validation pass.
- [Remote CI](https://github.com/Pranjaltyagi76/LearnGraphAI/actions/runs/44700160117): frontend and backend jobs succeeded. Backend is configured with real isolated PostgreSQL 17 and runs the SQL suite. Public raw-log download required authentication, so this report does not invent a separate hosted CI test-count transcript.
- Public API response: `/health` = 200 JSON; `/ready` = 503 `not_configured`, with the production frontend origin allowed. The actual browser shows the explicit unavailable notice and retains the recorded example.
- User confirmed no paid billing; Vercel's deployment-context tool independently returned `plan: hobby`. No paid resource was enabled, no database secret supplied, and no Supabase migration was run.
- **Remaining gate:** install/connect Supabase, select/create a verified free project, apply/verify migration and seed, configure a separate runtime login and hash secret, redeploy API, then prove browser → API → Supabase → grading response. Record DB/cold/warm/resource/recovery evidence afterward. Phase 1 is **not complete** until this succeeds.
- Vercel deployments were requested explicitly from the exact Git SHA. Automatic Git push-to-deploy linkage is not configured/verified; do not assume a later Git push redeploys these projects automatically.

### Phase 1 continuation — Supabase project provisioned, runtime connection pending

- Verified Supabase's connected Primary account and the owner's Free organization. The user created `learngraph-ai`, project `qnboukxsaczidpwtnadl`; dashboard shows Healthy Nano in `us-east-1`. Data API was disabled and automatic RLS enabled on the creation form. No paid billing/add-on was configured.
- Verified session/transaction pooler host and ports in the dashboard; free shared host has IPv4 DNS records. No authenticated connection or migration has run yet.
- Added a read-only runtime/TLS/content audit and a one-time restricted-login helper. Both commits use the owner's author/committer. [CI run 44715705552](https://github.com/Pranjaltyagi76/LearnGraphAI/actions/runs/44715705552) passed backend/frontend, including the new isolated PostgreSQL audit.
- Added bounded deployment smoke tooling and safe production timing/process-memory logging. Local lint/format and ten API tests pass; five PostgreSQL checks skip locally. These prepared hooks are not deployed or measured hosted results.
- The owner password is requested only in ignored `backend/.env.local` as temporary `SUPABASE_OWNER_PASSWORD`; no password/token should be sent in chat. At the last check that value and `MIGRATION_DATABASE_URL` were empty. The file is excluded by Git.
- **Resume:** prepare the TLS session-pooler owner DSN privately and remove the temporary password field; migrate/seed/verify; provision runtime; run the read-only runtime audit; set only `DATABASE_URL`/`CLIENT_ID_HASH_SECRET` in API production secrets; deploy the exact pushed source; exercise the real browser round trip and bounded smoke report; record measured evidence. Phase 1 remains incomplete until the gate passes.
