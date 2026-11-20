"""Pure authoritative grading and first-response evidence, without I/O or labels."""

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction

from app.contracts import ContractViolation, Estimate, GradedEvent


def rounded(value: Fraction) -> float:
    return round(float(value), 6)


@dataclass(frozen=True)
class Replay:
    events: tuple[dict, ...]
    graded: tuple[GradedEvent, ...]
    estimates: dict[str, Estimate]
    probabilities: dict[str, Fraction]


def replay(
    concepts, activities: dict, seed: list[dict], visitor: list[dict], config: dict
) -> Replay:
    """Streams are already structurally normalized; verify every catalog reference."""
    if len(seed) > 100 or len(visitor) > 200:
        raise ContractViolation("invalid_request")
    ids = [e["event_id"] for e in seed + visitor]
    if len(ids) != len(set(ids)):
        raise ContractViolation("event_conflict")
    attempts, graded = Counter(), []
    for index, event in enumerate(seed + visitor):
        activity = activities.get(event["activity_id"])
        if activity is None or not activity["active"]:
            raise ContractViolation("unknown_activity")
        if event["activity_version"] != activity["version"]:
            raise ContractViolation("version_mismatch")
        is_question = activity["kind"] == "question"
        if is_question != (event["kind"] == "response"):
            raise ContractViolation("invalid_response")
        attempts[activity["id"]] += 1
        attempt = attempts[activity["id"]]
        correct, explanation = None, None
        if is_question:
            option = event["response"]["option_id"]
            if option not in {o["id"] for o in activity["options"]}:
                raise ContractViolation("invalid_response")
            correct = option == activity["correct_option"]
            explanation = activity["explanation"]
            reason = (
                "repeat_activity"
                if attempt > 1
                else "hints_unknown"
                if event["hints_used"] is None
                else "hints_used"
                if event["hints_used"] > 0
                else "eligible"
            )
        else:
            reason = "lesson"
        graded.append(
            GradedEvent(
                event_id=event["event_id"],
                activity_id=activity["id"],
                activity_version=activity["version"],
                provenance="canonical_seed" if index < len(seed) else "visitor_demo",
                kind=event["kind"],
                concept_id=activity["primary_concept_id"],
                catalog_role=activity["role"],
                attempt_number=attempt,
                is_correct=correct,
                eligible=reason == "eligible",
                eligibility_reason=reason,
                occurred_at=event["occurred_at"],
                explanation=explanation,
            )
        )
    estimates, probabilities = {}, {}
    prior = config["prior"]
    policy = config["evidence"]
    weak = Fraction(**policy["weak_below"])
    ready = Fraction(**policy["ready_at_least"])
    for concept in sorted(concepts):
        responses = [g for g in graded if g.concept_id == concept and g.kind == "response"]
        evidence = [g for g in responses if g.eligible]
        n, s = len(evidence), sum(g.is_correct for g in evidence)
        probability = Fraction(s + prior["successes"], n + sum(prior.values()))
        probabilities[concept] = probability
        supported = n >= policy["supported_minimum"]
        state = (
            "unknown"
            if n == 0
            else "early"
            if not supported
            else "weak"
            if probability < weak
            else "ready"
            if probability >= ready
            else "developing"
        )
        estimates[concept] = Estimate(
            concept_id=concept,
            eligible_count=n,
            successes=s,
            total_attempts=len(responses),
            distinct_questions=len({g.activity_id for g in responses}),
            estimate=rounded(probability) if n else None,
            evidence_state="not_assessed"
            if not n
            else "supported_estimate"
            if supported
            else "early_estimate",
            performance_state=state,
            recent_failures=sum(not g.is_correct for g in evidence[-3:]),
            last_evidence_at=evidence[-1].occurred_at if evidence else None,
            evidence_event_ids=[g.event_id for g in evidence],
        )
    return Replay(tuple(seed + visitor), tuple(graded), estimates, probabilities)
