"""Loopback-only browser test fixture. Not an entrypoint or substitute for hosted SQL."""

from app.config import Settings
from app.main import create_app
from tests.test_analysis_api import AnalysisDatabase

app = create_app(
    Settings(
        database_url="postgresql://fixture",
        hash_secret="test-only-fixture" * 3,
        analysis_release_id="learngraph-review-v1",
    ),
    AnalysisDatabase(),
)
