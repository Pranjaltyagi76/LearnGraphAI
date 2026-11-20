# Free deployment and recovery

**State:** Planned runbook, no resource provisioned or deployment executed. **Date:** 20 November 2026. **Requirements:** NFR-01–08/10/11/13 and FR-16/17/19 in [requirement.md](../requirement.md).

This runbook is for Phase 1 feasibility and Phase 5 release. The user authorized documentation and Git delivery; writing this file is not authorization/evidence that hosting setup has already occurred. Commands must be filled in only after real scaffolds, versions, and selected project IDs exist.

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
| Frontend | Vercel Hobby project, root `frontend/` | Not provisioned; no deployment URL. |
| API | Separate Vercel Hobby project, root `backend/` | Not provisioned; no deployment URL. |
| Database | Supabase Free | Not provisioned; no project/region chosen. |
| Alternative API | Render Free only if required by measured failure | Not provisioned. |
| CI | Public GitHub repository, standard runners | No workflow exists yet. |

Confirm the actual provider account/team, repository, project roots, environment, and release commit before mutation. Do not accidentally deploy this project into an unrelated paid team.

## 3. Provider checks

The values below come from the 20 November 2026 planning snapshot recorded in PROJECT Section 14. They have not been revalidated against a provisioned account. Recheck official docs/account allowance at provisioning and release; record date, observed limits, and eligibility.

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

No exact `npm`, migration, or deploy command is claimed as runnable yet. Fill in commands after the corresponding package/scripts exist and have been checked.

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
| Commit/environment/project IDs | Not deployed; populate after setup. |
| Verified provider terms date/account limits | Planning snapshot only; live-account verification pending. |
| Frontend/API URLs and region | Not provisioned. |
| Runtime/package versions and bundle | Not selected/measured. |
| Migration/manifest versions | Not implemented. |
| Browser/API/database checks | Not run. |
| Restore/rollback exercise | Not run. |
| Cost/settings check | Not run against provisioned resources. |

Add concrete evidence and failed results here when available. Never paste credentials or claim successful deployment from a planned runbook.
