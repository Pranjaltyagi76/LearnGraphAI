# LearnGraph AI — Requirements

**Revision:** 20 November 2026. **State:** P0 requirement baseline; implementation and validation pending.

This file translates [PROJECT.md](PROJECT.md) into testable requirements. IDs are stable references for implementation, tests, and reviews. Requirements are planned, not evidence that features already exist. User instructions take precedence; changes must be reconciled across the specification and relevant context files.

## 1. Product scope

Build a personal portfolio demo of **answer → observed-performance estimate → prerequisite-aware hypothesis/evidence request → practice → distinct reassessment**. A diagnosis may abstain. Do not claim latent mastery, causal proof, or actual learning gains from synthetic demonstrations.

P0 uses 12 concepts, 72 distinct questions (one diagnostic, four practice, one reassessment per concept), additional short lessons, and four synthetic profiles. Canonical IDs, graph edges, formulas, and initial thresholds are specified in PROJECT Sections 6 and 8. They need Phase 0 review and versioning before implementation.

**Resolved design decision — OPEN-01:** The target is now six questions per concept (72 total): one diagnostic, four practice, and one reassessment. Three initial eligible observations leave two fresh practice questions and a different reassessment. The two-concept authored fixture tests this availability; the complete catalog and broader Phase 0 review remain pending. Details are in [the roadmap](context/phasewise_roadmap.md).

## 2. Functional requirements

| ID | Requirement | Acceptance evidence |
| --- | --- | --- |
| FR-01 | Enter a labeled synthetic demo without registration or personal information. | Clean-browser flow reaches each of four profiles. |
| FR-02 | Publish a reviewed, versioned 12-node prerequisite DAG with stable IDs; separate topic membership from prerequisite edges. | Validator rejects unknown nodes, self/duplicate edges, and cycles; arrows match the defined direction. |
| FR-03 | Author/version 72 distinct questions plus lessons with role, primary concept, contextual tags, difficulty, grading, and provenance. | Catalog validation and human content review; no repeated practice question disguised as reassessment. |
| FR-04 | Keep canonical seeds immutable; isolate each browser's visitor events by profile and published versions. | Independent browser contexts do not share mutations; no public seed update endpoint. |
| FR-05 | Resume local progress after refresh, handle concurrent tabs, and reset only local changes. | Browser tests cover refresh, reset, stale writes, and unavailable storage with a session-only notice. |
| FR-06 | Validate response events and derive grades/tags/difficulty/attempt counts from server-owned catalog data. | Malformed/forged metadata is rejected; correct and incorrect grading fixtures pass. |
| FR-07 | Replay seed plus ordered visitor responses deterministically; deduplicate identical event IDs and reject conflicting IDs/order. | Identical semantic input yields identical digest/result; conflicts return `409`, invalid ordering `422`. |
| FR-08 | Count only the first response to each distinct primary-concept question with known zero hints as baseline evidence. | Retried/hinted/unknown-hint responses, lessons, and secondary tags do not add observations. |
| FR-09 | Separate `not_assessed`, `early_estimate`, and `supported_estimate`; show counts and limitations. | No-data UI hides a misleading 50% mastery claim; thresholds match versioned configuration. |
| FR-10 | Diagnose target and prerequisite candidates up to three edges, using evidence-gated ranking and explicit abstention. | Unknown prerequisites request assessment; secure ancestors are not automatically blamed; evidence IDs/path are real. |
| FR-11 | Return at most three gap candidates and at most five plan items with valid IDs, reasons, readiness conditions, and prerequisite order. | Schema/catalog/order checks; deterministic ties; exhausted catalog returns an explicit state. |
| FR-12 | Complete diagnostic, practice, and different same-skill reassessment with honest before/after evidence. | Full live browser flow; unchanged or worse estimates are displayed accurately. |
| FR-13 | Return and display a single consistent analysis bundle tied to the same input digest and published versions. | No mix of new history with old estimates/plan; late responses cannot replace newer results. |
| FR-14 | Explain evidence and uncertainty with templates; work without any LLM setup. | Demo passes with no AI API key; no unsupported confidence/causal statements. |
| FR-15 | Provide learner dashboard, graph/list alternative, timeline, and plan with accessible loading/empty/error states. | Mobile/desktop and keyboard checks, labels/contrast, and non-color information. |
| FR-16 | Distinguish pending answers, accepted analysis, `429`, dependency failure, version mismatch, and item exhaustion. | Failure fixtures show correct retry/reset guidance and preserve pending local work. |
| FR-17 | Keep bundled prerecorded examples accessible during live dependency failure and label them explicitly. | Failure-mode browser test shows example date/versions and disables live submission; never fakes acceptance. |
| FR-18 | Publish reproducible baseline evaluation, actual counts/splits/configuration, and limitations. | Independent holdouts, prefix-based prediction, measured result files, and model card. BKT is not required. |
| FR-19 | Expose lightweight liveness, bounded readiness, versioned seed/analysis endpoints, and safe public evaluation summaries. | API contract checks and deployed browser → API → database verification. |

