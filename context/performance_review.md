# Performance review

**State:** Phase 1 live deployment/resource checks passed; small descriptive samples are recorded below. Full-analysis deployment and learning-loop performance remain unmeasured; the separate offline quality audit is linked below. **Date:** 20 November 2026.

This file covers latency, resources, reliability under bounded load, and the effect of free hosting. Model-quality evidence belongs in [benchmark.md](benchmark.md). Runtime constraints originate in PROJECT Sections 12–14 and [requirements](../requirement.md), especially NFR-03–06/10/13.

## 1. Separate constraints, targets, and results

| Measure | Initial requirement/target | Classification | Current result |
| --- | --- | --- | --- |
| Request body | Maximum 256 KiB, enforced while counting bytes | Application hard bound | Implemented; chunked oversized-body contract test passes. |
| History | At most 200 visitor events plus 100 server seed events | Application hard bound | Not implemented/tested. |
| Search/plan | Prerequisite depth ≤3; ≤3 diagnoses; ≤5 plan items | Application hard bound | Not implemented/tested. |
| Analysis work | Ten-second application time budget with tighter DB/operation deadlines | Agreed initial budget; cold behavior must be measured | Bootstrap middleware bound implemented. Observed smoke API durations 2.85–121.93 ms; full analysis not implemented. |
| Shared quota | Ten analyses/minute/client identifier; 1,000/day globally | Initial operational guard, not provider entitlement | Hosted concurrent client/global denial and counter atomicity passed; bootstrap grading uses this guard. |
| Quota retention | Expiry within 48 hours; bounded cleanup | Application retention bound | Hosted logical-expiry check passed. Physical deletion is opportunistic, not guaranteed during idle periods. |
| Warm API response | Proposed p95 ≤2 seconds end-to-end at the defined low-volume workload | Engineering target to review in Phase 1 | Five readiness samples: p50 584.48 ms, nearest-rank p95/max 695.60 ms; two grades 364.79/335.18 ms. Small smoke sample, not an SLO or full-analysis benchmark. |
| Pure analysis compute | Proposed p95 ≤100 ms for the maximum valid fixture on the declared local machine | Profiling target; excludes DB/network/cold boot | Not measured. |
| Initial learner page | Proposed usable primary content within 3 seconds under a stated device/network profile | UX target; report tool and conditions | Not measured. |
| Bundle/memory/DB pool | Fit verified free provider limits with documented margin | Deployment gate, exact values observed in Phase 1 | Reported artifact 12,699,243 bytes; provider peak memory 210 MB versus 2,048 MiB allocation; one client connection/instance; hosted TLS/permissions audit passed. |

New proposed targets do not override hard constraints or become measured claims. Record changes with evidence if free-host cold starts or regional latency require a different UX target. Do not relax correctness/security or enable payment merely to improve timings.

## 2. Measurement breakdown

Instrument request ID, total server duration, quota reservation, canonical fetch, validation/replay, pure estimation/diagnosis/plan time, serialization, payload bytes, and success/error code. Record config/manifest/commit identifiers.

Measure browser-perceived latency separately from server timing. Cold start, TLS/network, retries, and client rendering contribute to user experience and must not disappear from the reported total. Clearly label warm, naturally cold/restarted, cached, and uncached samples.

No raw answers, credential values, raw IP/client identifiers, or future personal records belong in timing logs. Aggregate durations/counts are sufficient. Tracing must remain lightweight and free; no hosted APM dependency is required.

## 3. Workload matrix

| Workload | Purpose |
| --- | --- |
| Empty visitor history with a canonical seed | Startup/initial estimates; unknown-state correctness. |
| Typical short prefix | Expected interactive response. |
| Maximum valid 100+200-event history | Bounded worst-size replay/serialization. |
| Repeated identical prefix and repeated question events | Idempotent output/eligibility; no cache-dependent correctness. |
| Dense valid 12-node DAG fixture and depth boundary | Traversal cost/path limits without inventing extra product concepts. |
| Supported/unknown/ambiguous/exhausted plan cases | Branching behavior and reason generation. |
| Concurrent quota reservations | Atomic allowance; no over-admission across instances. |
| Malformed/oversized bodies and invalid versions | Early rejection cost and safe errors. |
| Unavailable/stale DB connections, paused DB, slow dependency | Timeouts, cleanup, `503`, pending preservation, fallback. |

OPEN-01 is resolved by the 72-question target and authored-slice item-availability test. Complete practice/reassessment load measurements still require the full implemented loop; computational fixtures alone are not end-to-end evidence.

## 4. Test sequence and free-budget guard

