import asyncio
import hashlib
import hmac
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException

from app.analysis import analyze
from app.config import Settings
from app.contracts import (
    AnalysisBundle,
    AnalyzeRequest,
    ContractViolation,
    EvaluationSummary,
    ProfilesResponse,
    ReleaseSummary,
    SeedResponse,
)
from app.database import Database
from app.telemetry import emit_request_metrics

MAX_BODY = 256 * 1024


class APIError(Exception):
    def __init__(self, status: int, code: str, message: str, retry_after: int | None = None):
        self.status, self.code, self.message, self.retry_after = status, code, message, retry_after


def failure(status: int, code: str, message: str, request_id: str, retry: int | None = None):
    return JSONResponse(
        status_code=status,
        content={"code": code, "message": message, "request_id": request_id, "details": []},
        headers={"Retry-After": str(retry)} if retry else {},
    )


class BodyLimit:
    """Bound bytes while receiving, including requests without Content-Length."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        body = bytearray()
        try:
            async with asyncio.timeout(5):
                while True:
                    event = await receive()
                    if event["type"] == "http.disconnect":
                        return
                    body.extend(event.get("body", b""))
                    if len(body) > MAX_BODY:
                        response = failure(
                            413, "payload_too_large", "Request exceeds 256 KiB.", str(uuid4())
                        )
                        return await response(scope, receive, send)
                    if not event.get("more_body", False):
                        break
        except TimeoutError:
            response = failure(408, "body_timeout", "Request body timed out.", str(uuid4()))
            return await response(scope, receive, send)
        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, replay, send)


class Answer(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    event_id: Annotated[UUID, Field(strict=False)]
    release_id: Annotated[str, Field(min_length=1, max_length=80)]
    activity_id: Annotated[str, Field(min_length=1, max_length=80)]
    option_id: Annotated[str, Field(min_length=1, max_length=8)]


def public_question(question: dict) -> dict:
    return {key: question[key] for key in ("id", "concept_id", "role", "prompt", "code", "options")}


def create_app(settings: Settings | None = None, database=None) -> FastAPI:
    config = settings or Settings.from_env()
    db = database or Database(config)

    @asynccontextmanager
    async def lifespan(application):
        await db.open()
        yield
        await db.close()

    application = FastAPI(title="LearnGraph AI", version="0.1.0", lifespan=lifespan)
    application.state.request_count = 0

    @application.middleware("http")
    async def request_context(request: Request, call_next):
        request.state.request_id = str(uuid4())
        started = time.perf_counter()
        first = application.state.request_count == 0
        application.state.request_count += 1
        try:
            async with asyncio.timeout(10):
                response = await call_next(request)
        except TimeoutError:
            response = failure(
                503,
                "analysis_timeout",
                "Service timed out. Please retry.",
                request.state.request_id,
            )
        except Exception:
            # Never serialize a database exception/DSN or submitted response to clients/logs.
            response = failure(
                503,
                "dependency_unavailable",
                "Live service is unavailable.",
                request.state.request_id,
            )
        response.headers["X-Request-ID"] = request.state.request_id
        elapsed_ms = (time.perf_counter() - started) * 1000
        response.headers["Server-Timing"] = f"api;dur={elapsed_ms:.2f}"
        response.headers["Cache-Control"] = "no-store"
        if config.environment == "production":
            emit_request_metrics(request.state.request_id, response.status_code, elapsed_ms, first)
        return response

    @application.exception_handler(APIError)
    async def api_error(request: Request, exc: APIError):
        return failure(exc.status, exc.code, exc.message, request.state.request_id, exc.retry_after)

    @application.exception_handler(ContractViolation)
    async def contract_error(request: Request, exc: ContractViolation):
        status = (
            404
            if exc.code == "profile_not_found"
            else 409
            if exc.code in {"version_mismatch", "event_conflict"}
            else 422
        )
        return failure(
            status,
            exc.code,
            "Analysis input could not be accepted. Check the demo state.",
            request.state.request_id,
        )

    @application.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, exc: RequestValidationError):
        return failure(
            422,
            "invalid_request",
            "Response does not match the request schema.",
            request.state.request_id,
        )

    @application.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        return failure(
            exc.status_code,
            "not_found" if exc.status_code == 404 else "http_error",
            "Route unavailable.",
            request.state.request_id,
        )

    def require_config():
        if not config.configured:
            raise APIError(503, "not_configured", "Live database access is not configured.")

    async def canonical():
        require_config()
        return await db.release()

    async def published(release_id: str | None = None):
        require_config()
        if not config.analysis_release_id:
            raise APIError(503, "not_configured", "Full analysis is not configured.")
        if release_id is not None and release_id != config.analysis_release_id:
            raise APIError(409, "version_mismatch", "This analysis release is not supported.")
        return await db.analysis_release()

    async def guard(request: Request):
        require_config()
        address = request.client.host if request.client else "unknown"
        if config.on_vercel:
            address = request.headers.get("x-vercel-forwarded-for", address).split(",")[0].strip()
        day = datetime.now(UTC).date().isoformat()
        digest = hmac.new(
            config.hash_secret.encode(), f"{day}:{address}".encode(), hashlib.sha256
        ).hexdigest()
        allowed, retry = await db.reserve(digest)
        if not allowed:
            raise APIError(
                429, "quota_exhausted", "Demo request limit reached. Please retry later.", retry
            )

    @application.get("/health")
    async def health():
        return {
            "status": "ok",
            "service": "learngraph-ai-api",
            "stage": "phase3" if config.analysis_release_id else "phase1",
        }

    @application.get("/ready")
    async def ready():
        require_config()
        await db.ready()
        return {"status": "ready", "release_id": config.release_id}

    @application.get("/api/v1/demo/profiles")
    async def profiles():
        release = await canonical()
        return {"release_id": config.release_id, "profiles": release["payload"]["profiles"]}

    @application.get("/api/v1/demo/release", response_model=ReleaseSummary)
    async def analysis_pointer():
        return (await published()).summary()

    @application.get("/api/v1/releases/{release_id}/profiles", response_model=ProfilesResponse)
    async def analysis_profiles(release_id: str):
        return (await published(release_id)).profiles()

    @application.get(
        "/api/v1/releases/{release_id}/profiles/{profile_id}/seed", response_model=SeedResponse
    )
    async def analysis_seed(release_id: str, profile_id: str):
        package = await published(release_id)
        if profile_id not in package.release.profiles:
            raise APIError(404, "profile_not_found", "Synthetic profile not found.")
        return package.seed(profile_id)

    @application.post("/api/v1/demo/analyze", response_model=AnalysisBundle)
    async def full_analysis(body: AnalyzeRequest, request: Request):
        await guard(request)
        receipt = datetime.now(UTC)
        package = await published(body.versions.release_id)
        return await asyncio.to_thread(analyze, package.release, body, received_at=receipt)

    @application.get("/api/v1/analytics/evaluation", response_model=EvaluationSummary)
    async def evaluation():
        package = await published()
        if package.evaluation is None:
            raise APIError(404, "evaluation_not_published", "No measured evaluation is published.")
        return package.evaluation

    @application.get("/api/v1/demo/profiles/{profile_id}/seed")
    async def seed(profile_id: str):
        release = await canonical()
        payload = release["payload"]
        profile = next((p for p in payload["profiles"] if p["id"] == profile_id), None)
        if not profile:
            raise APIError(404, "profile_not_found", "Synthetic profile not found.")
        return {
            "stage": "phase1",
            "release_id": config.release_id,
            "content_hash": release["content_hash"],
            "profile": profile,
            "seed_events": payload["seed_events"],
            "concepts": payload["concepts"],
            "edges": payload["edges"],
            "activities": [public_question(q) for q in payload["questions"]],
        }

    @application.post("/api/v1/bootstrap/answer")
    async def answer(body: Answer, request: Request):
        # Phase 1 verifies grading and the real database path, not Phase 2 diagnosis/replay.
        await guard(request)
        if body.release_id != config.release_id:
            raise APIError(409, "version_mismatch", "Published content changed. Reload the demo.")
        payload = (await canonical())["payload"]
        question = next((q for q in payload["questions"] if q["id"] == body.activity_id), None)
        if not question or body.option_id not in {o["id"] for o in question["options"]}:
            raise APIError(422, "invalid_response", "Choose an option from the current question.")
        return {
            "stage": "phase1",
            "event_id": str(body.event_id),
            "release_id": config.release_id,
            "activity_id": question["id"],
            "is_correct": body.option_id == question["correct_option"],
            "explanation": question["explanation"],
            "persisted": False,
        }

    application.add_middleware(BodyLimit)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(config.origins),
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
        expose_headers=["X-Request-ID", "Server-Timing", "Retry-After"],
    )
    return application


app = create_app()
