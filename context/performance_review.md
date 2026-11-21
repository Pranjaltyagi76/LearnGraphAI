# Performance review

**State:** Phase 5 bounded compute, public workload/page, provider cold/hot/resource and actual recovery measurements recorded. These are descriptive engineering samples, not capacity or availability guarantees. **Date:** 21 November 2026.

This file covers latency, resources, reliability under bounded load, and the effect of free hosting. Model-quality evidence belongs in [benchmark.md](benchmark.md). Runtime constraints originate in PROJECT Sections 12–14 and [requirements](../requirement.md), especially NFR-03–06/10/13.

## 1. Separate constraints, targets, and results

| Measure | Initial requirement/target | Classification | Current result |
| --- | --- | --- | --- |
| Request body | Maximum 256 KiB, enforced while counting bytes | Application hard bound | Implemented; chunked oversized-body contract test passes. |
| History | At most 200 visitor events plus 100 seed events | Hard bound | Implemented; schema boundary tests and 300-event maximum-history core fixture pass. |
| Search/plan | Depth ≤3; ≤3 candidates; ≤5 items | Hard bound | Implemented and verified by direct, variant and full-audit plan checks. |
| Analysis work | Ten-second route budget with tighter DB/receive deadlines | Initial budget | Full analysis deployed; maximum-history sequential p95 24.42 ms locally, separate network/provider samples below. |
| Shared quota | Ten analyses/minute/client identifier; 1,000/day globally | Initial operational guard, not provider entitlement | Hosted concurrent client/global denial and counter atomicity passed; bootstrap grading uses this guard. |
| Quota retention | Expiry within 48 hours; bounded cleanup | Application retention bound | Hosted logical-expiry check passed. Physical deletion is opportunistic, not guaranteed during idle periods. |
| Warm API response | Proposed p95 ≤2 s at declared low volume | Target, not SLO | Eight public analyses at concurrency two: nearest-rank p95 440.65 ms. |
| Pure analysis compute | Proposed p95 ≤100 ms on declared maximum-history fixture | Local target | 100 measured / five warmup samples: p95 24.42 ms on Windows/Python 3.12.10. |
| Initial learner page | Proposed usable control within 3 s under stated conditions | UX target | Eight fresh unthrottled Chromium contexts; max 1,749.70/1,774.47 ms for desktop/mobile viewports. Not physical mobile or a network guarantee. |
| Bundle/memory/DB pool | Fit verified free limits | Deployment gate | Reported API package 12.15 MB; observed peak 216 MB / allocation 2,048 MB; one SQL client connection per instance. |

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
| Phase 3 complete learning loop | Actual live evidence retained | Bounded gate passed; expanded full release checked in Phase 4/5. |
| Phase 5 release review | Compute, low-volume public/page, provider resource, real quota/pause recovery and rollback records | Engineering checks passed; owner-approved synthetic-demo scope accepted, human validation deferred. |

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

## 12. Phase 3 public-loop samples — 20 November 2026

[Actual browser/API evidence](evidence/phase3_live.json) records ten explicitly timed samples (six metadata/health/readiness/evaluation reads and four primary-browser analysis actions), plus a separately recorded independent-browser analysis. There were five analysis reservations in total. Browser metadata/asset traffic is not all included in this timed list. All recorded responses are 200; versions, future-answer projection and production CORS pass.

The four primary analysis actions took 649, 572, 568 and 605 ms from UI action through response capture. These values include browser/action/network time; they are not pure compute timings, an SLO, a high-load test or classified cold samples. The first browser completes two practices and a different reassessment; the second receives unchanged canonical evidence. Refresh/reset and mobile overflow checks pass. Desktop/mobile captures were inspected. No browser exceptions were captured.

[Release evidence](evidence/phase3_release.json) records provider BUILDING→READY intervals (API 17,190 ms; frontend 18,671 ms), exact source/deployments, actual database size, package bytes, TLS/grants and unchanged legacy hash. No updated function-memory/bundle or cold-load claim is made. Provider error-level scans for these deployments found no matching entries in the recorded windows. There are no configured drains; existing provider logs/bounded request metrics remain the monitoring boundary, with no paid service added. Current local checks: 192 backend tests passed, six isolated SQL tests skipped locally, twenty-three browser tests passed; source CI passed with real isolated SQL and browser checks.

