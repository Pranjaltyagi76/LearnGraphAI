# Benchmark and model-quality protocol

**State:** Model-quality protocol only; the authored Phase 1 content fixture exists, but no prediction/diagnosis/recommendation benchmark has run. **Baseline date:** 20 November 2026. **Owner requirements:** FR-08–12/18 and NFR-09 in [requirement.md](../requirement.md). Algorithms and initial thresholds remain in [PROJECT.md](../PROJECT.md), Section 8.

Benchmark quality here means prediction/diagnosis/recommendation behavior. Runtime latency/resource tests belong in [performance_review.md](performance_review.md). Neither procedure establishes real learning gains from synthetic outcomes.

## 1. Questions to answer

1. Does per-concept smoothing predict held-out next responses better or worse than a training-only global correctness baseline?
2. Does prerequisite-aware ranking find independently labeled gaps, and when does it abstain?
3. Are plans valid, ordered, and able to gather missing evidence without blaming unknown skills?
4. Do retries, hints, sparse histories, misleading tags, and generator changes expose systematic failures?
5. Can a profile actually complete fresh practice and distinct reassessment under the content/evidence budget?

Question 5 led to the resolved 72-question budget decision OPEN-01 in [phasewise_roadmap.md](phasewise_roadmap.md). The authored slice proves remaining-item availability; a complete live-loop benchmark still needs the actual algorithm and full content.

## 2. Dataset separation

| Artifact | Purpose | Guardrail |
| --- | --- | --- |
| Four public demo profiles | Inspectable product examples | Not an independent hidden test set; do not tune and report on them as if unseen. |
| Training synthetic learners | Fit training-only aggregate rates and any later model parameters | No validation/test events or oracle diagnosis labels used as inference features. |
| Development learners/scenarios | Tune heuristic thresholds/weights and inspect failures | Never relabel them as untouched test evidence. |
| Frozen test learners/scenarios | Final reported evaluation | Freeze before tuning; log changes if the holdout is exposed/replaced. |
| Hand-authored holdout and generator variants | Stress independence from generator assumptions | Labels defined independently of production ranking; different seeds alone do not ensure independence. |
| Later EdNet subset | Separate P2 knowledge-tracing study | Appropriate license/subset manifest, different domain claims, no raw records in runtime/Git. |

Use learner-disjoint train/development/test splits; record actual counts, grouping, seeds, generator version, and hashes. Choose feasible sample sizes in Phase 0 after local resource/content constraints are known. There is no fabricated large dataset size or ratio in this document.

The application catalog is small. Repeated generated responses to the same question do not create new distinct observations. Synthetic benchmark sequences must obey the deployed evidence rules. Any separate larger research item pool must be disclosed and must not be presented as evidence that the small product catalog is sufficient.

## 3. Required scenario families

- Supported prerequisite weakness with independent qualifying evidence and a visible upstream path.
- Target-skill weakness with secure assessed prerequisites.
- No observations and early observations, including unknown prerequisites.
- Ambiguous/mixed or contradictory evidence and ordinary slip/guess behavior.
- Hinted first response, unknown hints, unhinted retry after hints, repeated correct response, and lesson completion.
- Multi-tag items where only the primary concept receives evidence.
- Different question difficulty/context, misleading tags, and graph-edge perturbations.
- Duplicate identical event, conflicting reuse, malformed option/version, invalid order, and boundary payload/history sizes.
- Tied ranks, no suitable activity, exhausted catalog, prerequisite locks, and different reassessment IDs.
- Fresh-item feasibility traces before and after remediation, including unchanged or worse estimates.

Specify expected behavior without reading outputs from the implementation being tested. Trusted labels may be planted simulator state or reviewed scenario annotations, with their provenance disclosed. Never feed those hidden labels or synthetic `error_type` truth into the diagnosis engine.

## 4. Next-response prediction protocol

For each held-out learner in chronological order:

1. Initialize the per-learner estimator from its declared prior. Do not start from the final history or an already summarized demo profile.
2. Before each eligible event, calculate `p(correct)` from that learner's earlier prefix and frozen global configuration.
3. Record probability/outcome and activity/learner identifiers for aggregate scoring.
4. Observe/grade the response and update eligibility/state afterward.
5. Skip noneligible events from the primary prediction denominator while still replaying their appropriate context. Report exclusions by reason.

The baseline uses only first responses to distinct primary-concept questions with known zero hints. Retry/hint robustness reports may use other denominators but must label them separately. Item reuse across learner splits must be disclosed; item-held-out claims require a separate valid split.

### P0 prediction baselines

- **Global rate:** One smoothed correctness rate fit on eligible training events only, frozen before evaluation.
- **Concept baseline:** The versioned `(successes + 2) / (eligible_count + 4)` per learner/concept estimate, with the test learner updated only from its own preceding observations.

Report log loss and Brier score as primary measures. Record a small numerical clipping epsilon for log loss (proposed `1e-15`) without changing the estimator itself. ROC-AUC and PR-AUC require meaningful class support; otherwise report `N/A` and explain. Accuracy, if included, states its decision threshold and is secondary.

