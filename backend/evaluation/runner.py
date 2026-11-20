"""Causal-prefix prediction and retrospective synthetic audit, with separate labels."""

import hashlib
import json
from collections import Counter
from fractions import Fraction

from pydantic import TypeAdapter

from app.contracts import EvaluationSummary, Event, normalized_events
from app.diagnosis import diagnose
from app.recommendation import completed_cycles, make_plan
from app.replay import replay
from evaluation.audit import audit_plan
from evaluation.metrics import diagnosis_metrics, prediction_metrics, ratio
from scripts.check_phase0 import validate_scenarios

EVENTS = TypeAdapter(list[Event])


def predict_case(release, raw_events: list[dict], global_probability: Fraction) -> dict:
    events = normalized_events(EVENTS.validate_python(raw_events))
    final = replay(release.graph.order, release.activities, [], events, release.config)
    rows, exclusions = [], Counter()
    for index, grade in enumerate(final.graded):
        if not grade.eligible:
            exclusions[grade.eligibility_reason] += 1
            continue
        prefix = replay(release.graph.order, release.activities, [], events[:index], release.config)
        concept = grade.concept_id
        rows.append(
            {
                "event_id": grade.event_id,
                "activity_id": grade.activity_id,
                "concept_id": concept,
                "prefix_events": index,
                "prefix_eligible_count": prefix.estimates[concept].eligible_count,
                "prefix_successes": prefix.estimates[concept].successes,
                "outcome": int(grade.is_correct),
                "global_rate": float(global_probability),
                "concept_smoothed": float(prefix.probabilities[concept]),
            }
        )
    return {"rows": rows, "exclusions": dict(sorted(exclusions.items())), "state": final}


def load_packet(root, release):
    raw = (root / "evaluation/scenarios.v1.json").read_bytes()
    manifest_raw = (root / "evaluation/manifest.v1.json").read_bytes()
    packet, manifest = json.loads(raw), json.loads(manifest_raw)
    if hashlib.sha256(raw).hexdigest() != manifest["source_hash"]:
        raise ValueError("Scenario source hash mismatch")
    for path, field in (
        ("curriculum/catalog-slice.v1.json", "catalog_hash"),
        ("curriculum/model-config.v1.json", "model_config_hash"),
    ):
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != manifest[field]:
            raise ValueError("Evaluation dependency hash mismatch")
    validate_scenarios(packet, manifest, release.activities)
    return packet, manifest, hashlib.sha256(manifest_raw).hexdigest()


