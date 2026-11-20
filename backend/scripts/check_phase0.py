"""Validate reviewed draft assets, not a deployed analysis or model benchmark."""

import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

from app.contracts import (
    LessonEvent,
    ProfileSeed,
    PublicLesson,
    PublicQuestion,
    ResponseEvent,
    normalized_events,
)
from scripts.freeze_phase0 import manifest, protocol_schema

ROOT = Path(__file__).resolve().parents[2]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate_graph(graph):
    ids = [c["id"] for c in graph["concepts"]]
    require(len(set(ids)) == len(ids) == 12, "Graph requires twelve unique concept IDs")
    parents = defaultdict(set)
    pairs = set()
    for edge in graph["edges"]:
        a, b = edge["prerequisite"], edge["dependent"]
        require(a in ids and b in ids and a != b, "Unknown/self prerequisite edge")
        require((a, b) not in pairs, "Duplicate prerequisite edge")
        require(
            edge["type"] == "prerequisite" and bool(edge["rationale"]), "Missing edge rationale"
        )
        pairs.add((a, b))
        parents[b].add(a)
    visited = set()
    active = set()

    def visit(node):
        require(node not in active, "Prerequisite cycle")
        if node in visited:
            return
        active.add(node)
        for parent in parents[node]:
            visit(parent)
        active.remove(node)
        visited.add(node)

    for node in ids:
        visit(node)
    return parents


def ancestors(node, parents):
    found = set()
    pending = list(parents[node])
    while pending:
        current = pending.pop()
        if current not in found:
            found.add(current)
            pending.extend(parents[current])
    return found


def validate_catalog(catalog, concept_ids):
    activities = catalog["activities"]
    by_id = {a["id"]: a for a in activities}
    require(len(by_id) == len(activities), "Duplicate activity ID")
    questions = []
    for activity in activities:
        public = {k: v for k, v in activity.items() if k not in {"correct_option", "explanation"}}
        if activity["kind"] == "question":
            PublicQuestion.model_validate(public)
            require(
                set(activity)
                == set(PublicQuestion.model_fields) | {"correct_option", "explanation"},
                "Unexpected private question fields",
            )
            options = [o["id"] for o in activity["options"]]
            require(
                len(set(options)) == 4 and activity["correct_option"] in options,
                "Invalid question options/key",
            )
            require(
                len({o["text"].strip().casefold() for o in activity["options"]}) == 4,
                "Duplicate option text",
            )
            require(bool(activity["explanation"]), "Missing grading explanation")
            questions.append(activity)
        else:
            PublicLesson.model_validate(public)
            require(set(activity) == set(PublicLesson.model_fields), "Unexpected lesson fields")
        require(activity["primary_concept_id"] in concept_ids, "Unknown primary concept")
        secondary = activity["secondary_concept_ids"]
        require(len(set(secondary)) == len(secondary), "Duplicate secondary concept")
        require(
            set(secondary) <= concept_ids - {activity["primary_concept_id"]},
            "Invalid secondary concept",
        )
    require(
        len(questions) == catalog["question_count"] == 12,
        "Expected twelve reviewed slice questions",
    )
    require(
        catalog["target_question_count"] == 72 and catalog["lesson_count"] == 2,
        "Wrong slice budget",
    )
    for concept in catalog["covered_concept_ids"]:
        require(
            Counter(q["role"] for q in questions if q["primary_concept_id"] == concept)
            == {"diagnostic": 1, "practice": 4, "reassessment": 1},
            "Wrong per-concept item roles",
        )
    return by_id


