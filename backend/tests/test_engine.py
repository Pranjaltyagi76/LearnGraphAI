"""Independent arithmetic/workflow and adversarial tests for FR-06–11/14."""

import copy
import itertools
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import pytest
from pydantic import TypeAdapter

from app.analysis import analyze
from app.contracts import AnalyzeRequest, ContractViolation, Event
from app.diagnosis import diagnose
from app.graph import Graph
from app.recommendation import completed_cycles, make_plan
from app.release import Release, load_release
from app.replay import replay

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 11, 20, tzinfo=UTC)
EVENTS = TypeAdapter(list[Event])


@pytest.fixture
def release():
    return load_release(ROOT)


def event(activity, index, correct=True, hints=0, *, run="run", day=19):
    return {
        "schema_version": 1,
        "kind": "response",
        "event_id": str(uuid5(NAMESPACE_URL, f"test:{run}:{index}:{activity['id']}")),
        "sequence_number": index,
        "activity_id": activity["id"],
        "activity_version": activity["version"],
        "assessment_run_id": str(uuid5(NAMESPACE_URL, run)),
        "occurred_at": f"2026-11-{day:02}T12:{(index - 1) // 60:02}:{(index - 1) % 60:02}.000Z",
        "hints_used": hints,
        "time_spent_seconds": None,
        "response": {
            "option_id": activity["correct_option"]
            if correct
            else next(o["id"] for o in activity["options"] if o["id"] != activity["correct_option"])
        },
    }


def fixture_request():
    return json.loads((ROOT / "contracts/fixtures/analysis-example.json").read_bytes())["request"]


def state_for(release, events):
    parsed = EVENTS.validate_python(events)
    return replay(
        release.graph.order,
        release.activities,
        [],
        [e.model_dump(mode="json") for e in parsed],
        release.config,
    )


def test_full_bundle_matches_independent_hand_calculation(release):
    fixture = json.loads((ROOT / "contracts/fixtures/analysis-example.json").read_bytes())
    actual = analyze(release, AnalyzeRequest.model_validate(fixture["request"]), received_at=NOW)
    assert actual.model_dump(mode="json") == fixture["bundle"]


@pytest.mark.parametrize(
    "profile,status",
    [
        ("demo_base_cases", "supported_gap"),
        ("demo_upstream", "supported_gap"),
        ("demo_sparse", "no_failed_trigger"),
        ("demo_ambiguous", "ambiguous"),
    ],
)
def test_profiles_have_expected_evidence_states(release, profile, status):
    raw = fixture_request()
    raw.update(profile_id=profile, versions=release.versions(profile).model_dump(mode="json"))
    bundle = analyze(release, AnalyzeRequest.model_validate(raw), received_at=NOW)
    assert bundle.diagnosis.status == status
    assert bundle.persisted is False
    assert len(bundle.estimates) == 12
    assert all(e.estimate is None for e in bundle.estimates if not e.eligible_count)


@pytest.mark.parametrize("outcomes", list(itertools.product((False, True), repeat=6)))
def test_all_six_question_outcome_patterns_use_exact_counts(release, outcomes):
    questions = [
        a
        for a in release.activities.values()
        if a["primary_concept_id"] == "function_calls" and a["kind"] == "question"
    ]
    events = [
        event(a, i, correct)
        for i, (a, correct) in enumerate(zip(questions, outcomes, strict=True), 1)
    ]
    state = state_for(release, events)
    estimate = state.estimates["function_calls"]
    expected = Fraction(sum(outcomes) + 2, 10)
    assert state.probabilities["function_calls"] == expected
    assert estimate.successes == sum(outcomes)
    assert estimate.eligible_count == 6
    assert estimate.recent_failures == sum(not c for c in outcomes[-3:])
    diagnosis = diagnose(release.graph, state, "function_calls", None, release.config)
    qualifies = expected < Fraction(45, 100) and sum(not c for c in outcomes[-3:]) >= 2
    assert bool(diagnosis.candidates) == qualifies
    if all(outcomes):
        assert diagnosis.status == "no_failed_trigger"


