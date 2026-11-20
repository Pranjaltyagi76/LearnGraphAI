"""Owner-only immutable analysis publication; preserves legacy rows and prints no secrets."""

import argparse
import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb

from app.published import payload_hash, publication_input, unpack

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "publish", "verify"))
    parser.add_argument("--evaluation", type=Path)
    args = parser.parse_args()
    payload = publication_input(ROOT, args.evaluation)
    digest = payload_hash(payload)
    release_id = payload["manifest"]["identity"]["release_id"]
    if args.action != "check":
        load_dotenv(ROOT / "backend/.env.local")
        url = os.getenv("MIGRATION_DATABASE_URL")
        if not url:
            raise SystemExit("Owner connection is missing; no operation performed.")
        try:
            with psycopg.connect(url, connect_timeout=5, prepare_threshold=None) as conn:
                if args.action == "publish":
                    conn.execute(
                        "INSERT INTO learngraph.releases(id,content_hash,payload) "
                        "VALUES (%s,%s,%s) ON CONFLICT (id) DO NOTHING",
                        (release_id, digest, Jsonb(payload)),
                    )
                row = conn.execute(
                    "SELECT content_hash,payload FROM learngraph.releases WHERE id=%s",
                    (release_id,),
                ).fetchone()
                if not row or row[0] != digest or row[1] != payload:
                    raise SystemExit("Publication differs or is missing; never overwrite it.")
                unpack(row[1], row[0])
        except psycopg.Error:
            raise SystemExit("Publication unavailable; check access privately.") from None
    print(
        json.dumps(
            {
                "action": args.action,
                "release_id": release_id,
                "release_hash": payload["manifest"]["release_hash"],
                "package_hash": digest,
                "package_bytes": len(json.dumps(payload).encode()),
                "verified": True,
            }
        )
    )


if __name__ == "__main__":
    main()
