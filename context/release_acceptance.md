# P0 engineering release acceptance — 21 November 2026

Candidate `0c56e86ba7ad63d43a8b8ed8b36abdf9601a7808`; [source CI](https://github.com/Pranjaltyagi76/LearnGraphAI/actions/runs/44916553094) passes **215 backend tests and 32 Chromium tests**, including eight real isolated PostgreSQL checks. [Release record](evidence/phase5_release.json) binds actual public deployments and rollback. The engineering checks below pass. On 21 November 2026 the owner explicitly approved engineering-reviewed synthetic-demo scope and deferred human content validation; no AI review is represented as human sign-off. There is no student validation, always-on availability, calibrated mastery or learning-gain claim.

| Requirement | Actual acceptance evidence |
| --- | --- |
| FR-01 | Four synthetic profiles; no registration. Clean browsers in [public proof](evidence/phase5_live.json) and all-profile browser checks in CI. |
| FR-02 | Frozen 12-node/17-edge DAG, cycle/reference/direction checks and graph/list alternatives; `check_phase0`, engine and graph tests. |
| FR-03 — engineering scope approved | [72-question/12-lesson review](../curriculum/full-review.md), distinct roles/versions/provenance and reproducible content checks. Engineering review is not independent educator review. |
| FR-04 | Immutable source/stored hashes, denied runtime writes, separate browser sandboxes; [hosted audit](evidence/phase5_hosted_final.json) and two-browser proof. |
| FR-05 | IndexedDB transactional recovery, reset and tab conflicts in real-browser CI; [actual paused-database pending recovery](evidence/phase5_outage_v3.json). |
| FR-06 | Server-owned grading/tags/version lookup; malformed metadata and key/explanation projection checks in backend/HTTP/browser suites. |
| FR-07 | Independent canonical/hash vectors, duplicate/conflicting IDs/order tests and [real repeated-snapshot quota drill](evidence/phase5_http_quota_v2.json). |
| FR-08 | Distinct-first/primary-only/known-zero-hints tests; hinted/repeat/lesson exclusions in both frozen audits and replay tests. |
| FR-09 | Unknown/early/supported estimates, explicit counts and null no-data estimates; browser states and full-track sparse controls. |
| FR-10 | Bounded upstream paths, competing gaps, abstention and actual event IDs; full audit plus independent graph/tie/depth variants. |
| FR-11 | All three plan baselines checked for catalog validity, ordering, readiness and exhaustion in [full audit](../evaluation/results/phase5-full-v1/report.md); direct hard-bound tests. |
| FR-12 | Real two-practice/distinct-reassessment loop; honest 3/6 correct, 0.5/developing exhausted outcome in [public proof](evidence/phase5_live.json); twelve concept workflow fixtures. |
| FR-13 | Bundle versions/digest/cache validation, pending/acknowledged CAS, delayed response and profile/reset race tests. |
| FR-14 | Fixed evidence templates and explanations; runtime requires no LLM key/provider/training. Diagnosis scores are not causal probabilities. |
| FR-15 | Dashboard, graph/list, timeline, locks, unknown/early/mixed/empty/error states and keyboard/mobile checks. |
| FR-16 | Real [429/retry](evidence/phase5_http_quota_v2.json), [paused dependency](evidence/phase5_outage_v3.json), [409/413](evidence/phase5_public_profile.json), plus browser mismatch/corrupt/exhaustion tests. |
| FR-17 | Real database pause left the versioned read-only example accessible, without a submission form; public failure-state evidence retained. |
| FR-18 | Freeze-before-first-measurement [full packet](../evaluation/full-manifest.v1.json), disjoint groups, training-only rate, causal prefixes, baseline comparisons, denominators and limitations. Same items/families and known implementation exposure are disclosed; no tuning after test outputs. |
| FR-19 | Byte/history bounds, ten/minute/client and 1,000/day shared atomic guards; isolated missing-table 503 and hosted concurrent/global denial. |

| Requirement | Actual acceptance evidence |
| --- | --- |
| NFR-01 | Existing active Hobby and Supabase Free verified; no new service/payment/paid fallback. Whole-account remaining allowances not fabricated. |
| NFR-02 | Final actual browser → API → database path passed after restart, real pause/resume, rollback and promotion. |
| NFR-03 | 256 KiB receive bound; 200 visitor/100 seed bounds, three-edge traversal and five-item plan tests. Maximum-history fixture has 300 graded events. |
| NFR-04 | [Local compute/process-start](evidence/phase5_compute_v2.json), [public low-volume/page samples](evidence/phase5_public_profile.json), [provider cold/hot metrics](evidence/phase5_provider_final.json), and 12.15 MB reported package. Samples are not an SLO/capacity guarantee. |
| NFR-05 | Twenty hosted attempts through four independent SQL connections admitted exactly ten; global denial increments neither counter; real public 429 verified. |
| NFR-06 | Missing real SQL quota table gives safe API 503, rollback restores function; actual paused database gives 503 with working read-only examples. |
| NFR-07 | Actual private values scanned against tracked/built files without recording them; future answers omitted from normal public seed responses. Only synthetic demo/audit data used. |
| NFR-08 | Runtime TLS, role separation, effective grants, hardened private guard and excluded public roles verified on hosted SQL. |
| NFR-09 | Immutable version/hash tuples, frozen audit manifests, normalized source hashes, exact result reproduction and retained failures. Unfavorable test prediction losses published. |
| NFR-10 | Owner scripts, evaluation, migrations, data, tests and env files excluded from runtime source package; production dependencies unchanged. Canonical data survived redeployment; visitor history remains browser-local. |
| NFR-11 | Clean isolated restore/reseed of three exact packages; real remote pause/resume and compatible public rollback/promotion. [Operator runbook](recovery_runbook.md) distinguishes canonical recovery from credentials/browser history. |
| NFR-12 | Real keyboard/focus/mobile checks; eight final public scans, graph/list equivalence, reduced motion and [direct rendered SVG contrast review](evidence/phase5_graph_accessibility.json). No complete assistive-technology conformance claim. |
| NFR-13 | Daily HMAC client identifiers, logical quota expiry within 48 hours, bounded opportunistic cleanup, no raw answers/addresses in application metric payloads. Idle physical deletion is not guaranteed. |

The 24-case full synthetic audit has 659 eligible predictions and six exclusions. Concept smoothing has worse test log loss/Brier (0.540454/0.175670) than global (0.415177/0.119409); diagnosis policies tie on sixteen labeled-gap cases. No accuracy threshold was invented to turn this into an educational claim. Full-v1's immutable package still contains no compatible hosted quality summary; the public report/methodology expose the measurements instead of overwriting it.

Initial failures remain in [CI evidence](evidence/phase5_ci.json), the two failed outage harness files, and the first quota-start 503. They are resolved by the corrected fixture, stable coordination/observation window and successful real public reruns. The application deliberately stops grading when a dependency or quota is unavailable; a provider-controlled outage is not hidden by a fake live result.

Supabase returned one expected INFO for the private quota table's deliberately absent public policies; runtime/public direct table access is denied and only the hardened guard writes it. [Linter explanation](https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy).

Owner scope decision: **“Accept engineering-reviewed synthetic-demo scope; defer human content validation.”** This resolves the original FR-03 human-review release condition for the bounded synthetic portfolio release only. It does not waive privacy, correctness, quota or free-hosting gates and does not authorize real-student use.
