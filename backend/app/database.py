from contextlib import asynccontextmanager
from typing import Any

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.config import Settings


class Database:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.pool: AsyncConnectionPool | None = None

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
        async with self.connection() as conn:
            row = await (
                await conn.execute(
                    "SELECT payload, content_hash FROM learngraph.releases WHERE id = %s",
                    (self.settings.release_id,),
                )
            ).fetchone()
            if not row:
                raise ConnectionError("Published release unavailable")
            return row

    async def ready(self) -> None:
        await self.release()
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
