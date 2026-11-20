"""Real SQL integration checks. Never point TEST_DATABASE_URL at a hosted project."""

import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from psycopg.types.json import Jsonb

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
