import json
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

PAYLOAD = json.loads((Path(__file__).parents[1] / "data/phase1.json").read_text())


class ContractDatabase:
    """Only an API contract fixture; it does not verify PostgreSQL or deployment."""

    def __init__(self, allowed=True, unavailable=False):
        self.allowed, self.unavailable = allowed, unavailable

    async def open(self):
        pass

    async def close(self):
        pass

    async def ready(self):
        if self.unavailable:
            raise ConnectionError("private database detail")

    async def release(self):
        await self.ready()
        return {"payload": PAYLOAD, "content_hash": "a" * 64}

    async def reserve(self, client_hash):
        await self.ready()
        assert len(client_hash) == 64
        return self.allowed, 30


def client(database=None, configured=True):
    settings = Settings(
        database_url="postgresql://unused" if configured else "",
        hash_secret="x" * 32 if configured else "",
    )
    return TestClient(create_app(settings, database or ContractDatabase()))


def answer(**changes):
    return {
        "event_id": str(uuid4()),
        "release_id": "phase1-v1",
        "activity_id": "base_cases_practice_03",
        "option_id": "c",
        **changes,
    }


def test_health_is_not_database_readiness():
    with client(configured=False) as api:
        assert api.get("/health").status_code == 200
        response = api.get("/ready")
        assert response.status_code == 503
        assert response.json()["code"] == "not_configured"


def test_seed_projection_omits_future_grading():
    with client() as api:
        seed = api.get("/api/v1/demo/profiles/demo_base_cases/seed").json()
        assert len(seed["activities"]) == 12
        assert all("correct_option" not in q and "explanation" not in q for q in seed["activities"])
        assert api.get("/api/v1/demo/profiles/missing/seed").status_code == 404


def test_real_response_shape_and_server_grading():
    with client() as api:
        correct = api.post("/api/v1/bootstrap/answer", json=answer())
        assert correct.status_code == 200, correct.text
        assert correct.json()["is_correct"] is True
        assert correct.json()["persisted"] is False
        wrong = api.post("/api/v1/bootstrap/answer", json=answer(option_id="b"))
        assert wrong.json()["is_correct"] is False


@pytest.mark.parametrize("changes", [{"is_correct": True}, {"option_id": "fake"}])
def test_rejects_forged_or_unknown_fields(changes):
    with client() as api:
        assert api.post("/api/v1/bootstrap/answer", json=answer(**changes)).status_code == 422


def test_version_conflict():
    with client() as api:
        assert (
            api.post("/api/v1/bootstrap/answer", json=answer(release_id="old")).status_code == 409
        )


def test_quota_and_dependency_errors_are_honest():
    with client(ContractDatabase(allowed=False)) as api:
        response = api.post("/api/v1/bootstrap/answer", json=answer())
        assert response.status_code == 429
        assert response.headers["retry-after"] == "30"
    with client(ContractDatabase(unavailable=True)) as api:
        response = api.post("/api/v1/bootstrap/answer", json=answer())
        assert response.status_code == 503
        assert "private database detail" not in response.text


def test_chunked_body_is_bounded_without_content_length():
    with client() as api:
        response = api.post(
            "/api/v1/bootstrap/answer",
            content=iter([b"x" * 131072, b"x" * 131073]),
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 413


def test_cors_accepts_only_configured_origins():
    with client() as api:
        allowed = api.get("/health", headers={"origin": "http://127.0.0.1:3000"})
        blocked = api.get("/health", headers={"origin": "https://attacker.invalid"})
        assert allowed.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
        assert "access-control-allow-origin" not in blocked.headers


def test_catalog_resolves_fresh_item_budget_for_authored_slice():
    seen = {event["activity_id"] for event in PAYLOAD["seed_events"]}
    for concept in ["function_calls", "base_cases"]:
        questions = [q for q in PAYLOAD["questions"] if q["concept_id"] == concept]
        assert len(questions) == 6
        remaining = [q for q in questions if q["id"] not in seen]
        assert sum(q["role"] == "practice" for q in remaining) == 2
        assert sum(q["role"] == "reassessment" for q in remaining) == 1