@pytest.mark.parametrize(
    "hints,reason", [(None, "hints_unknown"), (1, "hints_used"), (0, "eligible")]
)
def test_retry_cannot_rescue_first_slot_and_lessons_add_no_evidence(release, hints, reason):
    question = release.activities["base_cases_diagnostic_01"]
    lesson = release.activities["base_cases_lesson_01"]
    events = [event(question, 1, False, hints), event(question, 2)]
    lesson_event = event(question, 3)
    for key in ("response", "hints_used"):
        lesson_event.pop(key)
    lesson_event.update(kind="lesson_completed", activity_id=lesson["id"], activity_version=1)
    state = state_for(release, events + [lesson_event])
    assert [g.eligibility_reason for g in state.graded] == [reason, "repeat_activity", "lesson"]
    assert state.estimates["base_cases"].eligible_count == int(hints == 0)
    assert state.estimates["function_calls"].eligible_count == 0
    assert state.estimates["base_cases"].total_attempts == 2


@pytest.mark.parametrize(
    "mutation,code",
    [
        ("bad_option", "invalid_response"),
        ("unknown", "unknown_activity"),
        ("version", "version_mismatch"),
        ("kind", "invalid_response"),
        ("seed_collision", "event_conflict"),
        ("time", "invalid_timestamp"),
        ("conflict", "event_conflict"),
        ("order", "invalid_order"),
        ("trigger", "invalid_trigger"),
        ("release", "version_mismatch"),
        ("profile", "profile_not_found"),
        ("focus", "invalid_request"),
    ],
)
def test_admission_rejects_conflicts_and_bad_references(release, mutation, code):
    raw = fixture_request()
    item = event(release.activities["base_cases_practice_03"], 1, day=20)
    raw["events"] = [item]
    if mutation == "bad_option":
        item["response"]["option_id"] = "nope"
    elif mutation == "unknown":
        item["activity_id"] = "missing"
    elif mutation == "version":
        item["activity_version"] = 1
    elif mutation == "kind":
        item.update(kind="lesson_completed")
        item.pop("response")
        item.pop("hints_used")
    elif mutation == "seed_collision":
        item["event_id"] = release.profiles["demo_base_cases"].events[0].event_id
    elif mutation == "time":
        item["occurred_at"] = "2026-11-18T00:00:00Z"
    elif mutation == "conflict":
        raw["events"].append({**copy.deepcopy(item), "hints_used": 1})
    elif mutation == "order":
        item["sequence_number"] = 2
    elif mutation == "trigger":
        raw["trigger_event_id"] = release.profiles["demo_base_cases"].events[0].event_id
    elif mutation == "release":
        raw["versions"]["release_hash"] = "0" * 64
    elif mutation == "profile":
        raw["profile_id"] = "missing"
    elif mutation == "focus":
        raw["focus_concept_id"] = "missing"
    with pytest.raises(ContractViolation) as error:
        analyze(
            release,
            AnalyzeRequest.model_validate(raw),
            received_at=datetime(2026, 11, 21, tzinfo=UTC),
        )
    assert error.value.code == code


def test_identical_retry_preserves_output_and_transport_changes_preserve_semantics(release):
    raw = fixture_request()
    item = event(release.activities["base_cases_practice_03"], 1, day=20)
    raw["events"] = [item]
    now = datetime(2026, 11, 21, tzinfo=UTC)
    first = analyze(release, AnalyzeRequest.model_validate(raw), received_at=now)
    raw["events"].append(copy.deepcopy(item))
    assert analyze(release, AnalyzeRequest.model_validate(raw), received_at=now) == first
    raw["local_revision"] = 90
    other = analyze(release, AnalyzeRequest.model_validate(raw), received_at=now)
    assert other.history_digest == first.history_digest
    assert other.diagnosis == first.diagnosis and other.plan == first.plan


