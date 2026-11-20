# Benchmark and model-quality protocol

**State:** Phase 2 deterministic engine and evaluator implemented; frozen development/public synthetic audit measured and reproducible. **Baseline date:** 20 November 2026. **Owner requirements:** FR-08–12/18 and NFR-09 in [requirement.md](../requirement.md). Algorithms and initial thresholds remain in [PROJECT.md](../PROJECT.md), Section 8.

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

The initial [frozen packet](../evaluation/readme.md) has 4 training, 8 development and 12 public synthetic audit learners, with disjoint learner/group IDs, no identical cross-split observation pattern, separate annotations and hashed manifests. Random eligible comparator seed is 761120. Public demo seeds are excluded. These authored cases were visible during engineering review: they are not blind or evidence of real-world generalization. Any output-guided tuning requires a newly versioned independent final audit; never relabel exposed cases as untouched. Items and broad families are reused across splits and explicitly disclosed. Six future-catalog/fixture-DAG blueprints are not metric observations.

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

Report log loss and Brier as primary measures; metric-only clipping epsilon is frozen at `1e-15`. ROC-AUC uses pairwise ranking with half credit for ties; the public pr_auc field reports stepwise average precision, grouping equal scores, not trapezoidal interpolation. Both require positive and negative outcomes, otherwise null with an explanation. Report class/exclusion counts. Optional accuracy uses threshold 0.5 and remains secondary.

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

The measured artifacts are under [evaluation/results/phase2-v2](../evaluation/results/phase2-v2/manifest.json); this is the general layout for future runs:

```text
evaluation/manifests/<run_id>.json
evaluation/results/<run_id>/metrics.json
evaluation/results/<run_id>/report.md
evaluation/results/<run_id>/plots/
```

Manifest fields must include commit, dirty/clean tree state, generator/scenario versions and hashes, seed(s), exact environment/packages, split counts/hash, model/config/graph/catalog versions, eligibility/exclusion counts, metric definitions, execution command, and result hashes. Record run timestamp separately from deterministic input identity.

Use repeated seeds or learner-level bootstrap intervals only where sample size supports them. State method, resampling unit, repeats, and confidence level. Do not bootstrap individual correlated events as if independent learners or imply certainty from tiny synthetic samples.

Avoid committing raw large sequences or private records. Small aggregate metrics and authored independent fixtures are suitable. From backend/, `python -m scripts.evaluate --check ../evaluation/results/phase2-v2` verifies the measured source/input hashes and reproduces exact outputs. Use --output with a new directory for a new immutable run.

## 8. Release policy

- Functional invariants such as valid catalog references, no duplicate evidence, correct version/order handling, and no future-answer leakage must pass.
- Predictive quality has no invented target score or required percentage gain. Publish the actual baseline comparison, including worse results.
- Failures and undefined metrics remain visible with counts/reasons; do not remove difficult cases to improve the headline.
- Synthetic results are limited to the tested assumptions. Distinct real-world learning-gain claims require a later suitable study.
- BKT/DKT/EdNet and optional wording experiments are P2 and cannot block or substitute for honest P0 evaluation.

## 9. Current results

| Evaluation | State | Result |
| --- | --- | --- |
| Prediction baselines | Measured: 50 eligible public-audit responses | Concept/global log loss 0.640114/0.677044; Brier 0.223396/0.241975. |
| Public synthetic diagnosis audit | Twelve public-audit cases measured separately from development | Both policies find 2/2 labeled gaps; coverage 2/12; no false diagnosis on four no-gap controls. Exposed, not blind. |
| Recommendation comparisons | Three policies measured under identical hard constraints | Each: 25/25 catalog items, 12/12 prerequisite-valid plans, 3/3 distinct reassessments, 4/4 annotated exhaustion controls; aggregate tie. |
| Fresh practice/reassessment feasibility | OPEN-01 budget resolved; authored-slice test passes | Full catalog/live-loop evidence pending. |
| Contract/split integrity | Frozen hashes/splits validated; domain and independent metric/leakage tests pass | Four structural variants and explicit failures covered; HTTP/browser integration remains Phase 3. |
| Real learning benefit | No study | No claim. |

Future entries must link actual run artifacts/commits and record failed as well as passing results.

The [evaluation packet](../evaluation/readme.md) specifies annotation groups, exact denominators, future blueprint prerequisites, and the prefix-only Phase 2 runner. `python -m scripts.check_phase0` validates the definitions from backend/; it does not fit or evaluate a model.

## 10. Phase 2 measurement record

[Manifest](../evaluation/results/phase2-v2/manifest.json), [report](../evaluation/results/phase2-v2/report.md), [per-case development](../evaluation/results/phase2-v2/development.json), [public final audit](../evaluation/results/phase2-v2/test.json), and [model card](../evaluation/model_card.md) contain actual measurements with implementation hashes matching commit fc71e487c0e1261928dbe1217a32263f36c255b9. The manifest records pending documentation/prior artifacts as a dirty delivery tree. Initial clean-tree v1 is retained; v2 is regression reproduction following a Windows CLI output fix, with unchanged policy/metrics and no new independent-trial claim. All eight development and twelve audit expected-state/invariant checks pass; no metric was tuned to obtain this result. Definitions in the frozen packet retain historical results=not_run; the run manifest is the measurement record.

Training has 23 eligible responses (13 correct); smoothed global probability is 5/9. Audit predictions exclude thirteen events with explicit reasons; diagnosis counts separately cover two labeled-gap, four no-gap, four missing-evidence and two no-trigger cases. Prerequisite validity uses returned plans as the denominator (twelve); item checks and complete-plan invariants are separate. Exhaustion uses four explicitly annotated controls, rather than selecting a denominator after viewing model outputs. Average precision groups ties, and all null ratios have reasons.

Four [fixture-only structural variants](../evaluation/variants.v1.json) exercise ties, depth/multiple paths, an independent shortcut and contextual tags. Their artificial question scaffolds are not curriculum additions or quality labels. Exact reproduction is a regression check of an exposed public audit. Both diagnosis policies and all three plan policies tie here; no confidence interval, causal explanation or learning effect is claimed. The authored slice remains too narrow for a broad ranking/generalization conclusion.
