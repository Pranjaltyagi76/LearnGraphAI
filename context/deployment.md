# Free deployment and recovery

**State:** Phase 1 feasibility and Phase 3 public analysis/practice/reassessment loop verified on the existing Vercel Hobby/Supabase Free topology. Full product release remains pending. **Date:** 20 November 2026. **Requirements:** NFR-01–08/10/11/13 and FR-16/17/19 in [requirement.md](../requirement.md).

This runbook covers the retained Phase 1 baseline, Phase 3 rollout below and the future Phase 5 release gate. The user authorized Phase 1 implementation and confirmed Hobby/no paid billing. Observed hosting state is recorded below; a successful build does not prove database readiness. Tested local entrypoints are in the root README and backend migration README.

## 1. Zero-cost policy

- Recurring service budget is **₹0 / $0**. No paid subscription/API/GPU/domain, automatic top-up, or dependence on expiring trial credits.
- Do not attach payment methods or enable paid billing for this project. A free feature requiring paid billing is deferred or replaced with a verified free alternative.
- Use included provider subdomains and TLS. Do not buy a domain.
- Alerts are observational; they do not impose a hard spend limit. Free service suspension is preferable to charges.
- No artificial keepalive traffic, duplicate-account quota workarounds, or paid always-on fallback.

## 2. Planned inventory