def validate_profiles(profiles, activities):
    require(len(profiles) == 4, "Expected four profile definitions")
    require(
        {p["archetype"] for p in profiles} == {"target_gap", "upstream_gap", "sparse", "ambiguous"},
        "Missing contrasting profile archetype",
    )
    seen_ids = set()
    expected_counts = {
        "demo_base_cases": {"function_calls": (3, 3), "base_cases": (3, 0)},
        "demo_upstream": {"function_calls": (3, 0), "base_cases": (3, 2)},
        "demo_sparse": {"function_calls": (1, 1)},
        "demo_ambiguous": {"function_calls": (3, 3), "base_cases": (3, 2)},
    }
    for raw in profiles:
        profile = ProfileSeed.model_validate(raw)
        events = normalized_events(profile.events)
        require(len(events) == len(raw["events"]), "Seed duplicate event")
        seen_activities = set()
        counts = defaultdict(lambda: [0, 0])
        for event in events:
            require(event["event_id"] not in seen_ids, "Cross-profile event ID collision")
            seen_ids.add(event["event_id"])
            require(event["activity_id"] in activities, "Unknown seed activity")
            activity = activities[event["activity_id"]]
            require(
                event["activity_version"] == activity["version"], "Seed activity version mismatch"
            )
            require(event["activity_id"] not in seen_activities, "Repeated seed question")
            seen_activities.add(event["activity_id"])
            require(
                event["kind"] == "response"
                and event["response"]["option_id"] in {o["id"] for o in activity["options"]},
                "Invalid seed option",
            )
            if event["hints_used"] == 0:
                counts[activity["primary_concept_id"]][0] += 1
                counts[activity["primary_concept_id"]][1] += (
                    event["response"]["option_id"] == activity["correct_option"]
                )
        require(
            {k: tuple(v) for k, v in counts.items()} == expected_counts[profile.profile_id],
            "Profile does not match reviewed evidence counts",
        )


def validate_scenarios(dataset, split_manifest, activities):
    cases = dataset["cases"]
    require(len(cases) == 24, "Expected 24 authored audit cases")
    counts = Counter(c["split"] for c in cases)
    require(counts == {"train": 4, "development": 8, "test": 12}, "Audit split counts changed")
    require(dict(counts) == split_manifest["split_counts"], "Split manifest counts mismatch")
    require(len({c["id"] for c in cases}) == len(cases), "Duplicate audit case ID")
    require(len({c["learner_id"] for c in cases}) == len(cases), "Learner leakage across cases")
    groups = {}
    fingerprints = {}
    event_ids = set()
    for case in cases:
        split = case["split"]
        group = case["scenario_group"]
        require(groups.setdefault(group, split) == split, "Scenario-group leakage")
        require(case["learner_id"].startswith("eval_"), "Public demo learner leaked into audit")
        require(case["learner_id"] in split_manifest["splits"][split], "Missing split membership")
        parsed = [
            (ResponseEvent if e["kind"] == "response" else LessonEvent).model_validate(e)
            for e in case["events"]
        ]
        events = normalized_events(parsed)
        require(len(events) == len(parsed), "Duplicate audit event")
        signature = []
        for event in events:
            require(event["event_id"] not in event_ids, "Cross-learner event ID collision")
            event_ids.add(event["event_id"])
            activity = activities[event["activity_id"]]
            require(
                event["activity_version"] == activity["version"], "Audit activity version mismatch"
            )
            if event["kind"] == "response":
                require(activity["kind"] == "question", "Lesson used as a scored question")
                require(
                    event["response"]["option_id"] in {o["id"] for o in activity["options"]},
                    "Unknown audit option",
                )
            else:
                require(activity["kind"] == "lesson", "Question used as a lesson")
            signature.append(
                {
                    k: v
                    for k, v in event.items()
                    if k not in {"event_id", "sequence_number", "assessment_run_id", "occurred_at"}
                }
            )
        fingerprint = json.dumps(signature, sort_keys=True, separators=(",", ":"))
        require(
            fingerprints.setdefault(fingerprint, split) == split,
            "Duplicate observation pattern across splits",
        )
        require(
            case["annotation"]["source"].startswith("hand-authored"),
            "Missing annotation provenance",
        )
        expected_groups = {
            "supported_gap": "labeled_gap",
            "insufficient_evidence": "missing_evidence",
            "ambiguous": "no_gap_control",
            "no_supported_gap": "no_gap_control",
            "no_failed_trigger": "no_trigger_control",
        }
        annotation = case["annotation"]
        require(
            annotation["evaluation_group"] == expected_groups[annotation["expected_behavior"]],
            "Incorrect evaluation denominator group",
        )
        require(
            bool(annotation["acceptable_gap_concept_ids"])
            == (annotation["evaluation_group"] == "labeled_gap"),
            "Inconsistent gap annotation",
        )
    require(
        len(dataset["future_catalog_blueprints"]) == 6,
        "Missing future-catalog scenario definitions",
    )
    for path, field in [
        ("evaluation/scenarios.v1.json", "source_hash"),
        ("curriculum/catalog-slice.v1.json", "catalog_hash"),
        ("curriculum/model-config.v1.json", "model_config_hash"),
    ]:
        require(
            hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == split_manifest[field],
            "Evaluation artifact hash mismatch",
        )


