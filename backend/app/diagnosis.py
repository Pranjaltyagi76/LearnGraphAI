"""Bounded evidence-gated diagnosis; no scenario annotations or wall clock."""

from fractions import Fraction

from app.contracts import ContractViolation, Diagnosis, EvidenceRequest, GapCandidate
from app.graph import Graph
from app.replay import Replay, rounded


def diagnose(
    graph: Graph,
    state: Replay,
    focus: str,
    trigger_id: str | None,
    config: dict,
    *,
    baseline: str = "prerequisite_aware",
) -> Diagnosis:
    if baseline not in {"lowest_estimate", "prerequisite_aware"}:
        raise ValueError("Unknown diagnosis comparator")
    if focus not in graph.parents:
        raise ContractViolation("invalid_request")
    failed = [g for g in state.graded if g.concept_id == focus and g.is_correct is False]
    trigger = (
        next((g for g in failed if g.event_id == trigger_id), None)
        if trigger_id
        else (failed[-1] if failed else None)
    )
    if trigger_id and trigger is None:
        raise ContractViolation("invalid_trigger")
    policy = config["diagnosis"]
    paths = graph.paths(focus, policy["maximum_depth"])
    requests, qualifying = [], []
    for concept in graph.order:
        if concept not in paths:
            continue
        estimate = state.estimates[concept]
        if estimate.evidence_state != "supported_estimate":
            requests.append(
                EvidenceRequest(
                    concept_id=concept,
                    reason=estimate.evidence_state,
                    needed_observations=config["evidence"]["supported_minimum"]
                    - estimate.eligible_count,
                )
            )
        if (
            trigger
            and estimate.performance_state == "weak"
            and estimate.recent_failures >= policy["minimum_recent_failures"]
        ):
            distance = len(paths[concept]) - 1
            weakness = 1 - state.probabilities[concept]
            strength = min(
                Fraction(estimate.eligible_count, policy["evidence_strength_saturation"]), 1
            )
            recurrence = min(Fraction(estimate.recent_failures, policy["recurrence_saturation"]), 1)
            score = weakness * Fraction(1, distance + 1) * strength * recurrence
            rank = weakness if baseline == "lowest_estimate" else score
            qualifying.append((-rank, distance, concept, score))
    candidates = [
        GapCandidate(
            concept_id=c,
            relation="target" if c == focus else "upstream",
            distance=d,
            path=list(paths[c]),
            score=rounded(score),
            evidence_event_ids=state.estimates[c].evidence_event_ids,
            reason="supported_target_weakness" if c == focus else "supported_upstream_weakness",
        )
        for _, d, c, score in sorted(qualifying)[: policy["maximum_candidates"]]
    ]
    mixed = any(
        state.estimates[c].performance_state == "developing"
        or (
            state.estimates[c].performance_state == "weak"
            and state.estimates[c].recent_failures < policy["minimum_recent_failures"]
        )
        for c in paths
    )
    status = (
        "no_failed_trigger"
        if trigger is None
        else "supported_gap"
        if candidates
        else "insufficient_evidence"
        if requests
        else "ambiguous"
        if mixed
        else "no_supported_gap"
    )
    alternatives = ["item_difficulty", "response_error", "tag_mismatch"] if trigger else []
    if trigger and mixed:
        alternatives.append("mixed_evidence")
    return Diagnosis(
        status=status,
        trigger_event_id=trigger.event_id if trigger else None,
        candidates=candidates,
        evidence_requests=requests,
        alternatives=alternatives,
    )