def test_fresh_cycle_includes_incorrect_practice_but_rejects_cross_run_and_retries(release):
    ids = ["base_cases_diagnostic_01", "base_cases_practice_01", "base_cases_reassessment_01"]
    events = [event(release.activities[a], i, False) for i, a in enumerate(ids, 1)]
    state = state_for(release, events)
    assert len(completed_cycles(state)) == 1
    events[1]["assessment_run_id"] = str(uuid5(NAMESPACE_URL, "other"))
    assert completed_cycles(state_for(release, events)) == []
    events[1]["assessment_run_id"] = events[0]["assessment_run_id"]
    repeated = event(release.activities[ids[1]], 1, run="earlier")
    repeated["occurred_at"] = "2026-11-18T00:00:00.000Z"
    for i, e in enumerate(events, 2):
        e["sequence_number"] = i
    assert completed_cycles(state_for(release, [repeated, *events])) == []


def test_unassessed_parent_is_assessed_first_and_lesson_does_not_unlock(release):
    events = [
        event(release.activities[f"base_cases_{role}"], i, False)
        for i, role in enumerate(("diagnostic_01", "practice_01", "practice_02"), 1)
    ]
    state = state_for(release, events)
    diagnosis = diagnose(release.graph, state, "base_cases", None, release.config)
    plan = make_plan(
        release.graph, release.activities, state, "base_cases", diagnosis, release.config
    )
    assert diagnosis.candidates[0].concept_id == "base_cases"
    assert diagnosis.evidence_requests[0].concept_id == "function_calls"
    assert plan.items[0].concept_id == "function_calls"
    assert plan.items[0].reason == "gather_evidence"
    assert all(
        i.readiness == "locked"
        for i in plan.items
        if i.concept_id == "base_cases" and i.role != "lesson"
    )


def test_lessons_seen_in_current_run_are_not_reinserted(release):
    raw = fixture_request()
    q = event(release.activities["base_cases_practice_03"], 1, day=20)
    lesson = {k: v for k, v in q.items() if k not in {"hints_used", "response"}}
    lesson.update(kind="lesson_completed", activity_id="base_cases_lesson_01", activity_version=1)
    raw["events"] = [lesson]
    bundle = analyze(
        release, AnalyzeRequest.model_validate(raw), received_at=datetime(2026, 11, 21, tzinfo=UTC)
    )
    assert not any(i.role == "lesson" for i in bundle.plan.items)
    assert bundle.estimates[0].eligible_count == 3


def test_graph_shortest_path_ties_and_depth_boundary():
    variants = json.loads((ROOT / "evaluation/variants.v1.json").read_bytes())["variants"]
    variant = variants[1]
    source = {
        "concepts": [{"id": c} for c in variant["nodes"]],
        "edges": [
            {"prerequisite": a, "dependent": b, "type": "prerequisite"} for a, b in variant["edges"]
        ],
    }
    graph = Graph(source)
    assert variant["excluded_depth_four"] not in graph.paths("t")
    for concept, expected in variant["expected_paths"].items():
        assert graph.paths("t")[concept] == tuple(expected)
    source["edges"].append({"prerequisite": "e", "dependent": "t", "type": "prerequisite"})
    assert Graph(source).paths("t")["e"] == ("e", "t")


def test_equal_gap_scores_are_stable_and_capped_at_three(release):
    variant = json.loads((ROOT / "evaluation/variants.v1.json").read_bytes())["variants"][0]
    graph = Graph(
        {
            "concepts": [{"id": c} for c in variant["nodes"]],
            "edges": [
                {"prerequisite": a, "dependent": b, "type": "prerequisite"}
                for a, b in variant["edges"]
            ],
        }
    )
    activities, events = {}, []
    for concept in variant["nodes"]:
        for i in range(3):
            activity = copy.deepcopy(release.activities["function_calls_practice_01"])
            activity.update(id=f"fixture_{concept}_{i}", primary_concept_id=concept)
            activities[activity["id"]] = activity
            events.append(event(activity, len(events) + 1, False))
    state = replay(graph.order, activities, [], events, release.config)
    diagnosis = diagnose(graph, state, "t", None, release.config)
    assert [c.concept_id for c in diagnosis.candidates] == variant["expected_candidate_ids"]
    assert diagnosis.candidates[1].score == diagnosis.candidates[2].score == 0.214286


