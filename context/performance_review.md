# Performance review

**State:** Initial scaffold/build/failure-path review recorded; live database performance unmeasured. **Date:** 20 November 2026. Proposed targets remain distinct from the small observations below.

This file covers latency, resources, reliability under bounded load, and the effect of free hosting. Model-quality evidence belongs in [benchmark.md](benchmark.md). Runtime constraints originate in PROJECT Sections 12–14 and [requirements](../requirement.md), especially NFR-03–06/10/13.

## 1. Separate constraints, targets, and results

| Measure | Initial requirement/target | Classification | Current result |
| --- | --- | --- | --- |
| Request body | Maximum 256 KiB, enforced while counting bytes | Application hard bound | Implemented; chunked oversized-body contract test passes. |
| History | At most 200 visitor events plus 100 server seed events | Application hard bound | Not implemented/tested. |
| Search/plan | Prerequisite depth ≤3; ≤3 diagnoses; ≤5 plan items | Application hard bound | Not implemented/tested. |
| Analysis work | Ten-second application time budget with tighter DB/operation deadlines | Agreed initial budget; cold behavior must be measured | Not measured. |
| Shared quota | Ten analyses/minute/client identifier; 1,000/day globally | Initial operational guard, not provider entitlement | Atomic SQL implemented; isolated PostgreSQL CI passes. Hosted Supabase not configured. |
| Quota retention | Expiry within 48 hours; bounded cleanup | Application retention bound | Not implemented/tested. |
| Warm API response | Proposed p95 ≤2 seconds end-to-end at the defined low-volume workload | Engineering target to review in Phase 1 | Not measured; not a promise. |
| Pure analysis compute | Proposed p95 ≤100 ms for the maximum valid fixture on the declared local machine | Profiling target; excludes DB/network/cold boot | Not measured. |
| Initial learner page | Proposed usable primary content within 3 seconds under a stated device/network profile | UX target; report tool and conditions | Not measured. |
| Bundle/memory/DB pool | Fit verified free provider limits with documented margin | Deployment gate, exact values observed in Phase 1 | Not measured. |

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
| Phase 1 deployment viability | Both Vercel builds READY; health/CORS and unavailable readiness observed | Hosted database gate still pending; no inference latency claim. |
| Phase 3 complete learning loop | Not run | Pending full learning-loop implementation. |
| Phase 5 release review | Not run | Release not ready. |

Future reviewers must update this ledger from real execution. Do not replace `not measured` with guessed production numbers or promise always-on free hosting.

## 9. Observed Phase 1 checks — 20 November 2026

- Source commit `daef1171bdf2608911dba09ea6d658a5f19c5dfb`; local Windows, Node 24.18.0, Python 3.12.10. Local API suite: ten passed; four PostgreSQL checks skipped locally. The remote backend job with isolated PostgreSQL 17 and frontend job both succeeded: [CI run](https://github.com/Pranjaltyagi76/LearnGraphAI/actions/runs/44700160117).
- Frontend lint/typecheck/production build pass. Four local Chromium tests pass: recorded labeling, unavailable API, 390 px layout overflow check, and connected grading contract via an explicitly intercepted fixture. The last case does not verify Supabase.
- Initial scaffold attempts exposed unsupported TypeScript 7 lint parsing and Windows sandbox worker/cache limitations. The compatible TypeScript 6.0.3 toolchain is pinned; the production build and tests succeeded outside the restrictive process sandbox. No provider security setting was weakened.
- Two public API smoke requests after deployment/environment correction: `/health` 200 JSON in 809 ms, `/ready` 503 `not_configured` in 525 ms, including client network time. These are two descriptive observations, not p95 measurements, cold/warm classification, or successful database latency.
- Production CORS returns the exact frontend origin. An actual browser click displays the unavailable notice and preserves the prerecorded example; no accepted response is fabricated.
- API builder logs: Python 3.12, runtime install from uv.lock, output build 3 seconds. Build cache 9.29 MB is not runtime bundle size. Both Vercel deployments are READY in `iad1`; runtime memory/bundle size, database connections, cold starts, and complete analysis latency remain unmeasured.
- Shared limiter concurrency/global-budget and least-privilege/immutability checks are present in the passing isolated PostgreSQL CI job; they still require selected Supabase verification. No load test or model-quality benchmark was run.

### Prepared verification tooling — not a measured result

- The read-only `backend/scripts/verify_runtime.py` checks effective grants, owner separation, TLS, the quota function boundary, and source/published content hashes. Its database assertions passed isolated PostgreSQL CI in [run 44715705552](https://github.com/Pranjaltyagi76/LearnGraphAI/actions/runs/44715705552). Hosted execution is pending private credentials.
- `backend/scripts/smoke_deployment.py` caps a run at eleven sequential HTTP requests, including three grading quota reservations. It checks readiness, CORS, safe projections, correct/incorrect grading, and version conflict. It saves timings and sizes without raw answers. It has not been run against a configured hosted database.
- The API source now emits production-only JSON request measurements: request UUID, status, API duration, first request on the app instance, and Linux process peak RSS in KiB. It does not log submitted answers, network addresses, or secrets. This source is not yet deployed. A first instance request does not measure total platform cold-start time; process peak RSS is not provider-billed memory or per-request allocation.
- Supabase dashboard showed Healthy Nano in `us-east-1`, 5/60 connections, RAM 66%, disk 16%, CPU 0% immediately after startup and before application migration. These are single provider overview observations, not workload peak measurements or the 500 MB database allowance's utilization.
