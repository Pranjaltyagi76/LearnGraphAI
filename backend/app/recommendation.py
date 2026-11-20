"""Constrained plan construction. Comparators share the same hard constraints."""

from fractions import Fraction
from random import Random

from app.contracts import Diagnosis, Plan, PlanItem
from app.graph import Graph
from app.replay import Replay, rounded


def cycle_anchor(state: Replay, concept: str, run_id: str | None) -> str | None:
    """Use a prior anchor when entering a run; failed practice never restarts a cycle."""
    first_current = next(
        (i for i, e in enumerate(state.events) if e["assessment_run_id"] == run_id),
        len(state.events),
    )
    anchors = [
        (i, e, g)
        for i, (e, g) in enumerate(zip(state.events, state.graded, strict=True))
        if g.concept_id == concept and (g.is_correct is False or g.catalog_role == "diagnostic")
    ]
    previous = [g for i, _, g in anchors if i < first_current]
    if previous:
        return previous[-1].event_id
    current = [g for _, e, g in anchors if e["assessment_run_id"] == run_id]
    return current[0].event_id if current else None


def cycle_practices(state: Replay, concept: str, run_id: str, anchor_id: str | None) -> list[str]:
    """Fresh same-run practice after the anchor; correctness is not a workflow gate."""
    ids = [e["event_id"] for e in state.events]
    anchor = ids.index(anchor_id) if anchor_id in ids else -1
    return [
        g.activity_id
        for i, (e, g) in enumerate(zip(state.events, state.graded, strict=True))
        if i > anchor
        and e["assessment_run_id"] == run_id
        and g.concept_id == concept
        and g.catalog_role == "practice"
        and g.attempt_number == 1
    ]


def completed_cycles(state: Replay) -> list[dict]:
    """Report observed workflow only, not adherence, verified receipts, or learning."""
    result = []
    for index, (event, grade) in enumerate(zip(state.events, state.graded, strict=True)):
        if grade.catalog_role != "reassessment" or grade.attempt_number != 1:
            continue
        prefix = Replay(
            state.events[:index], state.graded[:index], state.estimates, state.probabilities
        )
        anchor = cycle_anchor(prefix, grade.concept_id, event["assessment_run_id"])
        if anchor is None:
            continue
        practices = cycle_practices(prefix, grade.concept_id, event["assessment_run_id"], anchor)
        if practices:
            result.append(
                {
                    "reassessment_event_id": grade.event_id,
                    "anchor_event_id": anchor,
                    "practice_activity_ids": practices,
                    "concept_id": grade.concept_id,
                }
            )
    return result


def activity_score(activity, state: Replay, selected: set, needed_parents: set, config: dict):
    concept = activity["primary_concept_id"]
    policy = config["plan"]
    desired = (
        Fraction(**policy["desired_difficulty_unknown"])
        if not (state.estimates[concept].eligible_count)
        else min(
            Fraction(**policy["difficulty_clip_max"]),
            max(Fraction(**policy["difficulty_clip_min"]), state.probabilities[concept]),
        )
    )
    seen = {e["activity_id"] for e in state.events}
    recent = {e["activity_id"] for e in state.events[-policy["recent_repeat_window"] :]}
    factors = {
        "gap_match": int(concept in selected),
        "prerequisite_coverage": int(concept in needed_parents),
        "difficulty_fit": 1 - abs(Fraction(str(activity["difficulty"])) - desired),
        "novelty": int(activity["id"] not in seen),
        "recent_repeat": int(activity["id"] in recent),
    }
    return sum(Fraction(**weight) * factors[key] for key, weight in policy["weights"].items())


