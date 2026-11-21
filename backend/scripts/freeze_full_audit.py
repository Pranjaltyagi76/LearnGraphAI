"""Author full-track scenario assumptions without calling production inference."""

import argparse
import hashlib
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

ROOT = Path(__file__).resolve().parents[2]


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def inputs():
    catalog = json.loads((ROOT / "curriculum/catalog-full.v1.json").read_bytes())
    activities = {a["id"]: a for a in catalog["activities"]}
    concepts = sorted(catalog["covered_concept_ids"])
    cases = []

    def case(
        name,
        split,
        focus,
        patterns,
        behavior,
        truth=(),
        group="no_gap_control",
        hints=None,
        repeat=False,
        lesson=False,
        exhausted=False,
    ):
        learner = f"full_audit_{split}_{name}"
        events = []
        suffixes = [
            "diagnostic_01",
            "practice_01",
            "practice_02",
            "practice_03",
            "practice_04",
            "reassessment_01",
        ]
        run = str(uuid5(NAMESPACE_URL, learner + ":run"))
        for concept, outcomes in patterns.items():
            for i, correct in enumerate(outcomes):
                a = activities[f"{concept}_{suffixes[i]}"]
                option = (
                    a["correct_option"]
                    if correct
                    else next(o["id"] for o in a["options"] if o["id"] != a["correct_option"])
                )
                n = len(events) + 1
                events.append(
                    {
                        "schema_version": 1,
                        "kind": "response",
                        "event_id": str(uuid5(NAMESPACE_URL, f"{learner}:{n}")),
                        "sequence_number": n,
                        "activity_id": a["id"],
                        "activity_version": a["version"],
                        "assessment_run_id": run,
                        "occurred_at": f"2026-11-19T01:{n // 60:02}:{n % 60:02}.000Z",
                        "time_spent_seconds": None,
                        "hints_used": hints,
                        "response": {"option_id": option},
                    }
                )
        if repeat:
            event = dict(events[0])
            n = len(events) + 1
            event.update(
                event_id=str(uuid5(NAMESPACE_URL, learner + ":retry")),
                sequence_number=n,
                hints_used=0,
                occurred_at=f"2026-11-19T01:{n // 60:02}:{n % 60:02}.000Z",
                response={"option_id": activities[event["activity_id"]]["correct_option"]},
            )
            events.append(event)
        if lesson:
            a = activities[f"{focus}_lesson_01"]
            n = len(events) + 1
            events.append(
                {
                    "schema_version": 1,
                    "kind": "lesson_completed",
                    "event_id": str(uuid5(NAMESPACE_URL, learner + ":lesson")),
                    "sequence_number": n,
                    "activity_id": a["id"],
                    "activity_version": a["version"],
                    "assessment_run_id": run,
                    "occurred_at": f"2026-11-19T01:{n // 60:02}:{n % 60:02}.000Z",
                    "time_spent_seconds": None,
                }
            )
        cases.append(
            {
                "id": learner,
                "learner_id": learner,
                "scenario_group": learner,
                "split": split,
                "focus_concept_id": focus,
                "events": events,
                "annotation": {
                    "expected_behavior": behavior,
                    "acceptable_gap_concept_ids": list(truth),
                    "evaluation_group": group,
                    "expected_plan_state": "catalog_exhausted" if exhausted else None,
                },
            }
        )

    # Distinct learner groups and different outcome patterns; item/family reuse is disclosed.
    for concept in concepts:
        case(
            concept,
            "train",
            concept,
            {concept: [True, False, True, True]},
            None,
            group="training_only",
            hints=0,
        )
        case(
            concept,
            "development",
            concept,
            {concept: [False, False, True]},
            "supported_gap",
            [concept],
            "labeled_gap",
            hints=0,
        )
        patterns = {c: [True] * 3 for c in concepts}
        patterns[concept] = [False] * 3
        case(concept, "test", concept, patterns, "supported_gap", [concept], "labeled_gap", hints=0)

    ready = {c: [True] * 3 for c in concepts}
    case(
        "unknown",
        "test",
        "function_calls",
        {},
        "no_failed_trigger",
        group="no_trigger_control",
        hints=0,
    )
    case(
        "early_failure",
        "test",
        "state_definition",
        {"state_definition": [False]},
        "insufficient_evidence",
        group="missing_evidence",
        hints=0,
    )
    case(
        "upstream",
        "test",
        "memoization",
        {**ready, "overlapping_subproblems": [False] * 3, "memoization": [True, False, True]},
        "supported_gap",
        ["overlapping_subproblems"],
        "labeled_gap",
        hints=0,
    )
    case(
        "competing",
        "test",
        "memoization",
        {
            **ready,
            "overlapping_subproblems": [False] * 3,
            "dp_base_cases": [False] * 3,
            "memoization": [False] * 3,
        },
        "supported_gap",
        ["memoization", "overlapping_subproblems", "dp_base_cases"],
        "labeled_gap",
        hints=0,
    )
    case(
        "mixed",
        "test",
        "tabulation",
        {**ready, "tabulation": [True, False, True]},
        "ambiguous",
        hints=0,
    )
    case(
        "ready_with_old_failure",
        "test",
        "tabulation",
        {**ready, "tabulation": [False, True, True, True, True]},
        "no_supported_gap",
        hints=0,
    )
    case(
        "recent_contradiction",
        "test",
        "base_cases",
        {**ready, "base_cases": [False, False, False, True, True]},
        "ambiguous",
        hints=0,
    )
    case(
        "hinted",
        "test",
        "base_cases",
        {"base_cases": [False] * 3},
        "insufficient_evidence",
        group="missing_evidence",
        hints=1,
    )
    case(
        "unknown_hint_retry",
        "test",
        "function_calls",
        {"function_calls": [False]},
        "insufficient_evidence",
        group="missing_evidence",
        hints=None,
        repeat=True,
    )
    case(
        "exhausted",
        "test",
        "state_definition",
        {"state_definition": [False] * 6},
        "supported_gap",
        ["state_definition"],
        "labeled_gap",
        hints=0,
        exhausted=True,
    )
    case(
        "lesson_only",
        "test",
        "function_calls",
        {},
        "no_failed_trigger",
        group="no_trigger_control",
        hints=0,
        lesson=True,
    )
    case(
        "unrelated_weakness",
        "test",
        "tabulation",
        {**ready, "function_calls": [False] * 3, "tabulation": [False] * 3},
        "supported_gap",
        ["tabulation"],
        "labeled_gap",
        hints=0,
    )
    packet = {
        "scenario_version": "full-scenarios-v1",
        "cases": cases,
        "label_provenance": (
            "Authored scenario assumptions before this audit's first run. No diagnosis output "
            "used as a label. Not independent educator or causal truth. Training labels are unused."
        ),
        "exposure": (
            "Public at freeze; existing baseline implementation already known. "
            "No blind/generalization claim or output-guided tuning."
        ),
        "item_reuse": (
            "Same full product items/families across disjoint learner groups; "
            "no item or family holdout claim."
        ),
    }
    data = encoded(packet)
    manifest = {
        "scenario_version": "full-scenarios-v1",
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "random_baseline_seed": 761121,
        "split_counts": {"train": 12, "development": 12, "test": 24},
        "release_manifest_sha256": hashlib.sha256(
            (ROOT / "contracts/releases/full-v1.json").read_bytes()
        ).hexdigest(),
        "policy_tuning": "None; baseline-v1 unchanged before/after this audit",
        "test_exposure": packet["exposure"],
    }
    return {
        "evaluation/full-scenarios.v1.json": data,
        "evaluation/full-manifest.v1.json": encoded(manifest),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    for name, data in inputs().items():
        p = ROOT / name
        if p.exists():
            if p.read_bytes() != data:
                raise ValueError(f"Frozen audit differs: {name}")
        elif args.write:
            p.write_bytes(data)
        else:
            raise ValueError(f"Missing frozen audit: {name}")
    print(
        "Full-track 12/12/24 scenario inputs frozen; inference has not been invoked by this tool."
    )


if __name__ == "__main__":
    main()