def main():
    graph = load("curriculum/graph.v1.json")
    parents = validate_graph(graph)
    recursion = {
        "function_calls",
        "call_stack",
        "base_cases",
        "recursive_progress",
        "recursive_tracing",
    }
    require(
        not (ancestors("tabulation", parents) & recursion),
        "Tabulation must have an independent DP route",
    )
    require(
        "recursive_tracing" in ancestors("memoization", parents),
        "Top-down memoization needs tracing in this track",
    )
    catalog = load("curriculum/catalog-slice.v1.json")
    activities = validate_catalog(catalog, {c["id"] for c in graph["concepts"]})
    profiles = load("curriculum/profiles.v1.json")["profiles"]
    validate_profiles(profiles, activities)
    validate_scenarios(
        load("evaluation/scenarios.v1.json"), load("evaluation/manifest.v1.json"), activities
    )
    mira = next(p for p in profiles if p["profile_id"] == "demo_base_cases")
    used = {e["activity_id"] for e in mira["events"]}
    remaining = [
        a
        for a in activities.values()
        if a["primary_concept_id"] == "base_cases"
        and a["id"] not in used
        and a["kind"] == "question"
    ]
    require(
        Counter(a["role"] for a in remaining) == {"practice": 2, "reassessment": 1},
        "Fresh-item loop unavailable",
    )
    # Hand-calculated feasibility values, not production diagnosis/evaluation outputs.
    config = load("curriculum/model-config.v1.json")
    require(config["prior"] == {"successes": 2, "failures": 2}, "Prior differs from PROJECT policy")
    require(config["evidence"]["supported_minimum"] == 3, "Evidence gate differs from PROJECT")
    require(
        config["evidence"]["weak_below"] == {"numerator": 45, "denominator": 100},
        "Weak threshold differs from PROJECT",
    )
    require(
        config["evidence"]["ready_at_least"] == {"numerator": 65, "denominator": 100},
        "Readiness threshold differs from PROJECT",
    )
    require(
        [Fraction(s + 2, n + 4) for n, s in [(3, 0), (4, 1), (5, 2), (6, 3)]]
        == [Fraction(2, 7), Fraction(3, 8), Fraction(4, 9), Fraction(1, 2)],
        "Feasibility arithmetic drift",
    )
    require(load("contracts/release-manifest.json") == manifest(), "Release manifest hash mismatch")
    require(load("contracts/protocol-v1.schema.json") == protocol_schema(), "Protocol schema drift")
    legacy = json.dumps(
        load("backend/data/phase1.json"), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    require(
        hashlib.sha256(legacy).hexdigest()
        == "ae54153b27c8193429f7b704ae592cb4c5d23f86dec5cc551b018974db5522dd",
        "Published Phase 1 content changed",
    )
    print(
        "Phase 0 draft valid: 12 concepts/17 edges, 12 questions/2 lessons, 4 profiles; "
        "legacy unchanged."
    )


if __name__ == "__main__":
    main()