1. Run local pure-function timing with fixed fixtures; record machine/OS/Python, exact packages, warm-up/sample count, and full input/config hashes.
2. Run local API/database integration checks, then low-volume concurrent tests against local or isolated test data. Keep quota logic enabled; test global/client exhaustion deliberately with test-only configuration in an isolated environment.
3. Measure a small real deployed sample only after checking remaining free allowances. Proposed smoke budget: at most 50 analysis calls total per candidate review, with each identifier kept below ten calls/minute and the global daily allowance respected. Stop on errors, resource pressure, or quota responses.
4. Measure naturally cold or controlled restart behavior through supported provider actions; never keep a free service artificially awake. If a cold start cannot be reliably identified, state that limitation.
5. Exercise clean-browser initial load, answer submission, chart/graph rendering, pending/error/retry states, mobile, and keyboard behavior.

Do not conduct a high-volume public load test, disable production quotas, or bypass the guard to collect more samples. Local tests may use explicitly scoped configuration; it must not leak into production. Shared-network client signals can cause users to share a quota and must be included in usability review.

Report p50/p95/max and sample count for ordinary workloads, but label small deployed samples as descriptive smoke measurements rather than statistically stable latency guarantees. Include failures/timeouts and retries, not just successful fast requests.

## 5. Resource and dependency review

- Inspect actual deployment artifact size and included files. Research notebooks, datasets, pandas/PyTorch/MLflow and caches must not enter runtime unless a concrete runtime requirement is approved and measured.
- Profile before optimizing. Prefer bounded replay and version-keyed immutable data reuse over adding infrastructure or a second independent algorithm.
- Record idle/peak memory where observable, DB pool settings and peak connections, egress/payload size, invocation/CPU usage, and provider error counts.
- A small per-instance pool does not cap global connections across all warm instances; verify shared limits, query timeouts, and connection release.
- Quota reservation adds a DB operation to every admitted analysis. Measure that cost; cache/instance reuse must not bypass the shared guard.
- Measure the maximum fixture without silently truncating history or changing evidence eligibility for speed.

## 6. Reliability checks

| Check | Passing behavior |
| --- | --- |
| Duplicate retry | Same semantic result; no extra observations. |
| Late response / profile switch | Old bundle cannot overwrite newer local state. |
| Concurrent tabs | Conflict detected/coordinated; no silent history loss. |
| Quota race | Atomic limits honored across concurrent requests. |
| Missing quota DB | Live analysis fails closed; no local global-limit replacement. |
| Request/query timeout | Bounded safe error; no false acknowledgement; pending history remains. |
| Restart/redeploy | Canonical data preserved; versioned browser history gets correct handling. |
| Static example | Clearly labeled; live result not fabricated during outage. |

## 7. Review record template

For each measured review, record:

- Date, commit, clean/dirty tree, environment/region and provider plan.
- Runtime/dependency versions, canonical manifest, fixture hashes and event/item counts.
- Tool/command, local hardware or client/network profile, warm-up, sample count, concurrency/rate.
- Per-stage and browser total timings, failures/retries, bundle/memory/connections/egress where available.
- Remaining provider quota and number of real deployed calls used.
- Actual versus hard bounds/proposed targets, caveats, root cause of regressions, and next action.
- Links to compact reproducible results; no secret-bearing traces or raw private data.

Keep attempted/failed runs visible. A change in machine, region, fixture, or methodology prevents a direct headline comparison unless explained.

## 8. Current review ledger

| Review | Evidence | Outcome |
| --- | --- | --- |
| Documentation foundation, 2026-11-20 | Requirements/budget/protocol design only | No performance pass/fail; nothing measured. |
| Phase 1 deployment viability | Live browser grading, hosted SQL checks, public smoke, cold/hot provider metrics, resource metadata, and reseeding passed | Free topology viable for the bounded feasibility slice; full product/inference gate remains later work. |
| Phase 3 complete learning loop | Not run | Pending full learning-loop implementation. |
| Phase 5 release review | Not run | Release not ready. |

Future reviewers must update this ledger from real execution. Do not replace `not measured` with guessed production numbers or promise always-on free hosting.

## 9. Observed Phase 1 checks — 20 November 2026

API source 568048188668d0a687b0b08677475f490099c7fd; unchanged frontend source daef1171bdf2608911dba09ea6d658a5f19c5dfb. Client: Windows/Python 3.12.10. API: Python 3.12, Vercel iad1; DB: Supabase Free Nano, us-east-1, PostgreSQL 17.12. Both plans were verified free; remaining whole-account allowances are not inferred from this sample.

