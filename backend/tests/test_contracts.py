"""Offline contract conformance, not diagnosis quality or browser persistence tests."""

import copy
from datetime import UTC, datetime
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import pytest
from pydantic import ValidationError

from app.contracts import (
    AnalysisBundle,
    AnalyzeRequest,
    ContractViolation,
    ProfileSeed,
    PublicQuestion,
    SandboxRecord,
    canonical_json,
    history_digest,
    normalized_events,
    sandbox_key,
    semantic_input,
    validate_clock,
)
from scripts.check_phase0 import (
    ancestors,
    load,
    validate_catalog,
    validate_graph,
    validate_scenarios,
)
from scripts.freeze_phase0 import check_or_create, manifest, protocol_schema

ROOT = Path(__file__).resolve().parents[2]
VECTORS = load("contracts/fixtures/hash-vectors.json")["vectors"]


def request():
    return copy.deepcopy(VECTORS[0]["request"])


@pytest.mark.parametrize("vector", VECTORS, ids=lambda v: v["id"])
def test_canonical_utf8_and_hash_vectors(vector):
    parsed = AnalyzeRequest.model_validate(vector["request"])
    assert canonical_json(semantic_input(parsed)).decode() == vector["canonical_utf8"]
    assert history_digest(parsed) == vector["sha256"]
    assert sandbox_key(parsed.profile_id, parsed.versions) == vector["storage_key"]
    if vector["same_semantics_as"]:
        other = next(v for v in VECTORS if v["id"] == vector["same_semantics_as"])
        assert vector["sha256"] == other["sha256"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("hints_used", True),
        ("hints_used", -1),
        ("hints_used", 101),
        ("hints_used", "0"),
        ("time_spent_seconds", 1.5),
        ("time_spent_seconds", float("nan")),
        ("time_spent_seconds", 86401),
        ("schema_version", True),
        ("schema_version", "1"),
        ("is_correct", True),
        ("concept_id", "base_cases"),
        ("error_type", "oracle_label"),
        ("occurred_at", "2026-11-20T07:00:00"),
        ("occurred_at", "2026-11-20T07:00:60Z"),
        ("occurred_at", "2026-11-20T07:00:00.0001Z"),
        ("event_id", "00000000-0000-0000-0000-000000000000"),
    ],
)
def test_strict_events_reject_forged_coerced_or_ambiguous_values(field, value):
    raw = request()
    raw["events"][0][field] = value
    with pytest.raises(ValidationError):
        AnalyzeRequest.model_validate(raw)


@pytest.mark.parametrize(
    "field,value",
    [
        ("local_revision", True),
        ("local_revision", 2**53),
        ("contract_version", True),
        ("seed_events", []),
    ],
)
def test_strict_envelope_rejects_authority_and_unsafe_numbers(field, value):
    raw = request()
    raw[field] = value
    with pytest.raises(ValidationError):
        AnalyzeRequest.model_validate(raw)


def test_raw_event_cap_precedes_deduplication():
    raw = request()
    raw["events"] *= 200
    parsed = AnalyzeRequest.model_validate(raw)
    assert len(normalized_events(parsed.events)) == 1
    raw["events"].append(copy.deepcopy(raw["events"][0]))
    with pytest.raises(ValidationError):
        AnalyzeRequest.model_validate(raw)


@pytest.mark.parametrize(
    "field,value", [("hints_used", 1), ("time_spent_seconds", 76), ("response", {"option_id": "a"})]
)
def test_reused_id_with_changed_normalized_payload_is_conflict(field, value):
    raw = request()
    changed = copy.deepcopy(raw["events"][0])
    changed[field] = value
    raw["events"].append(changed)
    with pytest.raises(ContractViolation, match="event_conflict"):
        normalized_events(AnalyzeRequest.model_validate(raw).events)


@pytest.mark.parametrize("change", ["gap", "duplicate_sequence", "decreasing_time", "reordered"])
def test_order_errors_are_not_silently_sorted(change):
    raw = copy.deepcopy(next(v["request"] for v in VECTORS if v["id"] == "two_events"))
    if change == "gap":
        raw["events"][1]["sequence_number"] = 3
    elif change == "duplicate_sequence":
        raw["events"][1]["sequence_number"] = 1
    elif change == "decreasing_time":
        raw["events"][1]["occurred_at"] = "2026-11-20T06:59:00Z"
    else:
        raw["events"].reverse()
    with pytest.raises(ContractViolation, match="invalid_order"):
        normalized_events(AnalyzeRequest.model_validate(raw).events)


