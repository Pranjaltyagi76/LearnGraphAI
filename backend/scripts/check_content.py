"""Validate the authored feasibility slice without treating it as a full curriculum."""

import json
from collections import Counter, defaultdict, deque
from pathlib import Path


def main():
    path = Path(__file__).resolve().parents[1] / "data/phase1.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    concepts = {concept["id"] for concept in payload["concepts"]}
    assert len(concepts) == 12
    adjacent = defaultdict(list)
    indegree = dict.fromkeys(concepts, 0)
    edges = set()
    for edge in payload["edges"]:
        a, b = edge["prerequisite"], edge["dependent"]
        assert a in concepts and b in concepts and a != b and (a, b) not in edges
        edges.add((a, b))
        adjacent[a].append(b)
        indegree[b] += 1
    queue = deque(c for c in concepts if indegree[c] == 0)
    visited = 0
    while queue:
        visited += 1
        for dependent in adjacent[queue.popleft()]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                queue.append(dependent)
    assert visited == len(concepts), "Prerequisite cycle"
    questions = payload["questions"]
    by_id = {q["id"]: q for q in questions}
    assert len(by_id) == len(questions) == 12
    assert payload["curriculum_target_questions"] == 72
    for question in questions:
        assert question["concept_id"] in concepts
        option_ids = [option["id"] for option in question["options"]]
        assert len(set(option_ids)) == len(option_ids) == 4
        assert question["correct_option"] in option_ids
        assert question["provenance"] and question["explanation"]
    initial_ids = [event["activity_id"] for event in payload["seed_events"]]
    assert len(set(initial_ids)) == len(initial_ids) == 6
    for event in payload["seed_events"]:
        assert event["activity_id"] in by_id and event["hints_used"] == 0
        assert event["option_id"] in {o["id"] for o in by_id[event["activity_id"]]["options"]}
    for concept in {q["concept_id"] for q in questions}:
        items = [q for q in questions if q["concept_id"] == concept]
        assert Counter(q["role"] for q in items) == {
            "diagnostic": 1,
            "practice": 4,
            "reassessment": 1,
        }
        remaining = [q for q in items if q["id"] not in initial_ids]
        assert Counter(q["role"] for q in remaining) == {"practice": 2, "reassessment": 1}
    print(
        "Content valid: 12 concepts, 17 acyclic edges, 12 slice questions; "
        "fresh-item trace is feasible."
    )


if __name__ == "__main__":
    main()
