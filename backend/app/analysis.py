"""Pure Phase 2 orchestration. No FastAPI, database, environment, or filesystem."""

from datetime import datetime

from app.contracts import (
    AnalysisBundle,
    AnalyzeRequest,
    ContractViolation,
    history_digest,
    normalized_events,
    validate_clock,
)
from app.diagnosis import diagnose
from app.recommendation import make_plan
from app.release import Release
from app.replay import replay
from app.validation import validate_bundle


def analyze(release: Release, request: AnalyzeRequest, *, received_at: datetime) -> AnalysisBundle:
    if request.profile_id not in release.profiles:
        raise ContractViolation("profile_not_found")
    if request.versions != release.versions(request.profile_id):
        raise ContractViolation("version_mismatch")
    if request.focus_concept_id not in release.graph.parents:
        raise ContractViolation("invalid_request")
    profile = release.profiles[request.profile_id]
    seed = normalized_events(profile.events)
    visitor = normalized_events(request.events)
    validate_clock(
        request, seed[-1]["occurred_at"] if seed else "0001-01-01T00:00:00.000Z", received_at
    )
    state = replay(release.graph.order, release.activities, seed, visitor, release.config)
    diagnosis = diagnose(
        release.graph, state, request.focus_concept_id, request.trigger_event_id, release.config
    )
    plan = make_plan(
        release.graph,
        release.activities,
        state,
        request.focus_concept_id,
        diagnosis,
        release.config,
    )
    bundle = AnalysisBundle(
        contract_version=1,
        versions=request.versions,
        profile_id=request.profile_id,
        sandbox_id=request.sandbox_id,
        local_revision=request.local_revision,
        focus_concept_id=request.focus_concept_id,
        requested_trigger_event_id=request.trigger_event_id,
        digest_algorithm="sha256-lg-c14n-v1",
        history_digest=history_digest(request),
        persisted=False,
        accepted_visitor_events=len(visitor),
        graded_events=list(state.graded),
        estimates=list(state.estimates.values()),
        diagnosis=diagnosis,
        plan=plan,
    )
    validate_bundle(bundle, release.graph, release.activities, state)
    return bundle
