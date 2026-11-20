"""Frozen offline protocol v1. Not yet wired to the deployed bootstrap API.

JSON Schema validates structure; catalog references and analysis semantics also
require the checks specified in contracts/protocol.md during Phase 2.
"""

import hashlib
import json
import re
from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field, model_validator

MAX_SAFE_INTEGER = 2**53 - 1
ID = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]{0,79}$", max_length=80)]
Digest = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
Count = Annotated[int, Field(ge=0, le=300)]
Revision = Annotated[int, Field(ge=0, le=MAX_SAFE_INTEGER)]
Unit = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


def exact_integer(value):
    if type(value) is not int:
        raise ValueError("An integer is required")
    return value


V1 = Annotated[Literal[1], BeforeValidator(exact_integer)]


def exact_boolean(value):
    if type(value) is not bool:
        raise ValueError("A boolean is required")
    return value


TrueOnly = Annotated[Literal[True], BeforeValidator(exact_boolean)]
FalseOnly = Annotated[Literal[False], BeforeValidator(exact_boolean)]


def uuid_text(value: str) -> str:
    return str(UUID(value))


EventID = Annotated[
    str,
    Field(
        pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[45][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
    ),
    AfterValidator(uuid_text),
]


TIMESTAMP_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?(?:Z|[+-]\d{2}:\d{2})$"


def utc_milliseconds(value: str) -> str:
    if not re.fullmatch(TIMESTAMP_PATTERN, value):
        raise ValueError(
            "RFC3339 with explicit timezone and at most millisecond precision required"
        )
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


Timestamp = Annotated[
    str,
    Field(
        min_length=20,
        max_length=29,
        pattern=TIMESTAMP_PATTERN,
        json_schema_extra={"format": "date-time"},
    ),
    AfterValidator(utc_milliseconds),
]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class Versions(Contract):
    release_id: ID
    release_hash: Digest
    seed_id: ID
    seed_version: Annotated[int, Field(ge=1, le=MAX_SAFE_INTEGER)]
    graph_version: ID
    catalog_version: ID
    model_version: ID


class ReleaseSummary(Contract):
    contract_version: V1
    release_id: ID
    release_hash: Digest
    graph_version: ID
    catalog_version: ID
    model_version: ID
    profiles_version: ID


class EventBase(Contract):
    schema_version: V1
    event_id: EventID
    sequence_number: Annotated[int, Field(ge=1, le=300)]
    activity_id: ID
    activity_version: Annotated[int, Field(ge=1, le=MAX_SAFE_INTEGER)]
    assessment_run_id: EventID
    occurred_at: Timestamp
    time_spent_seconds: Annotated[int, Field(ge=0, le=86400)] | None = None


class OptionResponse(Contract):
    option_id: Annotated[str, Field(pattern=r"^[a-z0-9_-]{1,8}$")]


class ResponseEvent(EventBase):
    kind: Literal["response"]
    response: OptionResponse
    hints_used: Annotated[int, Field(ge=0, le=100)] | None = None


class LessonEvent(EventBase):
    kind: Literal["lesson_completed"]


Event = Annotated[ResponseEvent | LessonEvent, Field(discriminator="kind")]


class AnalyzeRequest(Contract):
    contract_version: V1
    versions: Versions
    profile_id: ID
    sandbox_id: EventID
    local_revision: Revision
    focus_concept_id: ID
    trigger_event_id: EventID | None = None
    events: Annotated[list[Event], Field(max_length=200)]


class ProfileSeed(Contract):
    seed_id: ID
    seed_version: Annotated[int, Field(ge=1, le=MAX_SAFE_INTEGER)]
    profile_id: ID
    name: Annotated[str, Field(min_length=1, max_length=40)]
    synthetic: TrueOnly
    archetype: Literal["upstream_gap", "target_gap", "sparse", "ambiguous"]
    summary: Annotated[str, Field(min_length=1, max_length=240)]
    focus_concept_id: ID
    events: Annotated[list[Event], Field(max_length=100)]


class ProfileInfo(Contract):
    id: ID
    name: Annotated[str, Field(min_length=1, max_length=40)]
    synthetic: TrueOnly
    archetype: Literal["upstream_gap", "target_gap", "sparse", "ambiguous"]
    summary: Annotated[str, Field(min_length=1, max_length=240)]
    focus_concept_id: ID


class ProfileSummary(ProfileInfo):
    versions: Versions


class ProfilesResponse(Contract):
    contract_version: V1
    profiles: Annotated[list[ProfileSummary], Field(min_length=1, max_length=4)]


class PublicConcept(Contract):
    id: ID
    definition: Annotated[str, Field(min_length=1, max_length=500)]
    group: Literal["recursion", "dynamic_programming"]


class PublicEdge(Contract):
    prerequisite: ID
    dependent: ID
    type: Literal["prerequisite"]


class Provenance(Contract):
    origin: Literal["original"]
    attribution: Annotated[str, Field(min_length=1, max_length=120)]
    created_on: Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")]
    license_status: Literal["not_licensed"]


class ActivityBase(Contract):
    id: ID
    version: Annotated[int, Field(ge=1, le=MAX_SAFE_INTEGER)]
    primary_concept_id: ID
    secondary_concept_ids: Annotated[list[ID], Field(max_length=11)]
    active: TrueOnly
    foundational: bool
    difficulty: Unit
    provenance: Provenance


class PublicOption(Contract):
    id: Annotated[str, Field(pattern=r"^[a-z0-9_-]{1,8}$")]
    text: Annotated[str, Field(min_length=1, max_length=500)]


class PublicQuestion(ActivityBase):
    kind: Literal["question"]
    role: Literal["diagnostic", "practice", "reassessment"]
    question_type: Literal["multiple_choice", "code_tracing", "bug_identification"]
    prompt: Annotated[str, Field(min_length=1, max_length=2000)]
    code: Annotated[str, Field(max_length=4000)] | None
    options: Annotated[list[PublicOption], Field(min_length=4, max_length=4)]


class PublicLesson(ActivityBase):
    kind: Literal["lesson"]
    role: Literal["lesson"]
    title: Annotated[str, Field(min_length=1, max_length=120)]
    body: Annotated[str, Field(min_length=1, max_length=4000)]


PublicActivity = Annotated[PublicQuestion | PublicLesson, Field(discriminator="kind")]


class SeedResponse(Contract):
    contract_version: V1
    versions: Versions
    profile: ProfileInfo
    seed_events: Annotated[list[Event], Field(max_length=100)]
    concepts: Annotated[list[PublicConcept], Field(min_length=12, max_length=12)]
    edges: Annotated[list[PublicEdge], Field(max_length=132)]
    activities: Annotated[list[PublicActivity], Field(max_length=128)]


class GradedEvent(Contract):
    event_id: EventID
    activity_id: ID
    activity_version: Annotated[int, Field(ge=1, le=MAX_SAFE_INTEGER)]
    provenance: Literal["canonical_seed", "visitor_demo"]
    kind: Literal["response", "lesson_completed"]
    concept_id: ID
    catalog_role: Literal["diagnostic", "practice", "reassessment", "lesson"]
    attempt_number: Count
    is_correct: bool | None
    eligible: bool
    eligibility_reason: Literal[
        "eligible", "repeat_activity", "hints_used", "hints_unknown", "lesson"
    ]
    occurred_at: Timestamp
    explanation: Annotated[str, Field(max_length=2000)] | None


class Estimate(Contract):
    concept_id: ID
    eligible_count: Count
    successes: Count
    total_attempts: Count
    distinct_questions: Count
    estimate: Unit | None
    evidence_state: Literal["not_assessed", "early_estimate", "supported_estimate"]
    performance_state: Literal["unknown", "early", "weak", "developing", "ready"]
    recent_failures: Annotated[int, Field(ge=0, le=3)]
    last_evidence_at: Timestamp | None
    evidence_event_ids: Annotated[list[EventID], Field(max_length=300)]


class GapCandidate(Contract):
    concept_id: ID
    relation: Literal["target", "upstream"]
    distance: Annotated[int, Field(ge=0, le=3)]
    path: Annotated[list[ID], Field(min_length=1, max_length=4)]
    score: Unit
    evidence_event_ids: Annotated[list[EventID], Field(min_length=3, max_length=300)]
    reason: Literal["supported_target_weakness", "supported_upstream_weakness"]


class EvidenceRequest(Contract):
    concept_id: ID
    reason: Literal["not_assessed", "early_estimate"]
    needed_observations: Annotated[int, Field(ge=1, le=3)]


class Diagnosis(Contract):
    status: Literal[
        "supported_gap",
        "insufficient_evidence",
        "ambiguous",
        "no_supported_gap",
        "no_failed_trigger",
    ]
    trigger_event_id: EventID | None
    candidates: Annotated[list[GapCandidate], Field(max_length=3)]
    evidence_requests: Annotated[list[EvidenceRequest], Field(max_length=12)]
    alternatives: Annotated[
        list[Literal["item_difficulty", "response_error", "tag_mismatch", "mixed_evidence"]],
        Field(max_length=4),
    ]


class PlanItem(Contract):
    activity_id: ID
    activity_version: Annotated[int, Field(ge=1, le=MAX_SAFE_INTEGER)]
    concept_id: ID
    role: Literal["diagnostic", "practice", "reassessment", "lesson"]
    readiness: Literal["ready", "locked"]
    blocked_by_concept_ids: Annotated[list[ID], Field(max_length=12)]
    depends_on_activity_ids: Annotated[list[ID], Field(max_length=4)]
    reason: Literal[
        "gap_practice", "gather_evidence", "reassessment", "lesson_support", "further_practice"
    ]
    score: Annotated[float, Field(ge=-0.5, le=1, allow_inf_nan=False)]


class Plan(Contract):
    mode: Literal["remediation", "assessment", "practice", "none"]
    status: Literal["ready", "blocked", "catalog_exhausted", "no_suitable_activity"]
    items: Annotated[list[PlanItem], Field(max_length=5)]


class AnalysisBundle(Contract):
    contract_version: V1
    versions: Versions
    profile_id: ID
    sandbox_id: EventID
    local_revision: Revision
    focus_concept_id: ID
    requested_trigger_event_id: EventID | None
    digest_algorithm: Literal["sha256-lg-c14n-v1"]
    history_digest: Digest
    persisted: FalseOnly
    accepted_visitor_events: Annotated[int, Field(ge=0, le=200)]
    graded_events: Annotated[list[GradedEvent], Field(max_length=300)]
    estimates: Annotated[list[Estimate], Field(min_length=12, max_length=12)]
    diagnosis: Diagnosis
    plan: Plan


class PendingSubmission(Contract):
    event: Event
    focus_concept_id: ID
    trigger_event_id: EventID | None
    request_revision: Revision


def sandbox_key(profile_id: str, versions: Versions) -> str:
    values = [
        profile_id,
        versions.release_id,
        versions.release_hash,
        versions.seed_id,
        versions.seed_version,
        versions.graph_version,
        versions.catalog_version,
        versions.model_version,
    ]
    return "learngraph:v1:" + json.dumps(values, ensure_ascii=False, separators=(",", ":"))


class SandboxRecord(Contract):
    schema_version: V1
    key: Annotated[str, Field(min_length=1, max_length=1024)]
    versions: Versions
    profile_id: ID
    sandbox_id: EventID
    revision: Revision
    persistence: Literal["indexeddb", "session"]
    acknowledged_events: Annotated[list[Event], Field(max_length=200)]
    pending: PendingSubmission | None
    last_analysis: AnalysisBundle | None
    analysis_input_revision: Revision | None
    analysis_history_digest: Digest | None

    @model_validator(mode="after")
    def bounded_total(self):
        if len(self.acknowledged_events) + (self.pending is not None) > 200:
            raise ValueError("Acknowledged plus pending event count exceeds 200")
        if self.key != sandbox_key(self.profile_id, self.versions):
            raise ValueError("Storage key does not match the selected profile/versions")
        acknowledged = normalized_events(self.acknowledged_events)
        if len(acknowledged) != len(self.acknowledged_events):
            raise ValueError("Stored acknowledged events must be unique")
        if self.pending:
            event = self.pending.event
            if self.pending.request_revision != self.revision:
                raise ValueError("Pending request revision mismatch")
            if event.sequence_number != len(acknowledged) + 1 or any(
                e["event_id"] == event.event_id for e in acknowledged
            ):
                raise ValueError("Pending event identity/sequence mismatch")
            if acknowledged and event.occurred_at < acknowledged[-1]["occurred_at"]:
                raise ValueError("Pending event predates acknowledged history")
        if self.last_analysis is None:
            if self.analysis_input_revision is not None or self.analysis_history_digest is not None:
                raise ValueError("Cache metadata without a cached bundle")
        else:
            bundle = self.last_analysis
            if (
                bundle.profile_id != self.profile_id
                or bundle.versions != self.versions
                or bundle.sandbox_id != self.sandbox_id
                or bundle.local_revision > self.revision
                or bundle.local_revision != self.analysis_input_revision
                or bundle.history_digest != self.analysis_history_digest
                or bundle.accepted_visitor_events != len(acknowledged)
            ):
                raise ValueError("Cached bundle identity mismatch")
            snapshot = AnalyzeRequest(
                contract_version=1,
                versions=self.versions,
                profile_id=self.profile_id,
                sandbox_id=self.sandbox_id,
                local_revision=bundle.local_revision,
                focus_concept_id=bundle.focus_concept_id,
                trigger_event_id=bundle.requested_trigger_event_id,
                events=self.acknowledged_events,
            )
            if history_digest(snapshot) != bundle.history_digest:
                raise ValueError("Cached bundle digest does not describe acknowledged history")
        return self


class HealthResponse(Contract):
    status: Literal["ok"]
    service: Literal["learngraph-ai-api"]
    stage: Annotated[str, Field(pattern=r"^phase[0-7]$")]


class ReadyResponse(Contract):
    status: Literal["ready"]
    release_id: ID


class PredictionSummary(Contract):
    baseline: Literal["global_rate", "concept_smoothed"]
    eligible_predictions: Annotated[int, Field(ge=1, le=MAX_SAFE_INTEGER)]
    positive_outcomes: Revision
    negative_outcomes: Revision
    excluded_events: Revision
    log_loss: Annotated[float, Field(ge=0, le=40, allow_inf_nan=False)]
    brier: Unit
    roc_auc: Unit | None
    pr_auc: Unit | None


class DiagnosisSummary(Contract):
    baseline: Literal["lowest_estimate", "prerequisite_aware"]
    labeled_gap_cases: Annotated[int, Field(ge=1, le=MAX_SAFE_INTEGER)]
    all_cases: Revision
    no_gap_cases: Revision
    missing_evidence_cases: Revision
    no_trigger_cases: Revision
    precision_at_1: Unit
    precision_at_3: Unit
    recall_at_1: Unit
    recall_at_3: Unit
    mrr: Unit
    coverage: Unit
    false_diagnosis_rate: Unit | None


class RecommendationSummary(Contract):
    baseline: Literal["random_eligible", "lowest_estimate", "prerequisite_aware"]
    cases: Annotated[int, Field(ge=1, le=MAX_SAFE_INTEGER)]
    emitted_items: Revision
    prerequisite_checks: Revision
    reassessment_items: Revision
    exhaustion_cases: Revision
    catalog_validity: Unit | None
    prerequisite_validity: Unit | None
    reassessment_distinctness: Unit | None
    exhaustion_honesty: Unit | None


class EvaluationSummary(Contract):
    contract_version: V1
    evaluation_version: ID
    scenario_version: ID
    graph_version: ID
    catalog_version: ID
    model_version: ID
    source_commit: Annotated[str, Field(pattern=r"^[a-f0-9]{40}$")]
    measured_at: Timestamp
    split_manifest_hash: Digest
    synthetic_only: TrueOnly
    prediction: Annotated[list[PredictionSummary], Field(min_length=2, max_length=2)]
    diagnosis: Annotated[list[DiagnosisSummary], Field(min_length=2, max_length=2)]
    recommendation: Annotated[list[RecommendationSummary], Field(min_length=3, max_length=3)]
    limitations: Annotated[
        list[Annotated[str, Field(min_length=1, max_length=240)]],
        Field(min_length=1, max_length=10),
    ]


class ErrorDetail(Contract):
    path: Annotated[str, Field(max_length=120)]
    reason: Literal[
        "required", "invalid_type", "invalid_value", "unknown_reference", "out_of_range"
    ]


class ErrorEnvelope(Contract):
    code: Literal[
        "invalid_request",
        "invalid_response",
        "invalid_order",
        "invalid_timestamp",
        "invalid_trigger",
        "unknown_activity",
        "profile_not_found",
        "not_found",
        "http_error",
        "event_conflict",
        "version_mismatch",
        "payload_too_large",
        "body_timeout",
        "quota_exhausted",
        "not_configured",
        "dependency_unavailable",
        "analysis_timeout",
        "evaluation_not_published",
    ]
    message: Annotated[str, Field(min_length=1, max_length=240)]
    request_id: EventID
    details: Annotated[list[ErrorDetail], Field(max_length=10)]


class ContractViolation(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def normalized_events(events: list[ResponseEvent | LessonEvent]) -> list[dict]:
    unique = {}
    for event in events:
        item = event.model_dump(mode="json")
        if event.event_id in unique and unique[event.event_id] != item:
            raise ContractViolation("event_conflict")
        unique.setdefault(event.event_id, item)
    result = list(unique.values())
    if any(e["sequence_number"] != i for i, e in enumerate(result, 1)):
        raise ContractViolation("invalid_order")
    if any(a["occurred_at"] > b["occurred_at"] for a, b in zip(result, result[1:], strict=False)):
        raise ContractViolation("invalid_order")
    return result


def canonical_json(value: dict | list) -> bytes:
    """lg-c14n-v1: ASCII keys, integer/string/bool/null inputs, UTF-8, sorted keys."""
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def semantic_input(request: AnalyzeRequest) -> dict:
    return {
        "contract_version": request.contract_version,
        "versions": request.versions.model_dump(mode="json"),
        "profile_id": request.profile_id,
        "focus_concept_id": request.focus_concept_id,
        "trigger_event_id": request.trigger_event_id,
        "events": normalized_events(request.events),
    }


def history_digest(request: AnalyzeRequest) -> str:
    return hashlib.sha256(canonical_json(semantic_input(request))).hexdigest()


def validate_clock(request: AnalyzeRequest, seed_last: str, received_at: datetime) -> None:
    """Admission check only; wall-clock time is never hashed or used for scoring."""
    if received_at.tzinfo is None:
        raise ValueError("Explicit received_at timezone required")
    lower = utc_milliseconds(seed_last)
    upper = (
        (received_at.astimezone(UTC) + timedelta(minutes=5))
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )
    for event in normalized_events(request.events):
        if not lower < event["occurred_at"] <= upper:
            raise ContractViolation("invalid_timestamp")