@pytest.mark.parametrize("successes,expected", [(7, "developing"), (11, "ready")])
def test_exact_threshold_equality_is_not_rounded_before_classification(
    release, successes, expected
):
    activities, events = {}, []
    for i in range(16):
        activity = copy.deepcopy(release.activities["function_calls_practice_01"])
        activity["id"] = f"fixture_boundary_{i}"
        activities[activity["id"]] = activity
        events.append(event(activity, i + 1, i < successes))
    state = replay(release.graph.order, activities, [], events, release.config)
    assert state.estimates["function_calls"].performance_state == expected


def test_context_tag_variant_does_not_change_primary_evidence(release):
    events = [event(release.activities["base_cases_diagnostic_01"], 1, False)]
    baseline = state_for(release, events)
    changed = copy.deepcopy(release.activities)
    for activity in changed.values():
        activity["secondary_concept_ids"] = ["call_stack"]
    variant = replay(release.graph.order, changed, [], events, release.config)
    assert variant.estimates == baseline.estimates
    assert variant.estimates["call_stack"].eligible_count == 0


def test_parent_outside_diagnosis_radius_still_locks_available_activity(release):
    graph = Graph(
        {
            "concepts": [{"id": c} for c in "abcdt"],
            "edges": [
                {"prerequisite": a, "dependent": b, "type": "prerequisite"}
                for a, b in [("a", "b"), ("b", "c"), ("c", "d"), ("d", "t")]
            ],
        }
    )
    activities, events = {}, []
    for i in range(3):
        q = copy.deepcopy(release.activities["function_calls_practice_01"])
        q.update(id=f"fixture_t_{i}", primary_concept_id="t")
        activities[q["id"]] = q
        events.append(event(q, i + 1, False))
    q = copy.deepcopy(release.activities["function_calls_diagnostic_01"])
    q.update(id="fixture_b_diagnostic", primary_concept_id="b", foundational=False)
    activities[q["id"]] = q
    state = replay(graph.order, activities, [], events, release.config)
    diagnosis = diagnose(graph, state, "t", None, release.config)
    assert "a" not in [r.concept_id for r in diagnosis.evidence_requests]
    plan = make_plan(graph, activities, state, "t", diagnosis, release.config)
    assert plan.items[0].blocked_by_concept_ids == ["a"]
    assert plan.items[0].readiness == "locked"
    assert plan.status == "blocked"
    assert not any(i.concept_id == "a" for i in plan.items)


def test_exhausted_hinted_questions_cannot_be_reused_as_new_evidence(release):
    questions = [
        a
        for a in release.activities.values()
        if a["kind"] == "question" and a["primary_concept_id"] == "function_calls"
    ]
    events = [event(a, i, False, hints=1) for i, a in enumerate(questions, 1)]
    state = state_for(release, events)
    d = diagnose(release.graph, state, "function_calls", None, release.config)
    plan = make_plan(release.graph, release.activities, state, "function_calls", d, release.config)
    assert state.estimates["function_calls"].estimate is None
    assert d.status == "insufficient_evidence"
    assert plan.status == "catalog_exhausted"
    assert not any(i.role != "lesson" for i in plan.items)


def test_uncovered_root_returns_no_suitable_activity(release):
    state = state_for(release, [])
    d = diagnose(release.graph, state, "state_definition", None, release.config)
    plan = make_plan(
        release.graph, release.activities, state, "state_definition", d, release.config
    )
    assert plan.status == "no_suitable_activity"
    assert plan.items == []


