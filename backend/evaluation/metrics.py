"""Small dependency-free metrics with explicit denominators and tie handling."""

from math import fsum, log


def ratio(numerator: int | float, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def prediction_metrics(rows: list[dict], excluded: int) -> dict:
    probabilities = [r["probability"] for r in rows]
    outcomes = [r["outcome"] for r in rows]
    positives, negatives = sum(outcomes), len(outcomes) - sum(outcomes)
    clipped = [min(1 - 1e-15, max(1e-15, p)) for p in probabilities]
    loss = -fsum(y * log(p) + (1 - y) * log(1 - p) for p, y in zip(clipped, outcomes, strict=True))
    brier = fsum((p - y) ** 2 for p, y in zip(probabilities, outcomes, strict=True))
    auc, ap = None, None
    if positives and negatives:
        positive_scores = [p for p, y in zip(probabilities, outcomes, strict=True) if y]
        negative_scores = [p for p, y in zip(probabilities, outcomes, strict=True) if not y]
        auc = fsum(
            1 if a > b else 0.5 if a == b else 0 for a in positive_scores for b in negative_scores
        ) / (positives * negatives)
        seen, true, ap = 0, 0, 0.0
        for threshold in sorted(set(probabilities), reverse=True):
            indices = [i for i, p in enumerate(probabilities) if p == threshold]
            increment = sum(outcomes[i] for i in indices)
            seen += len(indices)
            true += increment
            ap += (increment / positives) * (true / seen)
    return {
        "eligible_predictions": len(rows),
        "positive_outcomes": positives,
        "negative_outcomes": negatives,
        "excluded_events": excluded,
        "log_loss": ratio(loss, len(rows)),
        "brier": ratio(brier, len(rows)),
        "roc_auc": auc,
        "pr_auc": ap,
    }


def diagnosis_metrics(rows: list[dict]) -> tuple[dict, dict]:
    labeled = [r for r in rows if r["group"] == "labeled_gap"]
    no_gap = [r for r in rows if r["group"] == "no_gap_control"]
    metrics = {
        "labeled_gap_cases": len(labeled),
        "all_cases": len(rows),
        "no_gap_cases": len(no_gap),
        "missing_evidence_cases": sum(r["group"] == "missing_evidence" for r in rows),
        "no_trigger_cases": sum(r["group"] == "no_trigger_control" for r in rows),
        "coverage": ratio(sum(bool(r["returned"]) for r in rows), len(rows)),
        "false_diagnosis_rate": ratio(sum(bool(r["returned"]) for r in no_gap), len(no_gap)),
    }
    for k in (1, 3):
        precision, recall = [], []
        for row in labeled:
            returned, truth = row["returned"][:k], set(row["truth"])
            hits = len(set(returned) & truth)
            precision.append(hits / len(returned) if returned else 0)
            recall.append(hits / len(truth))
        metrics[f"precision_at_{k}"] = ratio(fsum(precision), len(labeled))
        metrics[f"recall_at_{k}"] = ratio(fsum(recall), len(labeled))
    reciprocal = [
        next((1 / i for i, c in enumerate(r["returned"], 1) if c in r["truth"]), 0) for r in labeled
    ]
    metrics["mrr"] = ratio(fsum(reciprocal), len(labeled))
    single = [r for r in labeled if len(r["truth"]) == 1]
    answered_controls = [r for r in rows if r["returned"] and r["group"] != "no_trigger_control"]
    extras = {
        "single_gap_cases": len(single),
        "single_gap_top_1": ratio(
            sum(bool(r["returned"]) and r["returned"][0] in r["truth"] for r in single), len(single)
        ),
        "answered_cases_excluding_no_trigger": len(answered_controls),
        "top_1_error_among_answered": ratio(
            sum(r["returned"][0] not in r["truth"] for r in answered_controls),
            len(answered_controls),
        ),
        "abstention_rate": ratio(sum(not r["returned"] for r in rows), len(rows)),
    }
    return metrics, extras
