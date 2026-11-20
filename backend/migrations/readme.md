# Phase 1 database setup

Run only against the explicitly selected free project, after account/plan and environment verification. The roadmap records the actual migration and live verification status.

The owner connection must have schema/role/function creation privileges. `001_bootstrap.sql` creates a private `learngraph` schema, immutable versioned release payloads, a NOLOGIN runtime group, and a SECURITY DEFINER quota reservation restricted to that group. Public/anon browser access to this private schema is not required.

Create a separate database login privately and grant it `learngraph_runtime`; use that login in `DATABASE_URL`. Do not set the runtime URL to the migration-owner/postgres credentials. The runtime group can read canonical data and execute the quota function, but cannot mutate published releases or directly alter quota counters. Authored answer rules are public source; ordinary public responses still hide future answers.

Verified command entrypoints, from `backend/` after installing locked dependencies:

```powershell
uv run python scripts/manage_db.py migrate
uv run python scripts/manage_db.py seed
uv run python scripts/manage_db.py verify
uv run python scripts/provision_runtime.py
uv run python scripts/verify_runtime.py
```

Set `MIGRATION_DATABASE_URL` privately in `backend/.env.local`; do not paste values into Git or public logs. Use the provider-supported session-compatible route for migrations and shared transaction pooler for runtime, with TLS and prepared statements disabled in the client. Runtime and migration secrets have different owners/purposes.

The one-time provisioning helper requires the selected shared session-pooler owner connection on port 5432. It creates a fresh `learngraph_api` login with a ten-connection role limit, grants only the runtime group, and saves the transaction-pooler connection (port 6543) plus a random hash secret in the ignored local environment. It refuses an existing role or runtime URL instead of resetting credentials. Run it only after migrate/seed; never deploy the owner URL. If provisioning fails, inspect the role and private environment before retrying, because a local file and a database commit cannot be updated atomically.

The read-only runtime audit requires TLS and checks effective grants, owner separation, hardened quota-function configuration, and both the stored and recomputed canonical content hash. A working `SELECT` alone does not pass this audit. It prints only boolean checks and exits unsuccessfully if any check fails. CI exercises the audit against the migration owner, a permitted runtime role, and mismatched content. TLS and hosted pooling still require the actual selected Supabase connection.

Seeding refuses changed content under an existing release ID. Publish a new ID and verify the compatible manifest instead of overwriting old content. The current `phase1-v1` payload contains 12 authored questions across two concepts, one synthetic profile, six canonical initial responses, and the proposed full graph; it is not the completed 72-item P0 catalog or the Phase 2 diagnosis engine.

The quota function serializes each tiny reservation per namespace, checks the 1,000/day global and ten/minute/client allowances together, and increments both only when admitted. It deletes at most 20 expired buckets per reservation. Expired buckets cannot be used for new requests; deletion is opportunistic and may require bounded owner cleanup after inactivity. Thus “48 hours” is the logical bucket expiry, not a guarantee of physical deletion during an idle period.

Real SQL tests require `TEST_DATABASE_URL` targeting local/CI PostgreSQL and a database name ending in `_test`; the suite refuses a hosted/non-test target. CI provides isolated PostgreSQL 17. Contract fixtures in API unit tests do not substitute for these SQL checks or live Supabase verification.