def test_explanations_keep_unknown_evidence_separate_from_gap_claims(release):
    from app.explanation import explain

    raw = fixture_request()
    profile = "demo_sparse"
    raw.update(profile_id=profile, versions=release.versions(profile).model_dump(mode="json"))
    bundle = analyze(release, AnalyzeRequest.model_validate(raw), received_at=NOW)
    text = " ".join(explain(bundle))
    assert "no failure diagnosis" in text
    assert "further eligible observations needed" in text
    assert "support a suspected performance gap" not in text


def test_seed_failure_can_anchor_one_failed_visitor_practice_before_reassessment(release):
    raw = fixture_request()
    practice = event(release.activities["base_cases_practice_03"], 1, False, day=20)
    raw["events"] = [practice]
    bundle = analyze(
        release, AnalyzeRequest.model_validate(raw), received_at=datetime(2026, 11, 21, tzinfo=UTC)
    )
    reassess = next(i for i in bundle.plan.items if i.role == "reassessment")
    assert reassess.readiness == "ready"
    assert reassess.depends_on_activity_ids == []
    seed = [e.model_dump(mode="json") for e in release.profiles[raw["profile_id"]].events]
    answer = event(release.activities["base_cases_reassessment_01"], 2, False, day=20)
    state = replay(
        release.graph.order, release.activities, seed, [practice, answer], release.config
    )
    assert completed_cycles(state)[-1]["practice_activity_ids"] == [practice["activity_id"]]


def test_response_semantic_validation_rejects_forged_score(release):
    from app.validation import validate_bundle

    request = AnalyzeRequest.model_validate(fixture_request())
    bundle = analyze(release, request, received_at=NOW)
    seed = [e.model_dump(mode="json") for e in release.profiles[request.profile_id].events]
    state = replay(release.graph.order, release.activities, seed, [], release.config)
    diagnosis = bundle.diagnosis.model_copy(
        update={"candidates": [bundle.diagnosis.candidates[0].model_copy(update={"score": 0.99})]}
    )
    with pytest.raises(ValueError, match="Inconsistent analysis"):
        validate_bundle(
            bundle.model_copy(update={"diagnosis": diagnosis}),
            release.graph,
            release.activities,
            state,
        )


@pytest.mark.parametrize(
    "profile", ["demo_base_cases", "demo_upstream", "demo_sparse", "demo_ambiguous"]
)
def test_cli_profile_templates_work_with_windows_legacy_stream_encoding(profile):
    env = {**os.environ, "PYTHONIOENCODING": "cp1252"}
    raw = subprocess.check_output(
        [sys.executable, "-m", "scripts.analyze", "--profile", profile, "--explain"],
        cwd=ROOT / "backend",
        env=env,
    )
    result = json.loads(raw)
    assert len(result["analysis"]["estimates"]) == 12
    assert result["analysis"]["profile_id"] == profile
    assert result["explanation"]


@pytest.mark.parametrize("edge", [("a", "a"), ("x", "a"), ("b", "a"), ("a", "b")])
def test_graph_rejects_self_unknown_cycle_and_duplicate(edge):
    source = {
        "concepts": [{"id": c} for c in "ab"],
        "edges": [
            {"prerequisite": a, "dependent": b, "type": "prerequisite"}
            for a, b in [("a", "b"), edge]
        ],
    }
    with pytest.raises(ValueError):
        Graph(source)


@pytest.mark.parametrize("corrupt", ["bytes", "identity", "missing"])
def test_release_rejects_incompatible_package(release, corrupt):
    manifest = copy.deepcopy(release.manifest)
    artifacts = {
        a["path"]: (ROOT / a["path"]).read_bytes() for a in manifest["identity"]["artifacts"]
    }
    if corrupt == "bytes":
        artifacts["curriculum/catalog-slice.v1.json"] += b" "
    elif corrupt == "identity":
        manifest["identity"]["model_version"] = "baseline-v2"
    else:
        artifacts.pop("curriculum/graph.v1.json")
    with pytest.raises(ValueError):
        Release(manifest, artifacts)
