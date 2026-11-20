"""Independent output invariants. Never call the plan constructor to check itself."""

from fractions import Fraction


def audit_plan(graph, activities, state, plan, truth: list[str]) -> dict:
    seen = {g.activity_id for g in state.graded if g.kind == "response"}
    ids = [i.activity_id for i in plan.items]
    issues, catalog_ok, prereq_ok, reassess_ok, reassess_count = [], 0, 0, 0, 0
    checks, repeats, difficulty_fits = 0, 0, []
    positions = {c: index for index, c in enumerate(graph.order)}
    # Validate partial order, including transitive ancestors whose intermediate item is absent.
    for left_index, left in enumerate(plan.items):
        ancestors = graph.paths(left.concept_id)
        if any(
            right.concept_id != left.concept_id and right.concept_id in ancestors
            for right in plan.items[left_index + 1 :]
        ):
            issues.append("prerequisite_order")
    if len(ids) != len(set(ids)) or len(ids) > 5:
        issues.append("duplicate_or_oversized_plan")
    for item in plan.items:
        activity = activities.get(item.activity_id)
        valid = bool(
            activity
            and activity["active"]
            and activity["version"] == item.activity_version
            and activity["primary_concept_id"] == item.concept_id
            and activity["role"] == item.role
        )
        catalog_ok += valid
        if not valid:
            issues.append("invalid_catalog_reference")
            continue
        checks += 1
        blockers = sorted(
            p
            for p in graph.parents[item.concept_id]
            if state.estimates[p].performance_state != "ready"
        )
        exempt = item.role == "lesson" or item.role == "diagnostic" and activity["foundational"]
        expected = [] if exempt else blockers
        correct_lock = item.blocked_by_concept_ids == expected and (
            not expected or item.readiness == "locked"
        )
        prereq_ok += correct_lock
        if not correct_lock:
            issues.append("invalid_prerequisite_lock")
        if item.role != "lesson":
            repeats += item.activity_id in seen
            if item.activity_id in seen:
                issues.append("repeated_question")
        for dependency in item.depends_on_activity_ids:
            if dependency not in ids[: ids.index(item.activity_id)]:
                issues.append("missing_or_later_dependency")
            elif activities[dependency]["primary_concept_id"] != item.concept_id:
                issues.append("cross_concept_dependency")
        if item.role == "reassessment":
            reassess_count += 1
            reassess_ok += item.activity_id not in seen and activity["role"] == "reassessment"
        desired = (
            Fraction(1, 5)
            if not state.estimates[item.concept_id].eligible_count
            else min(Fraction(4, 5), max(Fraction(1, 5), state.probabilities[item.concept_id]))
        )
        difficulty_fits.append(float(1 - abs(Fraction(str(activity["difficulty"])) - desired)))
    ready_question = any(i.role != "lesson" and i.readiness == "ready" for i in plan.items)
    if (plan.status == "ready") != ready_question:
        issues.append("incorrect_ready_status")
    emitted_concepts = [positions[i.concept_id] for i in plan.items]
    return {
        "emitted_items": len(ids),
        "catalog_valid_items": catalog_ok,
        "prerequisite_checks": checks,
        "valid_prerequisite_checks": prereq_ok,
        "reassessment_items": reassess_count,
        "distinct_reassessment_items": reassess_ok,
        "repeated_questions": repeats,
        "difficulty_fits": difficulty_fits,
        "labeled_gaps": len(truth),
        "covered_gaps": len(
            set(truth) & {i.concept_id for i in plan.items if i.reason == "gap_practice"}
        ),
        "concept_topological_positions": emitted_concepts,
        "prerequisite_plan_valid": (
            prereq_ok == checks
            and catalog_ok == len(ids)
            and not set(issues)
            & {
                "prerequisite_order",
                "invalid_prerequisite_lock",
                "missing_or_later_dependency",
                "cross_concept_dependency",
            }
        ),
        "issues": sorted(set(issues)),
    }
