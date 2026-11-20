"""Owner-only, repeatable migration/seeding; never prints connection strings."""

import argparse
import hashlib
import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["migrate", "seed", "verify"])
    args = parser.parse_args()
    load_dotenv(ROOT / ".env.local")
    url = os.getenv("MIGRATION_DATABASE_URL")
    if not url:
        raise SystemExit("MIGRATION_DATABASE_URL is missing; no operation performed.")
    try:
        with psycopg.connect(url, connect_timeout=5, prepare_threshold=None) as conn:
            if args.action == "migrate":
                conn.execute((ROOT / "migrations/001_bootstrap.sql").read_text(), prepare=False)
            else:
                payload = json.loads((ROOT / "data/phase1.json").read_text())
                digest = hashlib.sha256(
                    json.dumps(
                        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
                    ).encode()
                ).hexdigest()
                if args.action == "seed":
                    conn.execute(
                        "INSERT INTO learngraph.releases(id, content_hash, payload) "
                        "VALUES (%s,%s,%s) "
                        "ON CONFLICT (id) DO NOTHING",
                        (payload["release_id"], digest, Jsonb(payload)),
                    )
                row = conn.execute(
                    "SELECT content_hash FROM learngraph.releases WHERE id = %s",
                    (payload["release_id"],),
                ).fetchone()
                if not row or row[0] != digest:
                    raise SystemExit(
                        "Release missing/hash mismatch; publish a new version, never overwrite."
                    )
        print(f"{args.action}: succeeded")
    except psycopg.Error:
        raise SystemExit(
            "Database operation failed; check connectivity/privileges privately."
        ) from None


if __name__ == "__main__":
    main()