def test_clock_admission_is_explicit_and_not_semantic_identity():
    parsed = AnalyzeRequest.model_validate(request())
    digest = history_digest(parsed)
    seed_last = "2026-11-19T01:40:00Z"
    validate_clock(parsed, seed_last, datetime(2026, 11, 20, 6, 55, tzinfo=UTC))
    validate_clock(parsed, seed_last, datetime(2027, 1, 1, tzinfo=UTC))
    assert history_digest(parsed) == digest
    with pytest.raises(ContractViolation, match="invalid_timestamp"):
        validate_clock(parsed, seed_last, datetime(2026, 11, 20, 6, 54, 59, tzinfo=UTC))
    with pytest.raises(ContractViolation, match="invalid_timestamp"):
        validate_clock(parsed, "2026-11-20T07:00:00Z", datetime(2026, 11, 20, 7, tzinfo=UTC))
    with pytest.raises(ValueError, match="timezone"):
        validate_clock(parsed, seed_last, datetime(2026, 11, 20, 7))


@pytest.mark.parametrize("mutation", ["unknown", "self", "duplicate", "cycle", "duplicate_node"])
def test_graph_validator_rejects_invalid_instructional_graphs(mutation):
    graph = load("curriculum/graph.v1.json")
    if mutation == "unknown":
        graph["edges"][0]["prerequisite"] = "not_a_concept"
    elif mutation == "self":
        graph["edges"][0]["dependent"] = graph["edges"][0]["prerequisite"]
    elif mutation == "duplicate":
        graph["edges"].append(copy.deepcopy(graph["edges"][0]))
    elif mutation == "cycle":
        graph["edges"].append(
            {
                "prerequisite": "tabulation",
                "dependent": "state_definition",
                "type": "prerequisite",
                "rationale": "invalid fixture",
            }
        )
    else:
        graph["concepts"][1]["id"] = graph["concepts"][0]["id"]
    with pytest.raises(ValueError):
        validate_graph(graph)


def test_bottom_up_route_is_independent_and_top_down_still_requires_tracing():
    parents = validate_graph(load("curriculum/graph.v1.json"))
    assert ancestors("tabulation", parents) == {
        "state_definition",
        "recurrence_relations",
        "state_transitions",
        "dp_base_cases",
    }
    assert "recursive_tracing" in ancestors("memoization", parents)


def test_public_question_schema_rejects_future_grading_keys():
    private = load("curriculum/catalog-slice.v1.json")["activities"][0]
    with pytest.raises(ValidationError):
        PublicQuestion.model_validate(private)
    public = {k: v for k, v in private.items() if k not in {"correct_option", "explanation"}}
    assert PublicQuestion.model_validate(public).id == private["id"]


def test_catalog_rejects_duplicate_choices_and_primary_secondary_overlap():
    ids = {c["id"] for c in load("curriculum/graph.v1.json")["concepts"]}
    catalog = load("curriculum/catalog-slice.v1.json")
    catalog["activities"][0]["options"][1] = copy.deepcopy(catalog["activities"][0]["options"][0])
    with pytest.raises(ValueError):
        validate_catalog(catalog, ids)
    catalog = load("curriculum/catalog-slice.v1.json")
    catalog["activities"][0]["secondary_concept_ids"] = ["function_calls"]
    with pytest.raises(ValueError):
        validate_catalog(catalog, ids)


def test_seed_bound_and_true_synthetic_marker():
    profile = load("curriculum/profiles.v1.json")["profiles"][0]
    bad = {**profile, "synthetic": 1}
    with pytest.raises(ValidationError):
        ProfileSeed.model_validate(bad)
    bad = {**profile, "events": [profile["events"][0]] * 101}
    with pytest.raises(ValidationError):
        ProfileSeed.model_validate(bad)


