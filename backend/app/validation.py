"""Validate relationships that the frozen structural schema cannot express."""

from fractions import Fraction

from app.replay import rounded


def validate_bundle(bundle, graph, activities, state):
    def require(value):
        if not value:
            raise ValueError("Inconsistent analysis response")

    estimates = {e.concept_id: e for e in bundle.estimates}
    require(len(estimates) == len(bundle.estimates) == len(graph.order))
    require(set(estimates) == set(graph.order))
    require(bundle.graded_events == list(state.graded))
    require(estimates == state.estimates)
    paths = graph.paths(bundle.focus_concept_id)
    for candidate in bundle.diagnosis.candidates:
        c = candidate.concept_id
        e = estimates[c]
        require(c in paths and candidate.path == list(paths[c]))
        require(candidate.distance == len(candidate.path) - 1)
        require(e.performance_state == "weak" and e.recent_failures >= 2)
        require(candidate.evidence_event_ids == e.evidence_event_ids)
        expected = (
            (1 - state.probabilities[c])
            * Fraction(1, candidate.distance + 1)
            * min(Fraction(e.eligible_count, 5), 1)
        )
        require(candidate.score == rounded(expected))
    ids = [i.activity_id for i in bundle.plan.items]
    require(len(ids) == len(set(ids)))
    positions = {c: i for i, c in enumerate(graph.order)}
    require(
        [positions[i.concept_id] for i in bundle.plan.items]
        == sorted(positions[i.concept_id] for i in bundle.plan.items)
    )
    used = {g.activity_id for g in state.graded if g.kind == "response"}
    for item in bundle.plan.items:
        activity = activities[item.activity_id]
        require(activity["active"] and activity["version"] == item.activity_version)
        require(activity["primary_concept_id"] == item.concept_id and activity["role"] == item.role)
        require(item.role == "lesson" or item.activity_id not in used)
        blockers = [
            p for p in graph.parents[item.concept_id] if estimates[p].performance_state != "ready"
        ]
        exempt = item.role == "lesson" or item.role == "diagnostic" and activity["foundational"]
        require(item.blocked_by_concept_ids == ([] if exempt else blockers))
        require(not item.blocked_by_concept_ids or item.readiness == "locked")
        require(all(d in ids[: ids.index(item.activity_id)] for d in item.depends_on_activity_ids))
    require(
        (bundle.plan.status == "ready")
        == any(i.role != "lesson" and i.readiness == "ready" for i in bundle.plan.items)
    )
