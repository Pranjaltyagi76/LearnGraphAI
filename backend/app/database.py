from contextlib import asynccontextmanager
from typing import Any

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.config import Settings
from app.published import PublishedRelease, payload_hash, unpack


class Database:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.pool: AsyncConnectionPool | None = None
        self.analysis_cache: dict[str, PublishedRelease] = {}

    async def open(self) -> None:
        if self.settings.database_url:
            self.pool = AsyncConnectionPool(
                self.settings.database_url,
                min_size=0,
                max_size=1,
                open=False,
                timeout=3,
                max_idle=60,
                kwargs={
                    "prepare_threshold": None,
                    "connect_timeout": 3,
                    "row_factory": dict_row,
                    "sslmode": "require" if self.settings.environment == "production" else "prefer",
                },
            )
            await self.pool.open()

    async def close(self) -> None:
        if self.pool:
            await self.pool.close(timeout=0.4)

    @asynccontextmanager
    async def connection(self):
        if not self.pool:
            raise ConnectionError("Database unavailable")
        async with self.pool.connection(timeout=3) as conn:
            await conn.execute("SET LOCAL statement_timeout = '2500ms'")
            yield conn

    async def release(self) -> dict[str, Any]:
        return await self.fetch_release(self.settings.release_id)

    async def fetch_release(self, release_id: str) -> dict[str, Any]:
        async with self.connection() as conn:
            row = await (
                await conn.execute(
                    "SELECT payload, content_hash FROM learngraph.releases WHERE id = %s",
                    (release_id,),
                )
            ).fetchone()
            if not row:
                raise ConnectionError("Published release unavailable")
            if payload_hash(row["payload"]) != row["content_hash"]:
                raise ConnectionError("Published release integrity failure")
            return row

    async def analysis_release(self, release_id: str | None = None) -> PublishedRelease:
        release_id = release_id or self.settings.analysis_release_id
        allowed = (self.settings.analysis_release_id, *self.settings.retained_analysis_release_ids)
        if release_id not in allowed or len(set(allowed)) > 2:
            raise ConnectionError("Unsupported analysis release configuration")
        if release_id not in self.analysis_cache:
            row = await self.fetch_release(release_id)
            published = unpack(row["payload"], row["content_hash"])
            if published.summary().release_id != release_id:
                raise ConnectionError("Analysis publication identity failure")
            self.analysis_cache[release_id] = published
        return self.analysis_cache[release_id]

    async def ready(self) -> None:
        await self.release()
        if self.settings.analysis_release_id:
            await self.analysis_release()
            for release_id in self.settings.retained_analysis_release_ids:
                await self.analysis_release(release_id)
        async with self.connection() as conn:
            row = await (
                await conn.execute(
                    "SELECT has_function_privilege(current_user, "
                    "'learngraph.reserve_budget(text,text)', 'EXECUTE') AS allowed"
                )
            ).fetchone()
            if not row or not row["allowed"]:
                raise ConnectionError("Quota guard unavailable")

    async def reserve(self, client_hash: str) -> tuple[bool, int]:
        async with self.connection() as conn:
            row = await (
                await conn.execute(
                    "SELECT * FROM learngraph.reserve_budget(%s, %s)",
                    (self.settings.quota_namespace, client_hash),
                )
            ).fetchone()
            if not row:
                raise ConnectionError("Quota guard unavailable")
            return row["allowed"], row["retry_after"]
