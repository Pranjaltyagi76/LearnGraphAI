"""HTTP admission/projection/replay tests; actual SQL remains separately verified."""

import copy
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.contracts import (
    AnalysisBundle,
    EvaluationSummary,
    ProfilesResponse,
    ReleaseSummary,
    SeedResponse,
)
from app.main import create_app
from app.published import payload_hash, publication_input, unpack
from tests.test_api import ContractDatabase

ROOT = Path(__file__).resolve().parents[2]


class AnalysisDatabase(ContractDatabase):
    def __init__(self, allowed=True, unavailable=False, evaluation=True):
        super().__init__(allowed, unavailable)
        summary = ROOT / "evaluation/results/phase2-v2/test.json" if evaluation else None
        self.payload = publication_input(ROOT, summary)
        self.package = unpack(self.payload, payload_hash(self.payload))
        self.reservations = 0

    async def analysis_release(self):
        await self.ready()
        return self.package

    async def reserve(self, client_hash):
        self.reservations += 1
        return await super().reserve(client_hash)


def client(database=None):
    return TestClient(
        create_app(
            Settings(
                database_url="postgresql://unused",
                hash_secret="x" * 32,
                analysis_release_id="learngraph-review-v1",
            ),
            database or AnalysisDatabase(),
        )
    )


def request(database):
    return {
        "contract_version": 1,
        "versions": database.package.release.versions("demo_base_cases").model_dump(mode="json"),
        "profile_id": "demo_base_cases",
        "sandbox_id": str(uuid4()),
        "local_revision": 0,
        "focus_concept_id": "base_cases",
        "trigger_event_id": None,
        "events": [],
    }


def response_event(database):
    activity = database.package.release.activities["base_cases_practice_03"]
    return {
        "schema_version": 1,
        "kind": "response",
        "event_id": str(uuid4()),
        "sequence_number": 1,
        "activity_id": activity["id"],
        "activity_version": activity["version"],
        "assessment_run_id": str(uuid4()),
        "occurred_at": datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "response": {"option_id": activity["correct_option"]},
        "hints_used": 0,
    }


def test_metadata_and_all_four_seeds_keep_future_feedback_private():
    db = AnalysisDatabase()
    with client(db) as api:
        summary = ReleaseSummary.model_validate(api.get("/api/v1/demo/release").json())
        profiles = ProfilesResponse.model_validate(
            api.get(f"/api/v1/releases/{summary.release_id}/profiles").json()
        )
        assert len(profiles.profiles) == 4
        for profile in profiles.profiles:
            raw = api.get(
                f"/api/v1/releases/{summary.release_id}/profiles/{profile.id}/seed"
            ).json()
            SeedResponse.model_validate(raw)
            assert raw["versions"] == profile.versions.model_dump(mode="json")
            assert len(raw["concepts"]) == 12 and len(raw["activities"]) == 14
            assert all(
                "correct_option" not in a and "explanation" not in a for a in raw["activities"]
            )
        assert api.get("/api/v1/releases/old/profiles").status_code == 409
        assert (
            api.get(f"/api/v1/releases/{summary.release_id}/profiles/missing/seed").status_code
            == 404
        )
        assert api.get("/api/v1/demo/profiles").json()["release_id"] == "phase1-v1"
        assert api.get("/ready").status_code == 200
        assert db.reservations == 0


def test_real_http_replay_returns_one_bundle_and_deduplicates_retry():
    db = AnalysisDatabase()
    raw = request(db)
    raw["events"] = [response_event(db)]
    with client(db) as api:
        response = api.post("/api/v1/demo/analyze", json=raw)
        assert response.status_code == 200, response.text
        first = AnalysisBundle.model_validate(response.json())
        raw["events"].append(copy.deepcopy(raw["events"][0]))
        retry = api.post("/api/v1/demo/analyze", json=raw)
        assert retry.json() == first.model_dump(mode="json")
        assert first.accepted_visitor_events == 1 and first.persisted is False
        assert response.headers["cache-control"] == "no-store"
        raw["events"][-1]["hints_used"] = 1
        conflict = api.post("/api/v1/demo/analyze", json=raw)
        assert conflict.status_code == 409 and conflict.json()["code"] == "event_conflict"
        assert conflict.headers["x-request-id"] == conflict.json()["request_id"]
        assert db.reservations == 3


def test_raw_schema_and_byte_bounds_precede_quota_semantic_failures_consume_it():
    db = AnalysisDatabase()
    with client(db) as api:
        raw = request(db)
        raw["is_correct"] = True
        assert api.post("/api/v1/demo/analyze", json=raw).status_code == 422
        raw = request(db)
        raw["events"] = [response_event(db)] * 201
        assert api.post("/api/v1/demo/analyze", json=raw).status_code == 422
        response = api.post(
            "/api/v1/demo/analyze",
            content=iter([b"x" * 131072, b"x" * 131073]),
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 413 and db.reservations == 0
        raw = request(db)
        raw["events"] = [response_event(db)]
        raw["events"][0]["activity_id"] = "missing"
        assert api.post("/api/v1/demo/analyze", json=raw).status_code == 422
        raw = request(db)
        raw["versions"]["release_hash"] = "0" * 64
        assert api.post("/api/v1/demo/analyze", json=raw).status_code == 409
        assert db.reservations == 2


@pytest.mark.parametrize(
    "allowed,unavailable,status,code",
    [(False, False, 429, "quota_exhausted"), (True, True, 503, "dependency_unavailable")],
)
def test_full_analysis_fails_closed_and_never_echoes_provider_errors(
    allowed, unavailable, status, code
):
    db = AnalysisDatabase(allowed=allowed, unavailable=unavailable)
    with client(db) as api:
        response = api.post("/api/v1/demo/analyze", json=request(db))
        assert response.status_code == status and response.json()["code"] == code
        assert "private database detail" not in response.text
        if status == 429:
            assert int(response.headers["retry-after"]) > 0


def test_evaluation_is_only_available_after_actual_summary_publication():
    with client() as api:
        EvaluationSummary.model_validate(api.get("/api/v1/analytics/evaluation").json())
    with client(AnalysisDatabase(evaluation=False)) as api:
        response = api.get("/api/v1/analytics/evaluation")
        assert response.status_code == 404 and response.json()["code"] == "evaluation_not_published"


def test_publication_checks_actual_payload_and_raw_artifact_bytes():
    db = AnalysisDatabase()
    payload = copy.deepcopy(db.payload)
    payload["artifacts"]["curriculum/catalog-slice.v1.json"] += "eA=="
    with pytest.raises(ValueError):
        unpack(payload, payload_hash(payload))
    with pytest.raises(ValueError):
        unpack(db.payload, "0" * 64)
    assert len(json.dumps(db.payload).encode()) < 262144