## 13. Phase 4 functional and accessibility review — 21 November 2026

[Local evidence](evidence/phase4_local.json) records 207 backend tests passing, six SQL checks skipped locally, and all 32 Chromium tests passing with the full fixture and retained slice. CI runs the isolated PostgreSQL checks. The initial Linux mobile scroll-focus failure is retained with its fix; later manual review adds correct control-group semantics and visible mobile learner navigation. Lint/typecheck/production build, frozen/generated inputs and exposed-regression reproduction pass. No runtime dependency was added; axe-core is development-only.

The [initial public measurement](evidence/phase4_live.json) records thirteen timed samples: nine metadata/readiness/profile reads and four primary-browser analysis actions. The independent browser's fifth analysis is recorded separately. The four UI-action-to-response samples were 658, 684, 730 and 651 ms. These include browser/action/network time; they are neither pure compute nor classified cold samples or a load/SLO claim. The deliberately unprovided full-catalog quality endpoint returns 404; that probe and page assets are outside the thirteen timed samples.

Desktop/mobile production captures were inspected. Automated accessibility scans cover four routes at two sizes; remaining SVG contrast uncertainty requires the targeted rendered-color review rather than claiming complete conformance from zero violations. The final follow-up proof and release record identify corrected source/deployments. Full-load, application cold-start, memory/bundle and disaster-recovery measurements were not repeated here and remain Phase 5 work. No learning or full-catalog quality improvement is claimed.

The [final corrected-source proof](evidence/phase4_live_v2.json) repeats the same bounded flow, with primary UI/action response samples of 753, 630, 633, 765 ms. Both runs are retained, totaling ten analysis reservations. [Targeted graph review](evidence/phase4_graph_accessibility.json) measured minimum text/arrow contrast of 6.2749:1/3.7294:1 and verified the named group and keyboard list. These small samples retain the limits above.

## 14. Phase 5 final release measurements

[Maximum-history profile](evidence/phase5_compute_v2.json) uses a fixture-only 100 seed + 200 visitor events without changing canonical profiles. Request/bundle are 69,807/150,391 canonical bytes. One hundred sequential samples after five warmups measured p50 16.63 ms/p95 24.42 ms; twenty additional samples use four threads. Three fresh Python processes separately record import/fixture/analysis/start-to-exit costs. The manifest accurately records a dirty delivery tree, measured source commit and script hash. The initial unbound formatting-era measurement remains preserved; v2 is the source-bound record.

[Public workload](evidence/phase5_public_profile.json) makes eight no-mutation full-analysis calls at concurrency two, followed by explicit 409/413 checks. All eight were 200 and repeated the same digest; p95/max 440.65 ms includes network. Eight fresh browser contexts at widths 1365/360 (unthrottled desktop hardware, not real mobile devices) measured usable analysis controls with maximum 1,749.70/1,774.47 ms. No production capacity, statistical confidence or high-load claim follows from eight samples.

[Final deployment-specific provider metrics](evidence/phase5_provider_final.json) classify two cold invocations: mean duration 1,000 ms, max 1,122 ms, average TTFB 1,169.5 ms, peak memory 204 MB. Fifty-eight hot invocations have mean duration 17.22 ms/max 231 ms, average TTFB 26.07 ms, peak memory 216 MB. Allocation is 2,048 MB. Groups include provider probes/metadata and the declared production drills, not exclusively grading; they are not an isolated client cold-grading benchmark. Included twenty-minute queries were used after a historical query requested a paid feature; no paid feature was enabled. Earlier mixed-deployment observations remain separately recorded.

[Release record](evidence/phase5_release.json) binds the 12.15 MB reported package (not asserted uncompressed), configured Python 3.12 / 15 s timeout, basic build machine and exclusions for owner/evaluation/migration/data/test/env inputs. Production dependencies are unchanged. [Hosted audit](evidence/phase5_hosted_final.json) records 11,433,651 database bytes, thirteen passing effective-access/hash/quota checks and actual-secret scans.

Real pause/resume, pending refresh/manual retry, 429 recovery and public compatible rollback/promotion pass. The short coordination timeout, test-runner cleanup race, fixture row-format mismatch and initial post-restore quota-start 503 remain recorded; successful reruns do not erase them. Long-duration capacity, arbitrary failure combinations, student benefit and always-on free hosting are not established.