def evaluate(
    release,
    packet: dict,
    split_manifest: dict,
    split: str,
    *,
    source_commit: str,
    measured_at: str,
    manifest_hash: str,
) -> dict:
    training_successes, training_count = 0, 0
    for case in packet["cases"]:
        if case["split"] != "train":
            continue
        events = normalized_events(EVENTS.validate_python(case["events"]))
        state = replay(release.graph.order, release.activities, [], events, release.config)
        training_count += sum(g.eligible for g in state.graded)
        training_successes += sum(g.eligible and g.is_correct for g in state.graded)
    prediction_policy = release.config["prediction"]
    prior_s = prediction_policy["global_rate_prior_successes"]
    prior_f = prediction_policy["global_rate_prior_failures"]
    global_probability = Fraction(training_successes + prior_s, training_count + prior_s + prior_f)
    cases, failures = [], []
    diagnosis_rows = {name: [] for name in ("lowest_estimate", "prerequisite_aware")}
    recommendation_rows = {
        name: [] for name in ("random_eligible", "lowest_estimate", "prerequisite_aware")
    }
    for case in packet["cases"]:
        if case["split"] != split:
            continue
        # Inference receives only versioned observations/focus; annotations stay here.
        result = predict_case(release, case["events"], global_probability)
        state = result.pop("state")
        annotation = case["annotation"]
        truth = annotation["acceptable_gap_concept_ids"]
        diagnoses, plans = {}, {}
        for name in diagnosis_rows:
            diagnosis = diagnose(
                release.graph, state, case["focus_concept_id"], None, release.config, baseline=name
            )
            diagnoses[name] = diagnosis.model_dump(mode="json")
            diagnosis_rows[name].append(
                {
                    "returned": [c.concept_id for c in diagnosis.candidates],
                    "truth": truth,
                    "group": annotation["evaluation_group"],
                }
            )
        actual = diagnoses["prerequisite_aware"]["status"]
        if actual != annotation["expected_behavior"]:
            failures.append(
                {
                    "case_id": case["id"],
                    "check": "diagnosis_state",
                    "expected": annotation["expected_behavior"],
                    "actual": actual,
                }
            )
        for name in recommendation_rows:
            diagnosis = diagnose(
                release.graph, state, case["focus_concept_id"], None, release.config
            )
            # Stable per-case RNG, independent of list order or Python's randomized hash().
            case_seed = split_manifest["random_baseline_seed"] + int.from_bytes(
                hashlib.sha256(case["learner_id"].encode()).digest()[:8], "big"
            )
            plan = make_plan(
                release.graph,
                release.activities,
                state,
                case["focus_concept_id"],
                diagnosis,
                release.config,
                baseline=name,
                random_seed=case_seed,
            )
            audit = audit_plan(release.graph, release.activities, state, plan, truth)
            expected = annotation["expected_plan_state"]
            audit["exhaustion_applicable"] = expected == "catalog_exhausted"
            audit["exhaustion_correct"] = plan.status == expected if expected else None
            if expected and plan.status != expected:
                failures.append(
                    {
                        "case_id": case["id"],
                        "baseline": name,
                        "check": "plan_state",
                        "expected": expected,
                        "actual": plan.status,
                    }
                )
            for issue in audit["issues"]:
                failures.append({"case_id": case["id"], "baseline": name, "check": issue})
            recommendation_rows[name].append(audit)
            plans[name] = {"plan": plan.model_dump(mode="json"), "audit": audit}
        cases.append(
            {
                "case_id": case["id"],
                "learner_id": case["learner_id"],
                "split": split,
                "prediction": result,
                "estimates": [e.model_dump(mode="json") for e in state.estimates.values()],
                "diagnosis": diagnoses,
                "recommendation": plans,
                "observed_completed_cycles": completed_cycles(state),
                "annotation": annotation,
            }
        )
    predictions, extras, undefined = [], {}, {}
    excluded = sum(sum(c["prediction"]["exclusions"].values()) for c in cases)
    for name in ("global_rate", "concept_smoothed"):
        rows = [
            {"probability": row[name], "outcome": row["outcome"]}
            for c in cases
            for row in c["prediction"]["rows"]
        ]
        metrics = prediction_metrics(rows, excluded)
        predictions.append({"baseline": name, **metrics})
        for key, value in metrics.items():
            if value is None:
                undefined[f"prediction.{name}.{key}"] = "Both outcome classes are required."
    diagnoses = []
    for name, rows in diagnosis_rows.items():
        metrics, extra = diagnosis_metrics(rows)
        diagnoses.append({"baseline": name, **metrics})
        extras[f"diagnosis.{name}"] = extra
        if metrics["false_diagnosis_rate"] is None:
            undefined[f"diagnosis.{name}.false_diagnosis_rate"] = "No no-gap controls."
    recommendations = []
    for name, rows in recommendation_rows.items():

        def total(key, rows=rows):
            return sum(r[key] for r in rows)

        emitted, checks = total("emitted_items"), len(rows)
        reassess = total("reassessment_items")
        exhaustion = total("exhaustion_applicable")
        metrics = {
            "baseline": name,
            "cases": len(cases),
            "emitted_items": emitted,
            "prerequisite_checks": checks,
            "reassessment_items": reassess,
            "exhaustion_cases": exhaustion,
            "catalog_validity": ratio(total("catalog_valid_items"), emitted),
            "prerequisite_validity": ratio(total("prerequisite_plan_valid"), checks),
            "reassessment_distinctness": ratio(total("distinct_reassessment_items"), reassess),
            "exhaustion_honesty": ratio(
                sum(r["exhaustion_correct"] is True for r in rows if r["exhaustion_applicable"]),
                exhaustion,
            ),
        }
        recommendations.append(metrics)
        fits = [f for r in rows for f in r["difficulty_fits"]]
        extras[f"recommendation.{name}"] = {
            "labeled_gap_denominator": total("labeled_gaps"),
            "gap_coverage": ratio(total("covered_gaps"), total("labeled_gaps")),
            "repeated_questions": total("repeated_questions"),
            "mean_authored_difficulty_fit": ratio(sum(fits), len(fits)),
            "plans_passing_all_invariants": sum(not r["issues"] for r in rows),
            "plans_checked": len(rows),
            "prerequisite_item_checks": total("prerequisite_checks"),
            "prerequisite_item_validity": ratio(
                total("valid_prerequisite_checks"), total("prerequisite_checks")
            ),
        }
        for key, value in metrics.items():
            if value is None:
                undefined[f"recommendation.{name}.{key}"] = "Zero applicable denominator."
    identity = release.manifest["identity"]
    summary = EvaluationSummary(
        contract_version=1,
        evaluation_version="evaluation-v1",
        scenario_version="scenarios-v1",
        graph_version=identity["graph_version"],
        catalog_version=identity["catalog_version"],
        model_version=identity["model_version"],
        source_commit=source_commit,
        measured_at=measured_at,
        split_manifest_hash=manifest_hash,
        synthetic_only=True,
        prediction=predictions,
        diagnosis=diagnoses,
        recommendation=recommendations,
        limitations=[
            "Public exposed synthetic audit; not blind or evidence of real-world generalization.",
            "Only two concepts have questions; items/families recur across learner splits.",
            "Gap labels are scenario assumptions, not causal truth; no measured learning benefit.",
            "The small audit does not support uncertainty intervals or calibrated mastery claims.",
            "Prerequisite validity counts returned plans with correct ordering/readiness/locks.",
        ],
    )
    return {
        "split": split,
        "summary": summary.model_dump(mode="json"),
        "extra_metrics": extras,
        "undefined_metric_reasons": undefined,
        "cases": cases,
        "failures": failures,
        "training_fit": {
            "eligible_events": training_count,
            "successes": training_successes,
            "probability_numerator": global_probability.numerator,
            "probability_denominator": global_probability.denominator,
        },
    }
