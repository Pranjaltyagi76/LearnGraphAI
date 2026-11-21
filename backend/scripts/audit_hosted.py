"""Owner-scoped hosted release audit; only uniquely named temporary quota fixtures mutate."""

import argparse
import json
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import psycopg
from dotenv import load_dotenv

from app.published import payload_hash, publication_input, unpack
from scripts.freeze_full_audit import ROOT
from scripts.verify_runtime import inspect_runtime


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    load_dotenv(ROOT / "backend/.env.local")
    owner, runtime = os.environ["MIGRATION_DATABASE_URL"], os.environ["DATABASE_URL"]
    legacy = json.loads((ROOT / "backend/data/phase1.json").read_bytes())
    expected = {
        "phase1-v1": legacy,
        "learngraph-review-v1": publication_input(
            ROOT, ROOT / "evaluation/results/phase3-regression-v1/test.json"
        ),
        "learngraph-full-v1": publication_input(ROOT, release_id="learngraph-full-v1"),
    }
    prefix, global_prefix = "p5" + uuid4().hex, "p5" + uuid4().hex

    def reserve(namespace, client="a" * 64):
        with psycopg.connect(
            runtime, connect_timeout=5, prepare_threshold=None, sslmode="require"
        ) as c:
            return c.execute(
                "SELECT * FROM learngraph.reserve_budget(%s,%s)", (namespace, client)
            ).fetchone()

    try:
        with psycopg.connect(
            runtime, connect_timeout=5, prepare_threshold=None, sslmode="require"
        ) as c:
            checks = inspect_runtime(c, legacy)
            checks["tls"] = bool(c.pgconn.ssl_in_use)
            rows = c.execute(
                "SELECT id,content_hash,payload FROM learngraph.releases ORDER BY id"
            ).fetchall()
            for name, digest, payload in rows:
                checks[name + "_source_hash"] = (
                    digest == payload_hash(payload) == payload_hash(expected[name])
                )
                if name != "phase1-v1":
                    unpack(payload, digest)
            identities = [{"id": n, "hash": d} for n, d, _ in rows]
            size = c.execute("SELECT pg_database_size(current_database())").fetchone()[0]
        with psycopg.connect(owner, connect_timeout=5, prepare_threshold=None) as c:
            # Avoid straddling a minute; the guard's authoritative clock is the SQL server.
            remaining = c.execute("SELECT 60-extract(second FROM clock_timestamp())").fetchone()[0]
        if remaining < 20:
            time.sleep(float(remaining) + 1)
        try:
            with ThreadPoolExecutor(max_workers=4) as pool:
                answers = list(pool.map(lambda _: reserve(prefix), range(20)))
            with psycopg.connect(owner, connect_timeout=5, prepare_threshold=None) as c:
                counts = [
                    r[0]
                    for r in c.execute(
                        "SELECT requests FROM learngraph.quota_buckets WHERE key LIKE %s",
                        (prefix + ":%",),
                    ).fetchall()
                ]
                checks["concurrent_admission_exactly_ten"] = sum(a[0] for a in answers) == 10
                checks["both_counters_equal_ten"] = sorted(counts) == [10, 10]
                c.execute(
                    (
                        "INSERT INTO learngraph.quota_buckets(key,requests,expires_at) VA"
                        "LUES (%s || ':day:' || extract(epoch FROM date_trunc('day',now()"
                        ",'UTC'))::bigint,1000,now()+interval '2 days')"
                    ),
                    (global_prefix,),
                )
            checks["global_denial"] = reserve(global_prefix, "b" * 64)[0] is False
            with psycopg.connect(owner, connect_timeout=5, prepare_threshold=None) as c:
                rows = c.execute(
                    "SELECT requests FROM learngraph.quota_buckets WHERE key LIKE %s",
                    (global_prefix + ":%",),
                ).fetchall()
                checks["global_denial_no_partial_increment"] = rows == [(1000,)]
                public = c.execute(
                    "SELECT has_schema_privilege('anon','learngraph','USAGE'), has_sc"
                    "hema_privilege('authenticated','learngraph','USAGE')"
                ).fetchone()
                checks["public_roles_excluded"] = not any(public)
        finally:
            with psycopg.connect(owner, connect_timeout=5, prepare_threshold=None) as c:
                c.execute(
                    "DELETE FROM learngraph.quota_buckets WHERE key LIKE %s OR key LIKE %s",
                    (prefix + ":%", global_prefix + ":%"),
                )
        assert all(checks.values()), checks
    except psycopg.Error:
        raise SystemExit(
            "Hosted audit failed; private provider details were not printed."
        ) from None
    # Match private values against tracked source and served static build files.
    # Never print the values or place them in a report.
    from psycopg.conninfo import conninfo_to_dict

    secrets = [
        os.environ.get("CLIENT_ID_HASH_SECRET", ""),
        owner,
        runtime,
        conninfo_to_dict(owner).get("password", ""),
        conninfo_to_dict(runtime).get("password", ""),
    ]
    secrets = [s.encode() for s in secrets if len(s) >= 16]
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    paths = [ROOT / p for p in tracked if p] + list((ROOT / "frontend/.next/static").rglob("*.js"))
    matches = [str(p.relative_to(ROOT)) for p in paths if any(s in p.read_bytes() for s in secrets)]
    assert not matches, "Secret value found in tracked/build content (values withheld)"
    report = {
        "observed_at": datetime.now(UTC).isoformat(),
        "checks": checks,
        "releases": identities,
        "database_bytes": size,
        "quota_workers": 4,
        "quota_attempts": 20,
        "admitted": 10,
        "temporary_buckets_removed": True,
        "secret_scan_files": len(paths),
        "secret_matches": [],
        "limitation": (
            "Canonical-source recovery only; no visitor data exists server-si"
            "de. Provider egress allowance not inferred from database size."
        ),
    }
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"passed": True, "database_bytes": size, "checks": len(checks)}))


if __name__ == "__main__":
    main()
