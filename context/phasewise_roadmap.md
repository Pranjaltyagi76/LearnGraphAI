# Phasewise roadmap

**Updated:** 20 November 2026. **Current stage:** Phase 0 engineering review and Phase 1 complete; Phase 2 is next. **Scope:** [requirement.md](../requirement.md); full phase rationale is in [PROJECT.md](../PROJECT.md), Section 18.

This is the operational handoff/status document. Check an item only after its stated artifact or verification exists. Drafting this context does not create the application, validate a model, provision a service, or pass a release gate.

## 1. Current state

| Area | Actual state |
| --- | --- |
| Git | Local `main`, origin points to the owner's LearnGraphAI repository; configured owner author/committer identity. Delivery evidence is Git history and the remote branch, not an invented hash here. |
| Specification | PROJECT/requirements reconciled with frozen protocol, storage and curriculum review decisions. |
| Code/dependencies | Offline strict contract/normalization/hash/storage-record models and conformance checks added; full diagnosis/replay remains Phase 2. |
| Curriculum | Reviewed draft: 12 concepts/17 scoped edges, 12 version-2 questions/2 lessons and 4 synthetic seed definitions. Published Phase 1 slice remains immutable; 60 questions remain. |
| Services | Two Vercel Hobby projects and a Healthy Supabase Free Nano project. Migration/seed/runtime login configured; public readiness 200 and actual browser grading passed. |
| Benchmarks/performance | Local checks and source CI pass. Hosted privilege/quota checks, eleven-request smoke, browser grading, artifact/memory and cold/hot provider metrics recorded. No model-quality benchmark. |
| Next action | Implement Phase 2 pure replay/estimation/diagnosis/plan services and evaluators, reusing frozen contracts/assets; publish only a compatible new release. |

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
- [x] Complete the bounded engineering product/content/schema review required by Phase 0 below.

Checkmarks above mean documentation/configuration exists. They do not mean proposed services/features have been implemented. The Git delivery status can be checked against the remote; no application phase is marked complete by the documentation push.

## 4. Implementation sequence

### Phase 0 — Product, curriculum, and contract freeze

Requirements: FR-02/03/06–11/18, NFR-01/03/09.

- [x] Resolve OPEN-01 and update the target budget; verify item availability in the authored two-concept slice.
- [x] Review canonical concepts, prerequisite rationale, entry assumptions, and DAG validation rules.
- [x] Author/review a small content slice with valid primary tags, grading, roles, and provenance.
- [x] Freeze event envelopes, strict schemas, version manifest, digest canonicalization, timestamp policy, and error contracts.
- [x] Review evidence eligibility, supported/unknown states, gap scoring, plan locks, and exhaustion behavior.
- [x] Define synthetic profiles and independent benchmark scenarios/splits, without creating ground truth from the diagnosis function.
- [x] Define local sandbox keys/revisions, pending recovery, reset, and cross-tab conflict rules.
- [x] Document actual design choices in system design/architecture; keep proposed values distinguishable from measurements.

**Gate:** Reviewed graph/content slice/data dictionary/contracts exist; a feasible fresh-item loop is demonstrated; no unresolved contradiction is hidden by code.

**Passed, 20 November 2026:** reviewed draft assets, frozen schemas/hash vectors, profile/scenario definitions and storage state machine exist and validate. This is an engineering review, not educator validation, deployed analysis, browser-store implementation, or a model benchmark.

### Phase 1 — Prove the free deployment path

Requirements: FR-19, NFR-01–06/08/10/11.

- [x] Create minimal frontend/backend scaffolds with verified supported pinned versions and lockfiles.
- [x] Add verified local setup commands and placeholder-only environment documentation.
- [x] Configure two Vercel Hobby projects and Supabase Free without paid billing, using correct repository roots.
- [x] Apply minimal canonical/quota migrations; verify least-privilege reads and atomic guard behavior on the hosted database.
- [x] Verify live transaction pooling/TLS, runtime/owner separation, FastAPI packaging, public aliases, project ownership, and production CORS.
- [x] Exercise browser → API → database → response; record artifact size, process/provider memory, cold/hot provider metrics, and client smoke timings with their limitations.
- [x] Implement and exercise health/readiness and clear unavailable/example states; hosted readiness now returns 200.
- [x] Record runtime/limits/URLs/checks, immutable hash verification, and idempotent reseeding in deployment/performance evidence.
- [x] Resolve fallback decision: preferred free Vercel path passed; Render is not required or provisioned.

**Gate:** A real public round trip works within verified free eligibility and constraints. Prerecorded examples alone cannot pass.

**Passed, 20 November 2026:** live browser grading and hosted database/resource checks succeeded. Evidence and cold-probe limitations are in [performance review](performance_review.md). This closes Phase 1, not the full learning loop or model evaluation.

### Phase 2 — Deterministic baseline and offline evaluation

Requirements: FR-06–11/14/18, NFR-03/09/10.

- [ ] Implement grading, deduplication, ordering validation, semantic digests, and evidence eligibility.
- [ ] Implement smoothed estimates/evidence states and bounded graph candidate traversal.
- [ ] Implement evidence-gated diagnosis/abstention, assessment requests, and constrained plan ranking.
- [ ] Implement evaluation over the frozen synthetic packet and author separately versioned variants/final audits when required; do not describe the public audit as blind.
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


### Phase 1 completion evidence — 20 November 2026

