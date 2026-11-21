"""Full-track workflow fixtures are engineering checks, separate from quality-audit labels."""

import asyncio
import copy
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.analysis import analyze
from app.config import Settings
from app.contracts import AnalyzeRequest
from app.database import Database
from app.main import create_app
from app.published import payload_hash, publication_input, unpack
from app.release import load_release
from scripts.check_full_curriculum import FULL_ID, ROOT
from tests.test_analysis_api import AnalysisDatabase


class FullDatabase(AnalysisDatabase):
    def __init__(self):
        super().__init__(evaluation=False)
        self.retained = self.package
        payload = publication_input(ROOT, release_id=FULL_ID)
        self.package = unpack(payload, payload_hash(payload))

    async def analysis_release(self, release_id=None):
        await self.ready()
        return self.retained if release_id == "learngraph-review-v1" else self.package


def full_settings():
    return Settings(
        database_url="postgresql://fixture",
        hash_secret="test-only-fixture" * 3,
        analysis_release_id=FULL_ID,
        retained_analysis_release_ids=("learngraph-review-v1",),
    )


@pytest.mark.parametrize("target", load_release(ROOT, FULL_ID).graph.order)
def test_every_concept_can_complete_two_fresh_practices_and_distinct_reassessment(target):
    release = copy.deepcopy(load_release(ROOT, FULL_ID))
    # Explicit ready evidence for every other concept isolates target workflow feasibility.
    # This fixture makes no diagnostic-quality or realistic student claim.
    events = []
    run = str(uuid4())
    for concept in release.graph.order:
        for suffix in ("diagnostic_01", "practice_01", "practice_02"):
            activity = release.activities[f"{concept}_{suffix}"]
            option = (
                activity["correct_option"]
                if concept != target
                else next(
                    o["id"] for o in activity["options"] if o["id"] != activity["correct_option"]
                )
            )
            sequence = len(events) + 1
            events.append(
                {
                    "schema_version": 1,
                    "kind": "response",
                    "event_id": str(uuid4()),
                    "sequence_number": sequence,
                    "activity_id": activity["id"],
                    "activity_version": activity["version"],
                    "assessment_run_id": run,
                    "occurred_at": f"2026-11-20T08:{sequence:02}:00.000Z",
                    "response": {"option_id": option},
                    "hints_used": 0,
                    "time_spent_seconds": None,
                }
            )
    profile_id = "demo_base_cases"
    profile = release.profiles[profile_id]
    # Revalidate the fixture through the same strict model, with canonical seed sequences.
    release.profiles[profile_id] = type(profile).model_validate(
        {**profile.model_dump(), "events": events}
    )
    visitor = []
    roles, activity_ids = [], []
    for step in range(4):
        request = AnalyzeRequest(
            contract_version=1,
            versions=release.versions(profile_id),
            profile_id=profile_id,
            sandbox_id=str(uuid4()),
            local_revision=step,
            focus_concept_id=target,
            events=visitor,
        )
        bundle = analyze(release, request, received_at=datetime(2026, 11, 21, 12, tzinfo=UTC))
        estimate = next(e for e in bundle.estimates if e.concept_id == target)
        assert estimate.eligible_count == 3 + step
        assert estimate.successes == step
        if step == 3:
            assert estimate.estimate == 0.5
            assert estimate.performance_state == "developing"
            assert bundle.plan.status == "catalog_exhausted"
            break
        item = next(i for i in bundle.plan.items if i.readiness == "ready" and i.role != "lesson")
        assert item.concept_id == target
        activity = release.activities[item.activity_id]
        roles.append(item.role)
        activity_ids.append(item.activity_id)
        visitor.append(
            {
                "schema_version": 1,
                "kind": "response",
                "event_id": str(uuid4()),
                "sequence_number": step + 1,
                "activity_id": activity["id"],
                "activity_version": activity["version"],
                "assessment_run_id": run,
                "occurred_at": f"2026-11-21T10:00:0{step}.000Z",
                "response": {"option_id": activity["correct_option"]},
                "hints_used": 0,
                "time_spent_seconds": None,
            }
        )
    assert roles == ["practice", "practice", "reassessment"]
    assert len(set(activity_ids)) == 3


def test_active_full_and_retained_slice_are_separate_safe_http_projections():
    db = FullDatabase()
    with TestClient(create_app(full_settings(), db)) as api:
        assert api.get("/health").json()["stage"] == "phase4"
        assert api.get("/api/v1/demo/release").json()["release_id"] == FULL_ID
        for release_id, count in ((FULL_ID, 84), ("learngraph-review-v1", 14)):
            profiles = api.get(f"/api/v1/releases/{release_id}/profiles").json()["profiles"]
            assert len(profiles) == 4
            for profile in profiles:
                seed = api.get(
                    f"/api/v1/releases/{release_id}/profiles/{profile['id']}/seed"
                ).json()
                assert len(seed["activities"]) == count
                assert seed["versions"]["release_id"] == release_id
                assert "correct_option" not in str(seed) and "explanation" not in str(seed)
                result = api.post(
                    "/api/v1/demo/analyze",
                    json={
                        "contract_version": 1,
                        "versions": seed["versions"],
                        "profile_id": profile["id"],
                        "sandbox_id": str(uuid4()),
                        "local_revision": 0,
                        "focus_concept_id": profile["focus_concept_id"],
                        "events": [],
                    },
                )
                assert result.status_code == 200
                assert result.json()["versions"]["release_id"] == release_id
        assert api.get("/api/v1/releases/unconfigured/profiles").status_code == 409


def test_real_adapter_cache_is_keyed_and_bounded_by_supported_releases():
    db = Database(full_settings())
    fetched = []

    async def fetch(release_id):
        fetched.append(release_id)
        payload = publication_input(ROOT, release_id=release_id)
        return {"payload": payload, "content_hash": payload_hash(payload)}

    db.fetch_release = fetch

    async def exercise():
        first = await db.analysis_release()
        old = await db.analysis_release("learngraph-review-v1")
        assert await db.analysis_release() is first
        assert await db.analysis_release("learngraph-review-v1") is old
        assert first.summary().release_id != old.summary().release_id
        with pytest.raises(ConnectionError):
            await db.analysis_release("unconfigured")

    asyncio.run(exercise())
    assert fetched == [FULL_ID, "learngraph-review-v1"]


def test_full_artifact_identity_cannot_relabel_or_follow_external_paths():
    payload = publication_input(ROOT, release_id=FULL_ID)
    payload["manifest"]["identity"]["release_id"] = "../external"
    import hashlib

    from app.contracts import canonical_json

    payload["manifest"]["release_hash"] = hashlib.sha256(
        canonical_json(payload["manifest"]["identity"])
    ).hexdigest()
    with pytest.raises(ValueError, match="Unsupported release identity"):
        unpack(payload, payload_hash(payload))
