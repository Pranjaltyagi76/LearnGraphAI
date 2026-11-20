"""Fixed evidence-grounded wording; no inference provider or causal claims."""

from app.contracts import AnalysisBundle

STATUS_TEXT = {
    "supported_gap": "Eligible responses support a suspected performance gap.",
    "insufficient_evidence": "More distinct unhinted responses are needed to assess this path.",
    "ambiguous": "The observed evidence is mixed or contradicts a consistent weakness.",
    "no_supported_gap": "The current evidence does not support a gap on this path.",
    "no_failed_trigger": (
        "No failed response for this focus was found; no failure diagnosis is made."
    ),
}


def explain(bundle: AnalysisBundle) -> list[str]:
    by_concept = {e.concept_id: e for e in bundle.estimates}
    lines = [STATUS_TEXT[bundle.diagnosis.status]]
    for candidate in bundle.diagnosis.candidates:
        e = by_concept[candidate.concept_id]
        lines.append(
            f"{candidate.concept_id}: {e.successes}/{e.eligible_count} eligible correct responses; "
            f"{e.recent_failures} failures among the latest three. "
            f"Path: {' → '.join(candidate.path)}. This is a hypothesis, not a causal conclusion."
        )
    for request in bundle.diagnosis.evidence_requests:
        lines.append(
            f"{request.concept_id}: {request.reason}; "
            f"{request.needed_observations} further eligible observations needed."
        )
    lines.append(
        f"Next plan: {bundle.plan.mode}; {bundle.plan.status}. "
        "Locked items require new evidence or fresh same-run practice."
    )
    lines.append("Estimates describe observed correctness, not proven mastery or learning gain.")
    return lines
