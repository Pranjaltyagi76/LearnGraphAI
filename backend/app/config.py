import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = ""
    hash_secret: str = ""
    environment: str = "development"
    origins: tuple[str, ...] = ("http://127.0.0.1:3000", "http://localhost:3000")
    release_id: str = "phase1-v1"
    quota_namespace: str = "development"
    on_vercel: bool = False

    @property
    def configured(self) -> bool:
        return bool(self.database_url) and len(self.hash_secret) >= 32

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            database_url=os.getenv("DATABASE_URL", ""),
            hash_secret=os.getenv("CLIENT_ID_HASH_SECRET", ""),
            environment=os.getenv("APP_ENV", "development"),
            origins=tuple(
                x.strip().rstrip("/")
                for x in os.getenv(
                    "ALLOWED_ORIGINS", "http://127.0.0.1:3000,http://localhost:3000"
                ).split(",")
                if x.strip() and x.strip() != "*"
            ),
            release_id=os.getenv("RELEASE_ID", "phase1-v1"),
            quota_namespace=os.getenv("QUOTA_NAMESPACE", "development"),
            on_vercel=os.getenv("VERCEL") == "1",
        )
