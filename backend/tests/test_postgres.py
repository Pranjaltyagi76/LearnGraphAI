"""Real SQL integration checks. Never point TEST_DATABASE_URL at a hosted project."""

import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from psycopg.types.json import Jsonb

from scripts.verify_runtime import content_hash, inspect_runtime

ROOT = Path(__file__).parents[1]
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def database():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL missing: real PostgreSQL integration not run")
    with psycopg.connect(url) as conn:
        if not conn.info.dbname.endswith("_test") or conn.info.host not in {
            "localhost",
            "127.0.0.1",
        }:
            pytest.fail("Integration requires a local database whose name ends in _test")
        conn.execute((ROOT / "migrations/001_bootstrap.sql").read_text(), prepare=False)
        payload = json.loads((ROOT / "data/phase1.json").read_text())
        conn.execute(
            "INSERT INTO learngraph.releases(id,content_hash,payload) VALUES (%s,%s,%s) "
            "ON CONFLICT DO NOTHING",
            ("phase1-test", "a" * 64, Jsonb(payload)),
        )
    return url


def reserve(url, namespace, client="a" * 64):
    with psycopg.connect(url) as conn:
        conn.execute("SET LOCAL ROLE learngraph_runtime")
        return conn.execute(
            "SELECT * FROM learngraph.reserve_budget(%s,%s)", (namespace, client)
        ).fetchone()


def test_atomic_client_quota_across_connections(database):
    namespace = str(uuid4())
    with ThreadPoolExecutor(max_workers=12) as workers:
        results = list(workers.map(lambda _: reserve(database, namespace), range(20)))
    assert sum(result[0] for result in results) == 10
    assert all(result[1] > 0 for result in results if not result[0])
    with psycopg.connect(database) as conn:
        rows = conn.execute(
            "SELECT requests FROM learngraph.quota_buckets WHERE key LIKE %s",
            (namespace + ":%",),
        ).fetchall()
        assert sorted(row[0] for row in rows) == [10, 10]


def test_global_budget_cannot_be_bypassed_with_new_client(database):
    namespace = str(uuid4())
    with psycopg.connect(database) as conn:
        conn.execute(
            "INSERT INTO learngraph.quota_buckets(key,requests,expires_at) "
            "VALUES (%s || ':day:' || extract(epoch FROM date_trunc('day',now(),'UTC'))::bigint, "
            "1000, now()+interval '2 days')",
            (namespace,),
        )
    assert reserve(database, namespace, "b" * 64)[0] is False


def test_runtime_has_only_intended_data_access(database):
    with psycopg.connect(database) as conn:
        conn.execute("SET LOCAL ROLE learngraph_runtime")
        assert conn.execute("SELECT id FROM learngraph.releases LIMIT 1").fetchone()
    with pytest.raises(psycopg.errors.InsufficientPrivilege), psycopg.connect(database) as conn:
        conn.execute("SET LOCAL ROLE learngraph_runtime")
        conn.execute("DELETE FROM learngraph.quota_buckets")
    with pytest.raises(psycopg.errors.InsufficientPrivilege), psycopg.connect(database) as conn:
        conn.execute("SET LOCAL ROLE learngraph_runtime")
        conn.execute("UPDATE learngraph.releases SET content_hash = %s", ("b" * 64,))


def test_published_content_is_immutable_even_for_seed_owner(database):
    with pytest.raises(psycopg.errors.RaiseException), psycopg.connect(database) as conn:
        conn.execute(
            "UPDATE learngraph.releases SET content_hash = %s WHERE id = %s",
            ("b" * 64, "phase1-test"),
        )


def test_runtime_audit_rejects_owner_and_detects_content_mismatch(database):
    payload = json.loads((ROOT / "data/phase1.json").read_text())
    payload["release_id"] = "audit-" + str(uuid4())
    with psycopg.connect(database) as conn:
        conn.execute(
            "INSERT INTO learngraph.releases(id,content_hash,payload) VALUES (%s,%s,%s)",
            (payload["release_id"], content_hash(payload), Jsonb(payload)),
        )
        owner = inspect_runtime(conn, payload)
        assert not owner["unprivileged_role"]
        assert not owner["runtime_grants"]
        assert not owner["separate_owner_and_hardened_guard"]
        conn.execute("SET LOCAL ROLE learngraph_runtime")
        assert all(inspect_runtime(conn, payload).values())
        changed = {**payload, "profiles": []}
        assert not inspect_runtime(conn, changed)["source_matches_published_release"]


def test_analysis_package_round_trips_exact_bytes_through_restricted_sql(database):
    from app.published import payload_hash, publication_input, unpack

    payload = publication_input(ROOT.parent)
    digest = payload_hash(payload)
    release_id = payload["manifest"]["identity"]["release_id"]
    with psycopg.connect(database) as conn:
        conn.execute(
            "INSERT INTO learngraph.releases(id,content_hash,payload) VALUES (%s,%s,%s) "
            "ON CONFLICT DO NOTHING",
            (release_id, digest, Jsonb(payload)),
        )
        conn.execute("SET LOCAL ROLE learngraph_runtime")
        row = conn.execute(
            "SELECT content_hash,payload FROM learngraph.releases WHERE id=%s", (release_id,)
        ).fetchone()
        assert row[0] == digest and row[1] == payload
        package = unpack(row[1], row[0])
        assert len(package.profiles().profiles) == 4
        assert len(package.seed("demo_base_cases").activities) == 14