| Observation | Actual result | Limitation |
| --- | --- | --- |
| Public smoke | Eleven sequential requests, no retries; three grading reservations | Health/readiness, CORS/projection, two grades, version conflict passed. |
| Network readiness | n=5; p50 584.48 ms; nearest-rank p95/max 695.60 ms; min 351.49 ms | Small descriptive sample including network/TLS; not an SLO. |
| Correct/incorrect grade | 364.79/335.18 ms client total; 56.12/31.02 ms API middleware time | n=2, bootstrap grading; no diagnosis computation. |
| Provider cold group | n=2; duration average/max 902.5/1,006 ms; TTFB 1,313/1,657 ms | Provider GET / probes returning 404, before public smoke; no database grading. |
| Provider hot group | n=16; duration average/max 34.5/127 ms; TTFB 43.19/137 ms | Mixed smoke/browser/preflight/version requests; fixed 11:56–12:01 UTC window. |
| Provider memory | Cold peak 201 MB; hot peak 210 MB; allocation 2,048 MiB | Includes more than application-process RSS. |
| Application process | Maximum 64,660 KiB across thirteen captured records | Linux high-water RSS, not billed or per-request allocation. |
| Function artifact | Reported 12,699,243 bytes; Python 3.12; timeout 15 s | Encoding unspecified; no uncompressed-size claim. Standard build passed. Build cache is separate. |
| Provider CPU / transfer | 250 ms summed active CPU; 19,008 origin-transfer bytes | Only this deployment's eighteen-invocation window, not team totals or remaining quota. |
| Database | 11,237,043 bytes; release relation 49,152 bytes | Below published 500 MB database allowance; distinct from dashboard disk percentage. |
| Connections | API pool min 0/max 1; runtime role limit 10; verification concurrency 4 | Per-instance pools alone do not cap all instances. Shared role/pooler limits still matter. |

Evidence: [public HTTP samples](evidence/phase1_deployment.json), [resource metadata](evidence/phase1_resources.json), [provider query/result](evidence/phase1_provider_metrics.json), and [hosted SQL checks](evidence/phase1_database.json). Reproduce provider metrics with the official Vercel CLI metrics command, using --data - --json --scope pranjal-tyagi-ai and supplying the saved query object through stdin, subject to free retention. No paid observability feature was enabled.

The actual browser connected, selected n, submitted, and displayed the server explanation: [captured feedback](evidence/phase1_live_grading.jpg). This used one additional grading reservation. The page begins with its labeled example; diagnosis, saved progress, and reassessment remain unimplemented.

Hosted quota/privilege/immutability/expiry checks passed and temporary fixtures were removed. The read-only TLS/grants/owner/hash audit passed. Repeated reseeding preserved the digest, and a new API deployment continued to read it. Full project-loss restore, pause/resume, and rollback remain Phase 5 work.

Local lint/format/content and ten API tests passed; five SQL checks skipped without a local test DB. [Source CI](https://github.com/Pranjaltyagi76/LearnGraphAI/actions/runs/44730530223) passed backend/frontend with isolated PostgreSQL 17 and four browser tests. Fixture browser coverage is distinct from the live browser/SQL checks above. Earlier TypeScript 7 lint incompatibility was resolved by pinned TypeScript 6.0.3. Approved local verification ran outside the restrictive process sandbox.

The earlier unconfigured API returned 503 and the actual browser preserved the example; the configured deployment now returns readiness 200. Cold provider probes were measured, but isolated end-user cold grading latency, full-analysis compute, full-loop page performance, long-duration load, and model-quality metrics remain unmeasured. Phase 1 viability passed without Render or payment.


## 10. Phase 0 engineering verification — 20 November 2026

[Review evidence](evidence/phase0_review.json) records lint/format, artifact and split validation, 68 passing local tests, five locally skipped isolated SQL tests, and independent Node verification of nine canonical/hash/storage vectors plus five artifact hashes. These are contract/content checks, not analysis latency, a browser-store test, or model-quality measurements. The Phase 1 deployed performance observations above are unchanged. No new service, migration or deployment was needed for the reviewed draft.

## 11. Phase 2 offline verification — 20 November 2026

[Local review evidence](evidence/phase2_review.json) records 185 passing local tests, five skipped isolated SQL tests, the existing deprecation warning, lint/format, frozen-input checks, Node conformance and exact saved-result reproduction. [Measured benchmark/model card](../evaluation/model_card.md) covers prediction/diagnosis/plan behavior, not latency or learning benefit. The implementation uses only existing runtime packages and Python standard-library arithmetic/metrics. No new provider invocation, deployment/resource claim or load measurement is made. Phase 1 hosted measurements remain historical observations of bootstrap grading; they are not full-analysis timings.
