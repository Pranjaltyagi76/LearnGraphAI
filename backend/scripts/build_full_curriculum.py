"Build separately versioned original full-catalog inputs; never edit frozen slice files."

import argparse
import copy
import hashlib
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from app.contracts import canonical_json
from scripts.full_content import CONTENT

ROOT = Path(__file__).resolve().parents[2]
FULL_ID = "learngraph-full-v1"
FULL_MANIFEST = "contracts/releases/full-v1.json"
CATALOG_PATH = "curriculum/catalog-full.v1.json"
PROFILES_PATH = "curriculum/profiles-full.v1.json"


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def catalog():
    source = json.loads((ROOT / "curriculum/catalog-slice.v1.json").read_bytes())
    graph = json.loads((ROOT / "curriculum/graph.v1.json").read_bytes())
    activities = copy.deepcopy(source["activities"])
    provenance = {
        "origin": "original",
        "attribution": "LearnGraph AI project",
        "created_on": "2026-11-21",
        "license_status": "not_licensed",
    }
    for concept, content in CONTENT.items():
        for i, item in enumerate(content["questions"]):
            suffix = (
                "diagnostic_01" if i == 0 else "reassessment_01" if i == 5 else f"practice_{i:02}"
            )
            activities.append(
                {
                    "id": f"{concept}_{suffix}",
                    "version": 1,
                    "kind": "question",
                    "role": "diagnostic" if i == 0 else "reassessment" if i == 5 else "practice",
                    "primary_concept_id": concept,
                    "secondary_concept_ids": [],
                    "active": True,
                    "foundational": concept == "state_definition",
                    "difficulty": [0.2, 0.35, 0.45, 0.5, 0.6, 0.55][i],
                    "provenance": provenance,
                    "prompt": item["prompt"],
                    "code": item["code"],
                    "question_type": item["question_type"],
                    "options": [
                        {"id": chr(97 + j), "text": text} for j, text in enumerate(item["options"])
                    ],
                    "correct_option": chr(97 + item["correct"]),
                    "explanation": item["explanation"],
                }
            )
        activities.append(
            {
                "id": f"{concept}_lesson_01",
                "version": 1,
                "kind": "lesson",
                "role": "lesson",
                "primary_concept_id": concept,
                "secondary_concept_ids": [],
                "active": True,
                "foundational": concept == "state_definition",
                "difficulty": 0.2,
                "provenance": provenance,
                "title": content["title"],
                "body": content["body"],
            }
        )
    return {
        "catalog_version": "catalog-full-v1",
        "status": "engineering_reviewed_not_educator_validated",
        "target_question_count": 72,
        "question_count": 72,
        "lesson_count": 12,
        "covered_concept_ids": sorted(c["id"] for c in graph["concepts"]),
        "activities": activities,
    }


