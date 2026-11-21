# Free P0 operations and recovery

Verified 21 November 2026. These procedures concern the synthetic portfolio demo, not real student records. [Release evidence](evidence/phase5_release.json) and [acceptance mapping](release_acceptance.md) identify the tested scope. Never upgrade, add a card/add-on, or enable a keepalive to make a drill pass.

## Before changing service state

Confirm the existing project IDs and aliases in [deployment.md](deployment.md), the exact source CI, the active/retained release tuple, and the current known-good deployment IDs. Keep owner/runtime credentials in private provider configuration and ignored `backend/.env.local`; never print them or include them in a backup artifact. Take a metadata/hash snapshot with `python -m scripts.audit_hosted --output ../context/evidence/a-new-hosted-audit.json` from backend/. This audit only changes uniquely named temporary quota buckets and removes those buckets afterward.

## Paused database and pending answers

The actual drill used `frontend/scripts/drill-release.mjs --mode outage --output ../context/evidence/a-new-outage.json`. Run it from frontend/ in a fresh synthetic browser. Its ignored `.vercel/phase5-control.json` coordinates these steps:

1. Wait for `ready_to_pause`; pause only the known Supabase Free project.
2. Once the provider reports inactive, write `{"state":"paused"}` to that control file.
3. Wait for `outage_observed`: public readiness/analysis are `503`, the exact pending event survives refresh, and read-only examples work. Warm cached metadata may still be readable; it is not proof that grading is available.
4. Resume the project immediately, including if the browser harness failed. Do not repeat pause requests or change billing. Startup can take several minutes.
5. Confirm the actual public `/ready` returns 200, then write `{"state":"restored"}`. The harness reloads, explicitly clicks retry, verifies the same request snapshot and accepts exactly one local event.

The observation window is fifteen minutes; it never sends a timed automatic POST retry. A metadata outage may hide the workspace during refresh, while IndexedDB still preserves pending work. Reconnect/reload after service recovery. Always finish with the database healthy and the public API ready. The initial short timeout and a coordination-file deletion by the local test runner are retained as failed harness attempts; coordination now lives outside auto-cleaned test output.

For ordinary users, keep/export pending work, wait for service recovery, and retry manually. Never reset or discard a response merely to hide a server failure. Browser storage can be evicted; session-only progress cannot survive refresh.

## Quota recovery

`node scripts/drill-release.mjs --mode quota --output ../context/evidence/a-new-quota.json` exercises real denial without spoofing client headers or weakening limits. It makes at most fourteen POST attempts, verifies repeated snapshots add no evidence, reaches `429`, preserves a staged response across refresh, waits for `Retry-After`, and explicitly retries once. Analysis attempts share the ten/minute/client and 1,000/day limits. Stop and wait when exhausted; do not add a paid fallback or change identity to bypass a limit.

Missing quota storage is exercised against actual isolated PostgreSQL in CI: the fixture temporarily renames its own test table, requires API `503`, rolls the transaction back, then verifies reservations work. It never renames a production table. Hosted four-connection tests separately verify exact admission/counter atomicity and global denial, using only isolated temporary namespaces.

## Restore canonical content into an empty database

No visitor history exists on the server. Authored source plus immutable measured-summary inputs restore canonical data; quotas can start empty. This is not a backup of credentials, browser histories or arbitrary future user data.

Privately point `MIGRATION_DATABASE_URL` to the intended empty database, verify its identity first, then from backend/:

```powershell
uv run --frozen python -m scripts.manage_db migrate
uv run --frozen python -m scripts.manage_db seed
uv run --frozen python -m scripts.publish_analysis publish --release learngraph-review-v1 --evaluation ../evaluation/results/phase3-regression-v1/test.json
uv run --frozen python -m scripts.publish_analysis publish --release learngraph-full-v1
uv run --frozen python -m scripts.manage_db verify
uv run --frozen python -m scripts.publish_analysis verify --release learngraph-review-v1 --evaluation ../evaluation/results/phase3-regression-v1/test.json
uv run --frozen python -m scripts.publish_analysis verify --release learngraph-full-v1
```

Use the exact historical Phase 3 summary for the reviewed package. A later summary has different package bytes and must not overwrite an existing row. Provision a fresh restricted login with the existing `scripts.provision_runtime` only for a genuinely new environment: it refuses an existing runtime role or configured runtime URL, generates secrets privately, and writes only the ignored local environment. Restore existing credentials through the owner's private credential process instead of resetting/adopting an existing role. Configure Production Secrets through the official CLI stdin/private provider UI, never command arguments or chat. Verify runtime TLS/grants/hashes before activation. Keep `RELEASE_ID=phase1-v1`, `ANALYSIS_RELEASE_ID=learngraph-full-v1`, and `RETAINED_ANALYSIS_RELEASE_IDS=learngraph-review-v1`.

CI actually restored all three exact packages twice into a newly created empty PostgreSQL 17 database, checked hashes/immutability/runtime access, and dropped only that isolated `_test` database. The database fixture rejects non-local hosts. The real Supabase pause/resume drill and post-resume hosted audit independently verify the existing remote project; no destructive production reseed or paid restore feature was used.

## Compatible deployment rollback

Hobby permits rollback to the immediately previous production deployment. Before releasing, retain that known-good pair and verify the version support matrix. The Phase 5 drill switched both public aliases from the candidate to the preceding pair, confirmed full and retained analysis on the actual public API, then promoted the candidate API followed by the frontend. Both releases use the same frozen content/protocol; the drill does not claim a destructive content downgrade or history migration.

Use the connected Vercel rollback/promote operations or the official CLI with explicit team/project/deployment scope. Wait for each project's alias mapping to finish. Recheck `/ready`, the active release, retained seed route, and a clean-browser loop. Promotion restores domain auto-assignment after rollback. Automatic Git-to-production linkage is still not configured; pushing source alone does not deploy. Never force-push Git history to perform a deployment rollback.

## Free-tier exhaustion and monitoring

Official terms and current plan checks are linked in [deployment.md](deployment.md). CLI independently confirmed active Vercel Hobby; Supabase confirmed Free. Database size was about 11.4 MB versus the published 500 MB allowance. Remaining whole-account monthly transfer/build/CPU allowances were not exposed by the available billing response; do not fabricate them or infer them from a small sample. Monitor the provider dashboard before expanding traffic.

Historical observability outside the included window requested a paid plan. It was not enabled; the recorded queries use the included recent twenty-minute window. No purchased domain, add-on, paid monitoring, automatic top-up, trial-credit dependency, new service or keepalive was introduced. If a free entitlement is exhausted, suspend live analysis and retain honest read-only examples. This release does not promise always-on free hosting or real-world educational benefit.