## 5. Diagnosis evaluation

Evaluate retrospective diagnosis at a defined failed-target trigger; the just-observed failed answer may be used here. This differs from next-response prediction.

Compare a lowest-estimate comparator and the prerequisite-aware heuristic. Declare each candidate universe explicitly. For a controlled ablation, use the same target-plus-bounded-ancestor universe/evidence eligibility and remove graph relevance from scoring; a whole-curriculum lowest-estimate baseline may be reported separately as a different information policy.

For cases with a nonempty independently labeled gap set `G` and returned top list `P` truncated at `K`:

- Precision@K uses `|P ∩ G| / |P|`; if the model abstains/returns no candidates, assign zero for that labeled-gap case in the all-case aggregate. State this returned-list denominator rather than implying a fixed-K definition.
- Recall@K uses `|P ∩ G| / |G|`; an abstention contributes zero.
- MRR is the reciprocal rank of the first acceptable labeled gap, or zero when absent/abstained.
- Top-1 accuracy is reported on single-gap cases unless an explicit multi-label correctness rule is stated.
- Report `K` (normally 1 and 3 for this API), all-case sample counts, per-scenario results, and evidence eligibility.

No-gap cases have no recall denominator: report false diagnosis rate and appropriate abstention/no-gap behavior separately. Track overall answer coverage/abstention rate and error among answered cases alongside all-case metrics, so selective abstention cannot inflate quality invisibly. Separate missing-evidence cases from confident false diagnoses.

Heuristic ranking/evidence-strength is not a causal probability. Do not publish probabilistic diagnosis calibration without a separately defined target and enough independent labeled data.

## 6. Recommendation evaluation

Compare fixed-seed random eligible selection, lowest-estimate-first, and prerequisite-aware ranking. Use the same catalog, information prefix, and hard readiness/validity constraints for controlled ranking comparisons; disclose any broader policy comparison separately.

| Measure | Definition |
| --- | --- |
| Catalog validity | Fraction of emitted item references that exist, are active, and match the requested catalog version. |
| Prerequisite validity | Fraction of emitted plans satisfying required ordering/readiness/locks; pending assessment is not counted as proven readiness. |
| Gap coverage | Relevant labeled target gaps covered by appropriate plan items, with denominator and assessment-versus-remediation mode stated. |
| Repetition | Reused/immediate-repeat question frequency; intentional review reported separately from fresh assessment. |
| Reassessment distinctness | Fraction of claimed fresh reassessments using an unseen different same-primary-skill item. |
| Exhaustion honesty | Exhausted/no-suitable-item cases return the documented state without fabricated IDs/evidence. |
| Difficulty fit | Fit to the authored ordinal difficulty policy; not measured item difficulty or expected learning gain. |

Ranking relevance metrics require independent relevance labels. Do not infer real learning gain from the recommendation score or simulator rewards generated by the same ranking rule.

## 7. Reproducibility and uncertainty

Proposed result artifacts (not existing files):

```text
evaluation/manifests/<run_id>.json
evaluation/results/<run_id>/metrics.json
evaluation/results/<run_id>/report.md
evaluation/results/<run_id>/plots/
```

Manifest fields must include commit, dirty/clean tree state, generator/scenario versions and hashes, seed(s), exact environment/packages, split counts/hash, model/config/graph/catalog versions, eligibility/exclusion counts, metric definitions, execution command, and result hashes. Record run timestamp separately from deterministic input identity.

Use repeated seeds or learner-level bootstrap intervals only where sample size supports them. State method, resampling unit, repeats, and confidence level. Do not bootstrap individual correlated events as if independent learners or imply certainty from tiny synthetic samples.

Avoid committing raw large sequences or private records. Small aggregate metrics and authored independent fixtures are suitable. No benchmark runner/package command exists yet; add a verified command when implemented instead of publishing an imaginary runnable example.

## 8. Release policy

- Functional invariants such as valid catalog references, no duplicate evidence, correct version/order handling, and no future-answer leakage must pass.
- Predictive quality has no invented target score or required percentage gain. Publish the actual baseline comparison, including worse results.
- Failures and undefined metrics remain visible with counts/reasons; do not remove difficult cases to improve the headline.
- Synthetic results are limited to the tested assumptions. Distinct real-world learning-gain claims require a later suitable study.
- BKT/DKT/EdNet and optional wording experiments are P2 and cannot block or substitute for honest P0 evaluation.

## 9. Current results

| Evaluation | State | Result |
| --- | --- | --- |
| Prediction baselines | Not implemented/run | Not measured. |
| Diagnosis holdout | Not authored/run | Not measured. |
| Recommendation comparisons | Not implemented/run | Not measured. |
| Fresh practice/reassessment feasibility | OPEN-01 budget resolved; authored-slice test passes | Full catalog/live-loop evidence pending. |
| Robustness/leakage checks | Not implemented/run | No passing claim. |
| Real learning benefit | No study | No claim. |

Future entries must link actual run artifacts/commits and record failed as well as passing results.