def profiles(full):
    original = json.loads((ROOT / "curriculum/profiles.v1.json").read_bytes())["profiles"]
    by_id = {a["id"]: a for a in full["activities"]}
    # Authored histories are product examples, never hidden evaluation labels.
    definitions = [
        (
            "demo_base_cases",
            "Mira",
            "target_gap",
            "base_cases",
            "Ready function calls with supported base-case weakness.",
            [("function_calls", [True] * 3), ("base_cases", [False] * 3)],
        ),
        (
            "demo_upstream",
            "Arjun",
            "upstream_gap",
            "memoization",
            (
                "Assessed DP dependencies with a supported overlapping-subproblem"
                "s gap and mixed memoization evidence."
            ),
            [
                ("function_calls", [True] * 3),
                ("call_stack", [True] * 3),
                ("base_cases", [True] * 3),
                ("recursive_progress", [True] * 3),
                ("recursive_tracing", [True] * 3),
                ("state_definition", [True] * 3),
                ("recurrence_relations", [True] * 3),
                ("overlapping_subproblems", [False] * 3),
                ("memoization", [True, False, True]),
            ],
        ),
        (
            "demo_sparse",
            "Leena",
            "sparse",
            "state_definition",
            (
                "One early state-definition observation; further assessment is ne"
                "eded, not a weakness label."
            ),
            [("state_definition", [True])],
        ),
        (
            "demo_ambiguous",
            "Kabir",
            "ambiguous",
            "tabulation",
            "Ready bottom-up dependencies with mixed tabulation evidence; no supported target gap.",
            [
                ("state_definition", [True] * 3),
                ("recurrence_relations", [True] * 3),
                ("state_transitions", [True] * 3),
                ("dp_base_cases", [True] * 3),
                ("tabulation", [True, False, True]),
            ],
        ),
    ]
    results = []
    for profile_id, name, archetype, focus, summary, observations in definitions:
        events = []
        run = str(uuid5(NAMESPACE_URL, f"{FULL_ID}:{profile_id}:seed-run"))
        for concept, outcomes in observations:
            for number, correct in enumerate(outcomes):
                suffix = "diagnostic_01" if number == 0 else f"practice_{number:02}"
                activity = by_id[f"{concept}_{suffix}"]
                option = (
                    activity["correct_option"]
                    if correct
                    else next(
                        o["id"]
                        for o in activity["options"]
                        if o["id"] != activity["correct_option"]
                    )
                )
                sequence = len(events) + 1
                events.append(
                    {
                        "schema_version": 1,
                        "kind": "response",
                        "event_id": str(uuid5(NAMESPACE_URL, f"{FULL_ID}:{profile_id}:{sequence}")),
                        "sequence_number": sequence,
                        "activity_id": activity["id"],
                        "activity_version": activity["version"],
                        "assessment_run_id": run,
                        "occurred_at": f"2026-11-20T08:{sequence:02}:00.000Z",
                        "response": {"option_id": option},
                        "hints_used": 0,
                        "time_spent_seconds": None,
                    }
                )
        old = next(p for p in original if p["profile_id"] == profile_id)
        results.append(
            {
                **{k: old[k] for k in ("synthetic",)},
                "profile_id": profile_id,
                "seed_id": f"{profile_id}_full_seed",
                "seed_version": 1,
                "name": name,
                "archetype": archetype,
                "summary": summary,
                "focus_concept_id": focus,
                "events": events,
            }
        )
    return {
        "profiles_version": "demo-profiles-full-v1",
        "status": "synthetic_engineering_reviewed",
        "profiles": results,
    }


def outputs():
    full = catalog()
    results = {CATALOG_PATH: encoded(full), PROFILES_PATH: encoded(profiles(full))}
    paths = [
        "curriculum/graph.v1.json",
        CATALOG_PATH,
        "curriculum/model-config.v1.json",
        PROFILES_PATH,
        "contracts/protocol-v1.schema.json",
    ]
    identity = {
        "contract_version": 1,
        "release_id": FULL_ID,
        "graph_version": "graph-v1",
        "catalog_version": "catalog-full-v1",
        "model_version": "baseline-v1",
        "profiles_version": "demo-profiles-full-v1",
        "scope": "full_twelve_concept_curriculum",
        "artifacts": [
            {
                "path": path,
                "sha256": hashlib.sha256(
                    results[path] if path in results else (ROOT / path).read_bytes()
                ).hexdigest(),
            }
            for path in paths
        ],
    }
    results[FULL_MANIFEST] = encoded(
        {
            "status": "reviewed_source_publication_is_separate",
            "identity": identity,
            "release_hash": hashlib.sha256(canonical_json(identity)).hexdigest(),
        }
    )
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Create missing draft artifacts only")
    args = parser.parse_args()
    for name, data in outputs().items():
        path = ROOT / name
        if path.exists():
            if path.read_bytes() != data:
                raise ValueError(f"Frozen full artifact differs: {name}")
        elif args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        else:
            raise ValueError(f"Missing full artifact: {name}")
    print(
        "Full curriculum: 72 questions, 12 lessons and four versioned synthetic histories verified."
    )


if __name__ == "__main__":
    main()
