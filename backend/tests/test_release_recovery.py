"""Actual isolated PostgreSQL restore and quota-storage-loss drills, never hosted DDL."""

import asyncio
import json
import os
from contextlib import asynccontextmanager
from uuid import uuid4

import httpx
import psycopg
import pytest
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from psycopg.types.json import Jsonb

from app.database import Database
from app.main import create_app
from app.published import payload_hash, publication_input, unpack
from scripts.freeze_full_audit import ROOT
from scripts.verify_runtime import inspect_runtime
from tests.test_full_curriculum import full_settings


@pytest.fixture
def isolated_database():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Isolated PostgreSQL required")
    info = conninfo_to_dict(url)
    assert info["host"] in {"127.0.0.1", "localhost"} and info["dbname"].endswith("_test")
    name = "phase5_" + uuid4().hex + "_test"
    with psycopg.connect(url, autocommit=True) as admin:
        admin.execute(sql.SQL("CREATE DATABASE {} TEMPLATE template0").format(sql.Identifier(name)))
    new_url = make_conninfo(url, dbname=name)
    try:
        with psycopg.connect(new_url) as conn:
            conn.execute((ROOT / "backend/migrations/001_bootstrap.sql").read_text(), prepare=False)
        yield new_url
    finally:
        with psycopg.connect(url, autocommit=True) as admin:
            admin.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name)))


@pytest.mark.integration
def test_clean_database_restore_reseeds_exact_packages_and_runtime_grants(isolated_database):
    legacy = json.loads((ROOT / "backend/data/phase1.json").read_bytes())
    packages = {
        "phase1-v1": legacy,
        "learngraph-review-v1": publication_input(
            ROOT, ROOT / "evaluation/results/phase3-regression-v1/test.json"
        ),
        "learngraph-full-v1": publication_input(ROOT, release_id="learngraph-full-v1"),
    }
    with psycopg.connect(isolated_database) as conn:
        for _ in range(2):
            for name, payload in packages.items():
                conn.execute(
                    "INSERT INTO learngraph.releases(id,content_hash,payload) "
                    "VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
                    (name, payload_hash(payload), Jsonb(payload)),
                )
        rows = conn.execute("SELECT id,content_hash,payload FROM learngraph.releases").fetchall()
        assert len(rows) == 3
        for name, digest, payload in rows:
            assert payload == packages[name] and digest == payload_hash(packages[name])
            if name != "phase1-v1":
                unpack(payload, digest)
        conn.execute("SET LOCAL ROLE learngraph_runtime")
        assert all(inspect_runtime(conn, legacy).values())


@pytest.mark.integration
def test_real_missing_quota_table_fails_closed_then_recovers(isolated_database):
    async def exercise():
        async with await psycopg.AsyncConnection.connect(isolated_database) as conn:
            await conn.execute("ALTER TABLE learngraph.quota_buckets RENAME TO quota_hidden")
            await conn.execute("SET LOCAL ROLE learngraph_runtime")
            db = Database(full_settings())

            @asynccontextmanager
            async def connection():
                yield conn

            db.connection = connection
            payload = publication_input(ROOT, release_id="learngraph-full-v1")
            package = unpack(payload, payload_hash(payload))
            request = {
                "contract_version": 1,
                "versions": package.release.versions("demo_base_cases").model_dump(mode="json"),
                "profile_id": "demo_base_cases",
                "sandbox_id": str(uuid4()),
                "local_revision": 0,
                "focus_concept_id": "base_cases",
                "events": [],
            }
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=create_app(full_settings(), db)),
                base_url="http://test",
            ) as api:
                response = await api.post("/api/v1/demo/analyze", json=request)
                assert response.status_code == 503
                assert response.json()["code"] == "dependency_unavailable"
                assert "quota_hidden" not in response.text and "does not exist" not in response.text
            await conn.rollback()  # restores the exact table name, privileges and transaction state
            await conn.execute("SET LOCAL ROLE learngraph_runtime")
            assert (await db.reserve("a" * 64))[0] is True

    asyncio.run(exercise())