def test_pending_plus_acknowledged_cannot_exceed_history_bound():
    raw = request()
    events = []
    for i in range(1, 201):
        event = copy.deepcopy(raw["events"][0])
        event.update(event_id=str(uuid5(NAMESPACE_URL, f"learngraph/bound/{i}")), sequence_number=i)
        events.append(event)
    record = {
        "schema_version": 1,
        "key": sandbox_key(raw["profile_id"], AnalyzeRequest.model_validate(raw).versions),
        "versions": raw["versions"],
        "profile_id": raw["profile_id"],
        "sandbox_id": raw["sandbox_id"],
        "revision": 1,
        "persistence": "indexeddb",
        "acknowledged_events": events,
        "pending": None,
        "last_analysis": None,
        "analysis_input_revision": None,
        "analysis_history_digest": None,
    }
    assert len(SandboxRecord.model_validate(record).acknowledged_events) == 200
    event = copy.deepcopy(raw["events"][0])
    event.update(sequence_number=201, event_id=str(uuid5(NAMESPACE_URL, "pending-201")))
    record["pending"] = {
        "event": event,
        "focus_concept_id": "base_cases",
        "trigger_event_id": None,
        "request_revision": 1,
    }
    with pytest.raises(ValidationError):
        SandboxRecord.model_validate(record)


def test_frozen_schema_manifest_and_public_audit_memberships():
    assert load("contracts/protocol-v1.schema.json") == protocol_schema()
    assert load("contracts/release-manifest.json") == manifest()
    catalog = load("curriculum/catalog-slice.v1.json")
    validate_scenarios(
        load("evaluation/scenarios.v1.json"),
        load("evaluation/manifest.v1.json"),
        {a["id"]: a for a in catalog["activities"]},
    )


def test_frozen_artifact_writer_refuses_in_place_changes(tmp_path, monkeypatch):
    import scripts.freeze_phase0 as freezer

    monkeypatch.setattr(freezer, "ROOT", tmp_path)
    path = tmp_path / "frozen.json"
    path.write_bytes(b"original")
    with pytest.raises(ValueError, match="Frozen artifact changed"):
        check_or_create("frozen.json", {"changed": True}, write=True)
    assert path.read_bytes() == b"original"


def stored_example():
    example = load("contracts/fixtures/analysis-example.json")
    req = AnalyzeRequest.model_validate(example["request"])
    return {
        "schema_version": 1,
        "key": sandbox_key(req.profile_id, req.versions),
        "versions": example["request"]["versions"],
        "profile_id": req.profile_id,
        "sandbox_id": req.sandbox_id,
        "revision": 0,
        "persistence": "indexeddb",
        "acknowledged_events": [],
        "pending": None,
        "last_analysis": example["bundle"],
        "analysis_input_revision": 0,
        "analysis_history_digest": example["bundle"]["history_digest"],
    }


def test_hand_calculated_bundle_and_cached_digest_are_consistent():
    example = load("contracts/fixtures/analysis-example.json")
    bundle = AnalysisBundle.model_validate(example["bundle"])
    assert (
        history_digest(AnalyzeRequest.model_validate(example["request"])) == bundle.history_digest
    )
    assert SandboxRecord.model_validate(stored_example()).last_analysis == bundle


def test_pending_focus_and_trigger_survive_a_cached_prior_analysis():
    record = stored_example()
    event = request()["events"][0]
    record.update(
        revision=1,
        pending={
            "event": event,
            "focus_concept_id": "base_cases",
            "trigger_event_id": None,
            "request_revision": 1,
        },
    )
    parsed = SandboxRecord.model_validate(record)
    assert parsed.pending.focus_concept_id == "base_cases"
    assert parsed.last_analysis.local_revision == 0
    assert parsed.pending.request_revision == 1


@pytest.mark.parametrize(
    "change", ["key", "uuid", "digest", "recomputed_digest", "cache_metadata", "pending_revision"]
)
def test_storage_rejects_stale_or_corrupt_identity(change):
    record = stored_example()
    if change == "key":
        record["key"] += "corrupt"
    elif change == "uuid":
        record["sandbox_id"] = str(uuid5(NAMESPACE_URL, "wrong-sandbox"))
    elif change == "digest":
        record["analysis_history_digest"] = "0" * 64
    elif change == "recomputed_digest":
        record["analysis_history_digest"] = "0" * 64
        record["last_analysis"]["history_digest"] = "0" * 64
    elif change == "cache_metadata":
        record["last_analysis"] = None
    else:
        record["pending"] = {
            "event": request()["events"][0],
            "focus_concept_id": "base_cases",
            "trigger_event_id": None,
            "request_revision": 1,
        }
    with pytest.raises(ValidationError):
        SandboxRecord.model_validate(record)