| Resource | Intended setup | Actual ID/URL/state |
| --- | --- | --- |
| Git source | Owner's LearnGraphAI repository, `main` | [Repository](https://github.com/Pranjaltyagi76/LearnGraphAI); branch delivery verified separately through Git. |
| Frontend | Vercel Hobby project, root `frontend/` | `prj_xN0EgVf3CJdn1TyTEbjZehtJK9Wf`; [public preview](https://learngraph-ai-web.vercel.app), READY. |
| API | Separate Vercel Hobby project, root `backend/` | `prj_K3hvjn2d1vKQDzJBTm7DJ14XC0iA`; [public health](https://learngraph-ai-api.vercel.app/health), READY. |
| Database | Supabase Free | `qnboukxsaczidpwtnadl`, `learngraph-ai`, `us-east-1`; Healthy Nano in Free organization `ijxtakdqmtyzsqljeifc`. Migrated/seeded; TLS runtime audit passed. |
| Alternative API | Render Free only if required by measured failure | Not provisioned. |
| CI | Public GitHub repository, standard runners | `.github/workflows/ci.yml`; frontend/backend jobs passed with real isolated PostgreSQL 17. |

Confirm the actual provider account/team, repository, project roots, environment, and release commit before mutation. Do not accidentally deploy this project into an unrelated paid team.

## 3. Provider checks

The values below originate in the 20 November 2026 planning snapshot recorded in PROJECT Section 14. Vercel Hobby and Supabase Free eligibility have since been observed on the selected accounts; the dated evidence below distinguishes account checks from unmeasured remaining usage. Recheck official docs/account allowance at release.

| Provider | Snapshot / consequence | Official reference |
| --- | --- | --- |
| Vercel Hobby | Personal noncommercial scope; published allowances include 4 active CPU hours, 360 GB-hours memory, 1M function invocations, 100 GB fast transfer. Two projects can share quotas. | [Hobby](https://vercel.com/docs/plans/hobby), [eligibility](https://vercel.com/pricing) |
| Vercel Functions | Native FastAPI; current planning values: 2 GB Hobby memory, 300-second maximum, 500 MB standard Python bundle, 4.5 MB body/non-streamed response limit. Application limits are smaller. | [FastAPI](https://vercel.com/docs/frameworks/backend/fastapi), [limits](https://vercel.com/docs/functions/limitations) |
| Supabase Free | 500 MB database, 5 GB egress, inactivity pause after a week, no included automatic backups. | [Pricing](https://supabase.com/pricing) |
| Render Free | Sleeps after 15 idle minutes, restart can take about a minute; 750 free hours/workspace/month. Bandwidth/build overages can incur charges with payment attached; no-payment paths can suspend. | [Free services](https://render.com/docs/free) |
| GitHub Actions | Standard public-repository runners are free; larger runners and excess artifact/cache storage may cost. | [Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions) |

Do not size traffic from invocation allowance alone. CPU, memory, egress, database work, builds, and abuse can bind first. Application quotas are not a guarantee against provider exhaustion or a promise of uptime.

## 4. Environment ownership

These are proposed application variable names, not existing secrets or a finalized SDK-specific interface. Freeze exact names with the scaffold and record names/placeholders only in `.env.example`.

| Proposed name | Location | Purpose / disclosure |
| --- | --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | Frontend | Public API origin, intentionally visible in browser bundle. |
| `DATABASE_URL` | API runtime secret | Least-privilege pooled Postgres access; never use a `NEXT_PUBLIC_` prefix. |
| `MIGRATION_DATABASE_URL` | Owner-controlled migration environment | Administrative/session-compatible migration route; exclude from frontend and routine runtime. |
| `ALLOWED_ORIGINS` | API | Exact production/local and explicitly configured preview origins; no blanket wildcard as an auth substitute. |
| `CLIENT_ID_HASH_SECRET` | API runtime secret | Rotate/hash short-lived quota signals without logging raw identifiers. |
| `APP_ENV`, `LOG_LEVEL` | API | Bounded environment/logging selection; no verbose sensitive production traces. |
| Published release manifest identifier | Backend config | Compatible seed/catalog/graph/model revision; choose exact representation in Phase 0. |

Use GitHub/Vercel Git integration where possible to avoid unnecessary deployment tokens. Future CI tokens, if needed, belong in protected provider secret stores and only reviewed secret-bearing steps. No Gemini key is required in P0.

## 5. Phase 1 feasibility procedure

1. Resolve Phase 0 contracts/content reachability sufficiently for the first slice. Create minimal Next.js/FastAPI code with currently supported compatible pinned runtimes and lockfiles.
2. Verify ordinary local startup commands, API contract, placeholder-only environment example, and basic checks. Add exact tested commands to the root README.
3. Select the correct free accounts/projects and noncommercial portfolio scope. Confirm no payment/trial/paid resource is being enabled.
4. Create minimal canonical-data and atomic-quota migrations; verify roles, grants, RLS for exposed tables, and no public answer-key writes/reads.
5. Seed versioned synthetic source using a repeatable owner-only script. Record a compatible release manifest and hashes; do not overwrite published content in place.
6. Configure Supabase transaction pooling, TLS, small client pools, bounded queries/timeouts, and driver-specific prepared-statement compatibility. Use a separate compatible route for migrations. Avoid a paid IPv4 add-on by using the appropriate shared pooler. [Connection documentation](https://supabase.com/docs/guides/database/connecting-to-postgres)
7. Deploy API from `backend/`; verify supported entrypoint and only runtime dependencies. Explicitly include shared curriculum source if outside that root; prove it appears in the bundle without notebooks/raw data.
8. Deploy frontend from `frontend/`; set its actual API origin. Configure production CORS and intentional preview behavior; do not allow arbitrary origins by suffix guessing.
9. Verify `/health`, `/ready`, profile/seed fetch, and a real analyze response from a clean browser. Check effective manifest/digest and safe error handling.
10. Measure bundle/memory/connection and warm/cold behavior using the performance-review protocol. Test 413/422/429/503, dependency failure, and labeled fallback.
11. Record actual URLs, versions, project IDs (nonsecrets), date, commands, and results. Pass the gate only if the free live round trip works.

Local npm/API entrypoints are verified and documented in the root README. Hosted migrate/seed/verify, runtime provisioning/audit, and a repeated seed/verify have succeeded using the migration README commands. The migration was applied with the owner script; this does not create Supabase CLI migration-history entries.

## 6. Release procedure — Phase 5

- Identify exact release commit, selected project/team, and environment. Check working-tree/remote state; use no force-push.
- Run the relevant code/content/schema/browser checks and frozen benchmark; inspect runtime bundle and secret handling.
- Test backward-compatible migrations on nonproduction/local synthetic data before applying to the intended database. Do not let an untrusted PR run production migrations or access production secrets.
- Publish compatible immutable canonical revisions before activating a new release manifest. Verify all referenced versions exist.
- Build/test the candidate deployment, including the actual browser → API → database path and quota/fallback behavior. Keep development/preview writes away from production canonical data.
- For previews, use local/separate free database data where available; do not assume paid branching. Supabase free project limits may constrain a second database. If no isolated preview database fits, use local tests and read-only canonical preview access with explicitly bounded separate quota keys.
- Release only the tested artifact/commit through the chosen supported Git/deployment flow; record which was tested. Recheck the final public URL and clean-browser live loop.
- Update the inventory, roadmap evidence, performance record, and README from actual outcomes; remove “not deployed” only once observed.

## 7. Rollback and compatibility

Rollback is an application **and manifest** operation. Select the previous known-good deployment and its compatible published seed/catalog/graph/model revisions. Retain old revisions needed for restoration and public examples.

Do not blindly reverse a destructive migration or delete newer evidence. Prefer backward-compatible expand/contract changes; a schema rollback may require a separate reviewed recovery operation. After rollback, test readiness, versions, quotas, and the complete loop, and verify how the provider handles subsequent automatic Git deployments.

Browser sandboxes with incompatible versions must get an explicit reset/migration path. No silent reinterpretation of old responses.

## 8. Recovery without payment

| Incident | Action | Verification |
| --- | --- | --- |
| Supabase inactivity pause | Show examples, disable live acceptance, preserve local pending events; owner restores through supported process. | Ready check, canonical manifest hashes, quota guard, clean-browser analyze. |
| Database cannot be restored | Recreate a verified free project; apply migrations and reseed from authored synthetic sources; update API secret privately. | Repeatable seed and compatible manifests; no claim of recovering browser data from a nonexistent server store. |
| Quota exhausted | Return `429`/controlled unavailable state; wait for actual reset and inspect usage. | No automated paid upgrade/top-up or limiter bypass. |
| Quota store unavailable | Fail live analysis closed with `503`; examples remain explicit. | Atomic limiter test after restoration. |
| API cold/restarting | Bounded retries using identical history/event IDs; preserve pending state. | No duplicate evidence or false acknowledgement. |
| Vercel API path fails viability | Measure the same lightweight API on Render Free with no paid billing; account for sleep and cross-origin changes. | Actual free live loop; do not substitute an always-on paid service. |
| No suitable free live path | Reduce workload/scope and document live unavailability; examples remain labeled. | Release remains blocked until the live gate is passed. |

Canonical synthetic content is rebuildable from source. Manual operational backups must exclude secrets, quota identifiers, and any future sensitive data from public Git. P0 visitor progress is browser-local; clearing a browser cannot be repaired from server history that was never stored.

## 9. Operational checks

Check provider usage/settings after a meaningful release or availability incident, rather than introducing a scheduled keepalive service. Confirm CPU/memory/egress/build usage, DB size/connections, quota expiry cleanup, logs/artifact retention, and no unexpected paid resources.

Quota cleanup must run through a bounded supported path chosen in Phase 1 (for example, small opportunistic expired-bucket cleanup), not an assumed paid cron/worker. Guard every cleanup operation so it cannot become an unbounded request workload.

## 10. Deployment evidence record

| Field | Current value |
| --- | --- |
| Commit/environment/project IDs | API production source `568048188668d0a687b0b08677475f490099c7fd`; unchanged frontend source `daef1171bdf2608911dba09ea6d658a5f19c5dfb`. Team `team_mRdCuSvoFHIrkEm4K3UAPs7P` (`pranjal-tyagi-ai`). |
| Verified provider terms date/account limits | 20 November 2026: Vercel context reports `hobby`; owner confirms no paid billing. Supabase organization shows Free, project Healthy Nano. Workload resource observations below; full remaining account allowances not audited. |
| Frontend/API URLs and region | Public primary aliases above; region `iad1`. Team/deployment aliases may be protected; use the observed public primary aliases rather than disabling protection. |
| Runtime/package versions and bundle | Frontend Node 24.x, Next 16.4.6, React 19.3.1, TS 6.0.3. API runtime Python 3.12, builder metadata Node 26.x, locked Python dependencies; reported lambda artifact 12,699,243 bytes, allocation 2,048 MiB, timeout 15 s. Size encoding is unspecified; no uncompressed-size claim. |
| Migration/manifest versions | Owner script applied `001_bootstrap.sql`; immutable `phase1-v1` seeded. Recomputed/source/stored digest `ae54153b27c8193429f7b704ae592cb4c5d23f86dec5cc551b018974db5522dd`. |
| Browser/API/database checks | Health/readiness 200, exact production CORS, safe seed projection, correct/incorrect grading, version 409, hosted quota/privilege/immutability checks, and actual browser feedback all passed. |
| Restore/rollback exercise | Idempotent reseed/hash verification and a new API deployment preserving the canonical data passed. Full project-loss restoration, pause/resume, and version rollback remain Phase 5 work. |
| Cost/settings check | Existing Hobby team selected; owner confirms no paid billing; no paid resource/payment setup performed. Detailed remaining usage not measured. |

Add concrete evidence and failed results here when available. Never paste credentials or claim successful deployment from a planned runbook.

### Phase 1 deployment snapshot (historical)

- Frontend: `dpl_Csccn2itaDGyh8JvmQp8fT9CW1By` (READY).
- API: `dpl_8VtMQHBUV5boQida7rGVeaFrkTnh` (READY).
- Frontend production `NEXT_PUBLIC_API_BASE_URL` is `https://learngraph-ai-api.vercel.app`; API allows the public frontend and observed team alias. `DATABASE_URL` and `CLIENT_ID_HASH_SECRET` are hidden Production Secrets. The owner connection is excluded from Vercel runtime.
- Ignored service-local `.vercel/project.json` files identify the existing projects. Vercel CLI 66.5.0 was authenticated by the owner, and `project inspect --non-interactive` verified the API project/owner/root before secret configuration. Secret values were sent only through stdin; none were printed or placed in process arguments.
- Deployment metadata separates the reported **12,699,243-byte lambda artifact** from the **9,736,192-byte build cache**. API runtime is Python 3.12. [Resource evidence](evidence/phase1_resources.json) records exact metadata and process measurements.
- Deployments were triggered explicitly from the exact Git SHA. Project automatic Git linkage was not established; future pushes must not be assumed to deploy automatically. Configure the intended repo/roots through a supported authenticated path when available.
- **No remaining Phase 1 credential prerequisite:** the temporary `SUPABASE_OWNER_PASSWORD` field was removed after preparing the ignored owner connection. Future maintenance uses the private migration environment and restricted runtime audit; never paste credentials in chat or Git.

### Supabase provisioning observation — 20 November 2026

- Dashboard account `Pranjaltyagi76`; connected account displayed as **Pranjal's Supabase account**, Primary. Organization **Pranjaltyagi76's Org** displays **Free Plan**. The plugin is installed/enabled, but this chat exposes no Supabase tools; dashboard computer control was used instead.
- The user created project `learngraph-ai` after entering its database password themselves. Project `qnboukxsaczidpwtnadl` reached **Healthy**, **Nano**, **East US (North Virginia)**. No payment setup or paid add-on was performed.
- Creation form: Data API disabled; automatic RLS on new public tables enabled. Application access uses the private SQL schema and restricted `learngraph_api` login, which inherits the NOLOGIN `learngraph_runtime` group. Its role connection limit is ten; each API instance opens at most one client connection.
- Dashboard confirmed shared pooler `aws-0-us-east-1.pooler.supabase.com`, session port **5432**, transaction port **6543**, owner user `postgres.qnboukxsaczidpwtnadl`. IPv4 DNS and authenticated TLS access succeeded without a paid IPv4 add-on. Runtime uses transaction pooling with prepared statements disabled; owner migration uses session pooling.
- Supabase pricing rechecked: Free has a 500 MB database allowance, 5 GB egress, two active projects, and pauses after one inactive week. [Official pricing](https://supabase.com/pricing). No inactivity keepalive will be added.
- Runtime setup/audit helpers are in `backend/scripts/`; source [CI run 44730530223](https://github.com/Pranjaltyagi76/LearnGraphAI/actions/runs/44730530223) passed. Separate [hosted checks](evidence/phase1_database.json) verified quota concurrency/global denial, privileges, public-role exclusion, immutability, and logical expiry. Temporary verification quota buckets were removed.
- The eleven-request [public smoke](evidence/phase1_deployment.json), [provider metrics](evidence/phase1_provider_metrics.json), and [actual browser feedback](evidence/phase1_live_grading.jpg) complete the live Phase 1 evidence. Full model/learning-loop acceptance remains later work.

## Phase 3 production rollout — 20 November 2026

- **Frontend URL:** https://learngraph-ai-web.vercel.app/learn — production, READY, Next.js, deployment dpl_6Sj1MYrhVL7d9MLu7XpcvdeDwQSM.
- **API URL:** https://learngraph-ai-api.vercel.app — production, READY, FastAPI, deployment dpl_7BHbv5GpXZY8fXBpbUmyXm4iCw7J.
- **Exact deployed source:** 24826440aa9e2eab076b93a39beede64d6525001. [Source CI](https://github.com/Pranjaltyagi76/LearnGraphAI/actions/runs/44759575477) passed both jobs. API was deployed and its real readiness/release pointer verified before the frontend rollout. Provider BUILDING→READY intervals were 17.190/18.671 s, not application cold-start measurements.
- **Publication:** learngraph-review-v1 is a new immutable JSONB row containing the frozen five-artifact byte package and actual measured summary. The compatible release hash is unchanged; the distinct outer package hash binds publication bytes/evaluation. Owner publish/verify, connector metadata reads and restricted runtime source/stored/hash/TLS checks passed. No SQL migration or visitor-history table/write was added. Legacy phase1-v1/source hash is unchanged.
- **Activation:** Production ANALYSIS_RELEASE_ID=learngraph-review-v1 is non-secret Config. RELEASE_ID=phase1-v1 and both existing Production Secrets are retained. /ready preserves the legacy release_id while checking both configured packages; GET /api/v1/demo/release is the new analysis pointer. The ignored local file received only this non-secret activation key; existing private connections/secret values were preserved.
- **Free boundary:** same two Vercel projects and existing Hobby team (owner confirmed), and the connector now confirms Supabase organization Free/project ACTIVE_HEALTHY. No payment, plan, new service, add-on, paid monitor or runtime dependency was introduced. No scheduled keepalive is used. Account-wide remaining allowance is not audited here.
- **Observed end-to-end:** [public proof](evidence/phase3_live.json) uses two fresh browser processes and real production data without mocks. It verifies metadata/CORS/projection, two fresh practices/distinct reassessment, honest 0.5/developing exhaustion, acknowledged refresh, local reset and independent browser isolation. [Release record](evidence/phase3_release.json) and [desktop](evidence/phase3_live_desktop.png)/[mobile](evidence/phase3_live_desktop_mobile.png) captures identify exact checks and limitations. Five analysis reservations were used; no automatic POST retry.
- **Observability:** no error-level entries matched these deployment filters in the observed provider windows; no drains are configured. Existing provider logs and bounded request metrics are retained. No full-load, new cold/memory/bundle or disaster-recovery claim is made.

Reproduce a new measurement from frontend/ with `node scripts/verify-live.mjs --output ../context/evidence/a-new-live-run.json --screenshot ../context/evidence/a-new-live-run.png`. It makes five real analysis reservations, writes synthetic evidence locally and never changes canonical seed history. The script uses fresh browser contexts, so it does not delete user browser data. Existing evidence should be kept when recording another run.

The frontend's generated protocol files live inside its deployment root; runtime canonical bytes come from the database, so the backend does not depend on implicit root-level curriculum inclusion. Strict benchmark CI now verifies [Phase 3 regression sources](../evaluation/results/phase3-regression-v1/manifest.json); archived runs retain their original source hashes. Automatic push-to-production Git linkage is still not configured; source push alone does not deploy. Future compatible releases must be validated/published under a new immutable row when content changes, activate API support before clients and retain a deliberately supported rollback target. Full rollback, pause/resume, outage/quota and restore drills remain Phase 5.
