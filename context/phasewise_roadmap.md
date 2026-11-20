# Phasewise roadmap

**Updated:** 20 November 2026. **Current stage:** Documentation foundation; application Phase 0 remains open. **Scope:** [requirement.md](../requirement.md); full phase rationale is in [PROJECT.md](../PROJECT.md), Section 18.

This is the operational handoff/status document. Check an item only after its stated artifact or verification exists. Drafting this context does not create the application, validate a model, provision a service, or pass a release gate.

## 1. Current state

| Area | Actual state |
| --- | --- |
| Git | Local `main`, origin points to the owner's LearnGraphAI repository; configured owner author/committer identity. Delivery evidence is Git history and the remote branch, not an invented hash here. |
| Specification | Revised PROJECT.md plus requirements and context references. |
| Code/dependencies | No frontend/backend code or manifests yet. |
| Curriculum | Proposed 12 concepts/17 edges only; no authored catalog or reviewed data artifacts. |
| Services | No Vercel/Supabase/Render resource provisioned by this work; no live URL. |
| Benchmarks/performance | Procedures and proposed budgets only; no measurements. |
| Next action | Resolve the content/evidence reachability conflict, then review/freeze the Phase 0 contracts and first authored slice. |

## 2. Phase 0 design blocker — OPEN-01

The agreed budget is four distinct questions per concept (48 total). The supported-gap rule requires at least three eligible distinct first responses. Once a concept qualifies, at most one unused item remains, but a fresh practice item **and** a different fresh reassessment item require two. Repeated/hinted attempts cannot legitimately repair this evidence budget.

Do not mark the live loop/content design ready until this is resolved consistently. Candidate resolutions to evaluate are expanding the item budget (at least five questions per concept for the minimum one-fresh-practice-plus-reassessment path) or revising and validating the evidence gate. Neither alternative is silently adopted by this context setup. If expanding content is chosen, five items per concept is only a minimum for that path, not enough for unlimited recovery or guaranteed threshold crossing.

- [ ] Construct per-profile/per-gap evidence traces showing counted history, remaining practice, and distinct reassessment.
- [ ] Select a defensible resolution; do not count lessons, secondary tags, or repeats as new question evidence.
- [ ] Update PROJECT, requirements, content totals/roles, algorithm configuration, benchmark fixtures, and context together.
- [ ] Include a feasible diagnostic → diagnosis → fresh practice → fresh reassessment trace in the Phase 0 exit evidence.

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

- [ ] Resolve OPEN-01 and update all affected totals/rules.
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

- [ ] Create minimal frontend/backend scaffolds with verified supported pinned versions and lockfiles.
- [ ] Add verified local setup commands and placeholder-only environment documentation.
- [ ] Configure two Vercel Hobby projects and Supabase Free without paid billing, using correct repository roots.
- [ ] Apply minimal canonical/quota migrations; verify least-privilege reads and atomic guard behavior.
- [ ] Verify FastAPI entrypoint, shared source packaging, transaction pooling/TLS, CORS, and production environment ownership.
- [ ] Exercise browser → API → database → response; measure bundle/cold/warm behavior.
- [ ] Implement health/readiness and clear unavailable/example states.
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
- [ ] Test independent browsers and concurrent tabs, no LLM credentials, and dependency failure.

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
| 2026-11-20 | Specification and development context foundation | Documentation only; Git history records delivery. OPEN-01 identified; no runtime/benchmark evidence. | Resolve OPEN-01 and complete Phase 0. |

Before a future batch, read [AGENTS.md](../AGENTS.md), inspect working-tree/remote state, and select a coherent slice. Preserve user changes. Deliver authorized work in 4–6 meaningful commits where the scope supports it, using the owner's configured author/committer and no assistant co-author trailers.