def make_plan(
    graph: Graph,
    activities: dict,
    state: Replay,
    focus: str,
    diagnosis: Diagnosis,
    config: dict,
    *,
    baseline: str = "prerequisite_aware",
    random_seed: int = 761120,
) -> Plan:
    if baseline not in {"prerequisite_aware", "lowest_estimate", "random_eligible"}:
        raise ValueError("Unknown recommendation comparator")
    paths = graph.paths(focus)
    gaps = {c.concept_id for c in diagnosis.candidates}
    missing = {r.concept_id for r in diagnosis.evidence_requests}
    mode = "remediation" if gaps else "assessment" if missing else "practice"
    selected = gaps | missing if gaps else missing or {focus}
    # Only the bounded universe is considered; outside parents remain explicit locks.
    for concept in tuple(selected):
        selected.update(
            c
            for c in paths
            if c in graph.paths(concept) and state.estimates[c].performance_state != "ready"
        )
    needed_parents = set(paths) - {focus}
    seen_questions = {g.activity_id for g in state.graded if g.kind == "response"}
    run_id = (
        state.events[-1]["assessment_run_id"]
        if state.events and state.graded[-1].provenance == "visitor_demo"
        else None
    )
    completed_lessons = {
        e["activity_id"]
        for e in state.events
        if e["kind"] == "lesson_completed" and e["assessment_run_id"] == run_id
    }
    rng = Random(random_seed)
    random_ranks = {a: rng.random() for a in sorted(activities)}

    def rank(activity):
        score = activity_score(activity, state, selected, needed_parents, config)
        if baseline == "random_eligible":
            return random_ranks[activity["id"]], activity["id"]
        return -score, activity["id"]

    order = list(graph.order)
    if baseline != "prerequisite_aware":
        # Comparator concept priorities vary only among currently available DAG nodes.
        remaining, order = set(graph.order), []
        random_concepts = {c: rng.random() for c in sorted(remaining)}
        while remaining:
            available = [c for c in remaining if not set(graph.parents[c]) & remaining]
            concept = min(
                available,
                key=lambda c: (
                    random_concepts[c] if baseline == "random_eligible" else state.probabilities[c],
                    c,
                ),
            )
            order.append(concept)
            remaining.remove(concept)
    items, empty_states = [], []
    for concept in order:
        if concept not in selected:
            continue
        catalog = [
            a for a in activities.values() if a["primary_concept_id"] == concept and a["active"]
        ]
        questions = [a for a in catalog if a["kind"] == "question"]
        fresh = [a for a in questions if a["id"] not in seen_questions]
        blockers = [
            p for p in graph.parents[concept] if state.estimates[p].performance_state != "ready"
        ]
        gather = concept in missing
        stages = []
        if gather:
            diagnostic = sorted((a for a in fresh if a["role"] == "diagnostic"), key=rank)[:1]
            practice = sorted((a for a in fresh if a["role"] == "practice"), key=rank)
            needed = (
                config["evidence"]["supported_minimum"] - state.estimates[concept].eligible_count
            )
            stages = [
                (a, "gather_evidence", [])
                for a in diagnostic + practice[: min(2, needed - len(diagnostic))]
            ]
            pool = [a for a in questions if a["role"] in {"diagnostic", "practice"}]
        else:
            lessons = sorted(
                (a for a in catalog if a["kind"] == "lesson" and a["id"] not in completed_lessons),
                key=rank,
            )[:1]
            practice = sorted((a for a in fresh if a["role"] == "practice"), key=rank)[:2]
            reassess = sorted((a for a in fresh if a["role"] == "reassessment"), key=rank)[:1]
            stages = [(a, "lesson_support", []) for a in lessons]
            stages += [
                (a, "gap_practice" if mode == "remediation" else "further_practice", [])
                for a in practice
            ]
            anchor = cycle_anchor(state, concept, run_id)
            practiced = cycle_practices(state, concept, run_id, anchor) if run_id and anchor else []
            dependencies = [] if practiced else [a["id"] for a in practice[:1]]
            # With no anchor or no available/observed practice, reassessment stays locked.
            for a in reassess:
                stages.append((a, "reassessment", dependencies))
            pool = [a for a in questions if a["role"] in {"practice", "reassessment"}]
        if not any(a["kind"] == "question" for a, _, _ in stages):
            empty_states.append("catalog_exhausted" if pool else "no_suitable_activity")
        for activity, reason, dependencies in stages:
            if len(items) >= config["plan"]["maximum_items"]:
                break
            role = activity["role"]
            parents = (
                []
                if role == "lesson" or (role == "diagnostic" and activity["foundational"])
                else blockers
            )
            workflow_locked = role == "reassessment" and (not anchor or not practiced)
            items.append(
                PlanItem(
                    activity_id=activity["id"],
                    activity_version=activity["version"],
                    concept_id=concept,
                    role=role,
                    readiness="locked" if parents or workflow_locked else "ready",
                    blocked_by_concept_ids=parents,
                    depends_on_activity_ids=dependencies,
                    reason=reason,
                    score=rounded(
                        activity_score(activity, state, selected, needed_parents, config)
                    ),
                )
            )
    has_question = any(i.role != "lesson" for i in items)
    status = (
        "ready"
        if any(i.role != "lesson" and i.readiness == "ready" for i in items)
        else (
            "blocked"
            if has_question
            else "catalog_exhausted"
            if "catalog_exhausted" in empty_states
            else "no_suitable_activity"
        )
    )
    return Plan(mode=mode, status=status, items=items)