## 3. Nonfunctional requirements

| ID | Requirement | Initial acceptance rule |
| --- | --- | --- |
| NFR-01 | Strict recurring service budget ₹0 / $0. | Free plans only; no paid billing/payment setup, paid fallback, bought domain, auto-top-up, or expiring-credit dependency. |
| NFR-02 | Verify a viable free live topology early. | Phase 1 demonstrates actual Next.js → FastAPI → pooled Supabase access; fallback-only examples do not pass. |
| NFR-03 | Bound runtime work. | Body ≤256 KiB; ≤200 visitor events plus ≤100 canonical seed events; traversal depth ≤3; plan ≤5 items. |
| NFR-04 | Bound latency and resource consumption. | Ten-second application analysis budget; actual cold/warm/bundle/memory measurements recorded against proposed targets in the performance review. |
| NFR-05 | Enforce shared quotas atomically. | Initial ten analysis requests/minute/client identifier and 1,000/day globally; cross-instance tests; `429` on exhaustion. These do not guarantee provider limits cannot be reached. |
| NFR-06 | Fail closed on unavailable quota enforcement. | Analysis returns `503`; no in-memory global bypass; static examples remain available. |
| NFR-07 | Keep synthetic data and secrets separated. | No real learner records; no credentials in Git/browser/logs; public runtime responses withhold future answers until feedback is due. Public authored source is not a secret exam bank. |
| NFR-08 | Use least-privilege database access. | Public canonical writes denied; runtime/admin roles separated; exposed tables have appropriate grants/RLS; privileged roles are not assumed to enforce ownership automatically. |
| NFR-09 | Preserve reproducibility and truthful reporting. | Versioned seeds/catalog/graph/model, semantic digests, exact package versions, split manifests; unrun checks remain unrun. |
| NFR-10 | Keep deployment lightweight and stateless. | Research dependencies/data excluded; no user persistence on function disk/memory; restart/redeploy does not destroy canonical data. |
| NFR-11 | Make recovery possible without payment. | Restore/reseed and version checks documented and exercised; local sandbox persistence limits disclosed. |
| NFR-12 | Maintain accessible, responsive UX. | Keyboard/focus/semantic labels, sufficient contrast, graph list alternative, mobile layout, and reduced-motion behavior where applicable. |
| NFR-13 | Minimize retained identifiers and logs. | Hashed rotating client identifiers, quota expiry within 48 hours, no raw answers/personal data in logs, bounded artifacts/caches. |

Values above are agreed initial application defaults. Provider entitlements are separate, dated checks in [deployment.md](context/deployment.md); performance proposals are not measured results.

## 4. Deferred requirements and prerequisites

| Stage | Feature | Gate before implementation/release |
| --- | --- | --- |
| P1 | Feedback, export, synthetic mentor/evaluation preview | P0 passes; workflow works end to end; export can be generated in browser. |
| P1 | CSV import | Explicit provenance, schema/row/byte limits, preview, and privacy/retention rules. |
| P1 | Public accounts and server history | Complete verified free login/recovery, ownership, deletion/export, durable event idempotency, and cross-user tests. Default Supabase SMTP is not general public email delivery. |
| P1 | Real mentor access | Authentication plus explicit assignments, query scoping, denial tests, and audit records. |
| P2 | BKT, recency/difficulty changes | Untouched offline comparisons to the frozen baseline; no automatic model promotion. |
| P2 | EdNet, DKT, cohort analysis | Appropriate license, separate claims/data pipeline, enough local data/compute, and no hosted training dependency. |
| P2 | Gemini wording | Disabled by default, verified free access, synthetic minimal inputs, strict limits, validated output, template fallback. |

## 5. Release and traceability

P0 requires FR-01–FR-19 and NFR-01–NFR-13, plus the full checklist in PROJECT Section 19. A high model score cannot waive privacy, identity, quota, or correctness failures. There is no fabricated accuracy threshold or required improvement over a baseline; measure and report the actual outcome.

| Concern | Owning development reference |
| --- | --- |
| User/data flows and API consistency | [System design](context/system%20design.md) |
| Modules, dependencies, and state placement | [Architecture](context/architecture.md) |
| Sequence, status, and phase evidence | [Phasewise roadmap](context/phasewise_roadmap.md) |
| Free hosting, environment boundaries, and recovery | [Deployment](context/deployment.md) |
| Latency, payload, bundle, and load review | [Performance review](context/performance_review.md) |
| Model/diagnosis/recommendation quality and leakage | [Benchmark](context/benchmark.md) |

When completing a task, reference relevant IDs in tests/review notes and record the actual command/artifact and commit. Change versions deliberately when event semantics, grading, graph, or thresholds change.
