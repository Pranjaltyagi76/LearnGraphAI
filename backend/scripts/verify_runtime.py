"""Read-only audit of the runtime connection; never print credentials or database errors."""

import hashlib
import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def content_hash(payload: dict) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def inspect_runtime(conn, expected: dict) -> dict[str, bool]:
    """Use effective SQL privileges, rather than trusting a role's name."""
    role = conn.execute(
        "SELECT NOT (rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls) "
        "FROM pg_roles WHERE rolname = current_user"
    ).fetchone()
    access = conn.execute(
        "SELECT pg_has_role(current_user, 'learngraph_runtime', 'MEMBER'), "
        "has_schema_privilege(current_user, 'learngraph', 'USAGE'), "
        "NOT has_schema_privilege(current_user, 'learngraph', 'CREATE'), "
        "has_table_privilege(current_user, 'learngraph.releases', 'SELECT'), "
        "NOT has_table_privilege(current_user, 'learngraph.releases', "
        "'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER'), "
        "NOT has_table_privilege(current_user, 'learngraph.quota_buckets', "
        "'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER'), "
        "has_function_privilege(current_user, 'learngraph.reserve_budget(text,text)', 'EXECUTE')"
    ).fetchone()
    boundary = conn.execute(
        "SELECT NOT pg_has_role(current_user, n.nspowner, 'MEMBER') "
        "AND NOT pg_has_role(current_user, c.relowner, 'MEMBER') "
        "AND NOT pg_has_role(current_user, p.proowner, 'MEMBER'), "
        "c.relrowsecurity, p.prosecdef, p.proconfig = ARRAY['search_path=pg_catalog'] "
        "FROM pg_namespace n JOIN pg_class c ON c.relnamespace = n.oid "
        "JOIN pg_proc p ON p.oid = 'learngraph.reserve_budget(text,text)'::regprocedure "
        "WHERE n.nspname = 'learngraph' AND c.relname = 'releases'"
    ).fetchone()
    row = conn.execute(
        "SELECT content_hash, payload FROM learngraph.releases WHERE id = %s",
        (expected["release_id"],),
    ).fetchone()
    return {
        "unprivileged_role": bool(role and role[0]),
        "runtime_grants": bool(access and all(access)),
        "separate_owner_and_hardened_guard": bool(boundary and all(boundary)),
        "source_matches_published_release": bool(
            row and row[0] == content_hash(expected) == content_hash(row[1])
        ),
    }


def main() -> None:
    load_dotenv(ROOT / ".env.local")
    url = os.getenv("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is missing; no operation performed.")
    expected = json.loads((ROOT / "data/phase1.json").read_text(encoding="utf-8"))
    try:
        with psycopg.connect(
            url, connect_timeout=5, prepare_threshold=None, sslmode="require"
        ) as conn:
            conn.execute("SET TRANSACTION READ ONLY")
            conn.execute("SET LOCAL statement_timeout = '2500ms'")
            checks = inspect_runtime(conn, expected)
            checks["tls"] = bool(conn.pgconn.ssl_in_use)
    except psycopg.Error:
        raise SystemExit(
            "Runtime verification failed; inspect connection/privileges privately."
        ) from None
    print(json.dumps(checks, sort_keys=True))
    if not all(checks.values()):
        raise SystemExit("Runtime verification failed; do not deploy this connection.")


if __name__ == "__main__":
    main()
