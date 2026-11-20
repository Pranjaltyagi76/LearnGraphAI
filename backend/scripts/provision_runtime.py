"""Provision a fresh runtime login using a privately configured owner connection.

Run once after migrate/seed. Existing roles are never reset or adopted.
Secrets are written only to the ignored backend/.env.local file.
"""

import os
import secrets
from pathlib import Path

import psycopg
from dotenv import load_dotenv, set_key
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env.local"
ROLE = "learngraph_api"


def main() -> None:
    load_dotenv(ENV_PATH)
    owner_url = os.getenv("MIGRATION_DATABASE_URL")
    if not owner_url:
        raise SystemExit("MIGRATION_DATABASE_URL is missing; no operation performed.")
    try:
        owner = conninfo_to_dict(owner_url)
    except psycopg.Error:
        raise SystemExit("Owner connection format is invalid; inspect it privately.") from None
    user = owner.get("user", "")
    host = owner.get("host", "")
    if not user.startswith("postgres.") or not host.endswith(".pooler.supabase.com"):
        raise SystemExit("Use the selected Supabase shared session-pooler owner connection.")
    if owner.get("port") != "5432":
        raise SystemExit("Owner connection must use shared session-pooler port 5432.")
    if os.getenv("DATABASE_URL"):
        raise SystemExit("DATABASE_URL already exists; refusing to replace runtime credentials.")
    runtime_password = secrets.token_urlsafe(48)
    runtime_url = make_conninfo(
        host=host,
        port="6543",
        dbname=owner.get("dbname", "postgres"),
        user=ROLE + "." + user.split(".", 1)[1],
        password=runtime_password,
        sslmode="require",
    )
    try:
        with psycopg.connect(
            owner_url, connect_timeout=5, prepare_threshold=None, sslmode="require"
        ) as conn:
            conn.execute("SET LOCAL statement_timeout = '5000ms'")
            if conn.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (ROLE,)).fetchone():
                raise SystemExit("Runtime role already exists; credentials were not changed.")
            conn.execute(
                sql.SQL(
                    "CREATE ROLE {} LOGIN INHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE "
                    "NOREPLICATION NOBYPASSRLS CONNECTION LIMIT 10 PASSWORD {}"
                ).format(sql.Identifier(ROLE), sql.Literal(runtime_password))
            )
            conn.execute(sql.SQL("GRANT learngraph_runtime TO {}").format(sql.Identifier(ROLE)))
            # Save before commit: a file-write failure rolls the new role back.
            set_key(ENV_PATH, "DATABASE_URL", runtime_url)
            if len(os.getenv("CLIENT_ID_HASH_SECRET", "")) < 32:
                set_key(ENV_PATH, "CLIENT_ID_HASH_SECRET", secrets.token_urlsafe(48))
        print("Runtime login created; ignored local environment saved. Run verify_runtime.py next.")
    except psycopg.Error:
        raise SystemExit(
            "Provisioning failed; inspect owner connectivity/privileges privately."
        ) from None


if __name__ == "__main__":
    main()