- **Passed gate:** public browser → API → Supabase → real grading feedback. The page switched from its labeled example to a live question, accepted option n, and displayed the server explanation. [Browser proof](evidence/phase1_live_grading.jpg).
- API source 568048188668d0a687b0b08677475f490099c7fd, deployment dpl_8VtMQHBUV5boQida7rGVeaFrkTnh; unchanged frontend source daef1171bdf2608911dba09ea6d658a5f19c5dfb. Public aliases are in deployment.md. Automatic Git push-to-deploy linkage is not configured; future code pushes require an explicit deployment.
- Vercel team is Hobby, confirmed without paid billing. Supabase organization is Free; project qnboukxsaczidpwtnadl is Healthy Nano in us-east-1. No paid plan, add-on, payment setup, or keepalive was introduced.
- Owner migrate/seed/verify and restricted runtime provisioning succeeded. Transaction pooling/TLS, effective grants, owner separation, and source/stored/recomputed hashes passed. Vercel Production Secrets were supplied through CLI stdin. Private configuration remains ignored; the temporary password field was removed.
- [Hosted database report](evidence/phase1_database.json): twelve reservations with four workers admitted exactly ten, both counters equal ten; global exhaustion rejects another client without incrementing. Runtime writes/public-role access are denied, published releases resist owner mutation, and logical expiry is within 48 hours. Temporary quota fixtures were removed. Database size: 11,237,043 bytes.
- [Public smoke](evidence/phase1_deployment.json): eleven sequential requests, three grading reservations, no retries. Health/readiness 200, CORS/projection, correct/incorrect grades, and version 409 passed. The separate browser answer used one additional reservation.
- [Resources](evidence/phase1_resources.json): Python 3.12, reported lambda size 12,699,243 bytes, allocation 2,048 MiB, timeout 15 s, iad1; captured process peak RSS 64,660 KiB. Artifact encoding is unspecified; no uncompressed-size claim.
- [Provider metrics](evidence/phase1_provider_metrics.json): two cold GET / probes (404, no grading) and sixteen hot invocations. Cold duration average/max 902.5/1,006 ms; TTFB 1,313/1,657 ms. Hot duration average/max 34.5/127 ms. Provider peak memory 210 MB. These are small provider samples, not full client cold-grading latency.
- Repeated seed/hash verification and a new API deployment preserving canonical data passed. Full disaster restore, pause/resume, version rollback, and full-loop failure recovery remain Phase 5 work.
- Local lint/format/content and ten API tests passed; five SQL checks skip without a local test DB. [Source CI run 44730530223](https://github.com/Pranjaltyagi76/LearnGraphAI/actions/runs/44730530223) passed backend/frontend with isolated PostgreSQL 17 and four browser tests. No model-quality benchmark was run.
- Initial tool/credential-transfer obstacles were resolved through the authenticated dashboard, owner scripts, and official CLI. Supabase tools remain absent from this chat. Render fallback was unnecessary.
- **Next:** Phase 0 review has now passed (record below); implement Phase 2 deterministic replay, estimates, diagnosis/plans and offline evaluation. Full P0 curriculum and learning-loop acceptance remain open.

### Phase 0 review completion — 20 November 2026

- Reviewed all 12 concepts and 17 scoped edges. The DP route now reaches tabulation without recursion; top-down memoization retains recursive tracing. [Rationales and item review](../curriculum/review.md).
- Revised 12 draft questions at activity version 2, added two supporting lessons, and defined four explicit synthetic seeds (19 events). The published phase1-v1 semantic hash is unchanged. Sixty more questions and the full curriculum UI remain Phase 4 work.
- Frozen [protocol/schema/manifest](../contracts/protocol.md): strict event and API structures, compatible release/hash tuples, UTC milliseconds, null metadata, canonical UTF-8/SHA-256, deterministic ordering and bounded errors. New release-scoped metadata preserves legacy bootstrap clients.
- Reviewed exact evidence eligibility, uncertainty/abstention precedence, rational scores/ties, readiness locks and honest exhaustion. Mira's available fresh practice/reassessment trace ends at 0.5 after three correct new responses, not readiness or a learning claim.
- Frozen [IndexedDB state machine](browser_storage.md): atomic revision checks, pending focus/trigger snapshots, refresh/retry, reset/new UUID, stale responses, cross-tab conflicts and session-only fallback. Fourteen browser scenarios are defined; actual IndexedDB/browser implementation remains Phase 3.
- Frozen [evaluation packet](../evaluation/readme.md): 4 training/8 development/12 public synthetic final-audit cases with separate assumptions/annotations, hashes and split integrity checks; six future-catalog/fixture-DAG blueprints. No production diagnosis output generated labels. Cases were visible in review, not blind or evidence of generalization. No evaluator or benchmark ran.
- Actual local verification: lint/format, schema/manifest, graph/catalog/profile/split checks passed; 68 tests passed and 5 isolated SQL checks skipped locally. Node independently passed nine canonical/hash/storage vectors and five release hashes. [Review evidence](evidence/phase0_review.json). CI now runs the new checks with real isolated PostgreSQL and existing browser regressions.
- Original-content license remains unselected; educator validation is not claimed. No new infrastructure, billing, production migration or activation was performed.
- Next: Phase 2 pure replay/eligibility/estimation/diagnosis/plan services, versioned publication, and real offline evaluator. Reuse frozen DTOs/fixtures; do not mark route integration, saved progress or measured model quality complete.
