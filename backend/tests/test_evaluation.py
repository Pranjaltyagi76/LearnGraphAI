"""Metric oracles and leakage tests, separate from production scoring functions."""

import copy
import json
from fractions import Fraction

import pytest

from app.release import load_release
from evaluation.audit import audit_plan
from evaluation.metrics import diagnosis_metrics, prediction_metrics
from evaluation.runner import evaluate, load_packet, predict_case
from scripts.evaluate import ROOT
from tests.test_engine import event, state_for


@pytest.fixture
def release():
    return load_release(ROOT)


def test_metric_oracles_include_ties_and_single_class_undefined():
    rows = [{"probability": p, "outcome": y} for p, y in [(0.8, 1), (0.8, 0), (0.2, 1), (0.2, 0)]]
    metrics = prediction_metrics(rows, 3)
    assert metrics["roc_auc"] == 0.5
    assert metrics["pr_auc"] == 0.5
    assert metrics["brier"] == pytest.approx(0.34)
    assert metrics["log_loss"] == pytest.approx(0.916290731874155)
    single = prediction_metrics([{"probability": 0.8, "outcome": 1}], 0)
    assert single["roc_auc"] is None and single["pr_auc"] is None
    perfect = prediction_metrics(
        [{"probability": 1.0, "outcome": 1}, {"probability": 0.0, "outcome": 0}], 0
    )
    assert perfect["roc_auc"] == perfect["pr_auc"] == 1
    assert perfect["brier"] == 0


def test_diagnosis_denominators_count_abstention_and_separate_controls():
    rows = [
        {"group": "labeled_gap", "truth": ["a", "b"], "returned": ["b", "x"]},
        {"group": "labeled_gap", "truth": ["a"], "returned": []},
        {"group": "no_gap_control", "truth": [], "returned": ["x"]},
        {"group": "missing_evidence", "truth": [], "returned": []},
        {"group": "no_trigger_control", "truth": [], "returned": []},
    ]
    metrics, extras = diagnosis_metrics(rows)
    assert metrics["precision_at_1"] == 0.5
    assert metrics["precision_at_3"] == 0.25
    assert metrics["recall_at_3"] == 0.25
    assert metrics["mrr"] == 0.5
    assert metrics["coverage"] == 0.4
    assert metrics["false_diagnosis_rate"] == 1
    assert extras["top_1_error_among_answered"] == 0.5


def test_predict_before_observe_and_future_outcome_cannot_change_earlier_predictions(release):
    ids = [
        "function_calls_diagnostic_01",
        "function_calls_practice_01",
        "function_calls_practice_02",
    ]
    events = [event(release.activities[a], i) for i, a in enumerate(ids, 1)]
    result = predict_case(release, events, Fraction(3, 5))
    assert [r["concept_smoothed"] for r in result["rows"]] == [0.5, 0.6, 2 / 3]
    assert [r["prefix_eligible_count"] for r in result["rows"]] == [0, 1, 2]
    events[-1] = event(release.activities[ids[-1]], 3, False)
    changed = predict_case(release, events, Fraction(3, 5))
    assert [r["concept_smoothed"] for r in changed["rows"]] == [0.5, 0.6, 2 / 3]
    assert changed["rows"][-1]["outcome"] == 0


def test_eligibility_exclusions_are_reported_not_silently_removed(release):
    q = release.activities["function_calls_diagnostic_01"]
    result = predict_case(release, [event(q, 1, hints=None), event(q, 2)], Fraction(1, 2))
    assert result["rows"] == []
    assert result["exclusions"] == {"hints_unknown": 1, "repeat_activity": 1}


def test_training_fit_does_not_read_development_outcomes_or_labels(release):
    packet, manifest, digest = load_packet(ROOT, release)
    # Only training + development are used in this test; final-audit outputs stay unobserved.
    args = dict(
        source_commit="0" * 40, measured_at="2026-11-20T00:00:00.000Z", manifest_hash=digest
    )
    first = evaluate(release, packet, manifest, "development", **args)
    changed = copy.deepcopy(packet)
    for case in changed["cases"]:
        if case["split"] == "development":
            for e in case["events"]:
                if e["kind"] == "response":
                    e["response"]["option_id"] = release.activities[e["activity_id"]][
                        "correct_option"
                    ]
            case["annotation"]["acceptable_gap_concept_ids"] = ["call_stack"]
    other = evaluate(release, changed, manifest, "development", **args)
    assert first["training_fit"] == other["training_fit"]
    relabeled = copy.deepcopy(packet)
    for case in relabeled["cases"]:
        case["annotation"]["acceptable_gap_concept_ids"] = ["memoization"]
    labels = evaluate(release, relabeled, manifest, "development", **args)
    for a, b in zip(first["cases"], labels["cases"], strict=True):
        assert a["diagnosis"] == b["diagnosis"]
        for baseline in a["recommendation"]:
            assert a["recommendation"][baseline]["plan"] == b["recommendation"][baseline]["plan"]


def test_independent_plan_auditor_catches_forged_reference_and_lock(release):
    from app.diagnosis import diagnose
    from app.recommendation import make_plan

    events = [event(release.activities["base_cases_diagnostic_01"], 1, False)]
    state = state_for(release, events)
    d = diagnose(release.graph, state, "base_cases", None, release.config)
    plan = make_plan(release.graph, release.activities, state, "base_cases", d, release.config)
    assert not audit_plan(release.graph, release.activities, state, plan, [])["issues"]
    target_index = next(i for i, item in enumerate(plan.items) if item.blocked_by_concept_ids)
    forged = plan.items[target_index].model_copy(update={"readiness": "ready"})
    bad = plan.model_copy(update={"items": [*plan.items[:target_index], forged]})
    assert (
        "invalid_prerequisite_lock"
        in audit_plan(release.graph, release.activities, state, bad, [])["issues"]
    )
    bad = plan.model_copy(
        update={"items": [plan.items[0].model_copy(update={"activity_id": "missing"})]}
    )
    assert (
        "invalid_catalog_reference"
        in audit_plan(release.graph, release.activities, state, bad, [])["issues"]
    )


def test_variant_manifest_has_independent_versioned_expectations():
    raw = (ROOT / "evaluation/variants.v1.json").read_bytes()
    variants = json.loads(raw)
    assert variants["variant_version"] == "domain-variants-v1"
    assert len(variants["variants"]) == 4
