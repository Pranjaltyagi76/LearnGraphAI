"""Loopback-only browser test fixture. Not an entrypoint or substitute for hosted SQL."""

from app.main import create_app
from tests.test_full_curriculum import FullDatabase, full_settings

app = create_app(
    full_settings(),
    FullDatabase(),
)
