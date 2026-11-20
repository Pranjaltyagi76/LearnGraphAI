# Baseline v1 model card

**Measured:** 20 November 2026. **Status:** the deterministic baseline is now active in the verified Phase 3 public API/browser loop; the full curriculum and release audit remain later gates. [Measured report](results/phase2-v2/report.md), [per-case final audit](results/phase2-v2/test.json), [run manifest](results/phase2-v2/manifest.json).

## Intended use and policy

This synthetic demonstration summarizes observed correctness, proposes evidence-supported target/upstream gaps, and offers bounded practice or assessment. It is not validated mastery, causal explanation, student placement, or evidence of improved learning. No real student data is used.

`baseline-v1` uses `(successes+2)/(eligible+4)`. Only the first distinct primary-concept response with known zero hints counts. Unknown/hinted first responses consume the slot; retries cannot rescue it. Lessons and contextual tags add zero observations. Unassessed public estimates are null. Support requires three observations; weakness is strictly below 0.45 and prerequisite readiness is at least 0.65. These frozen initial policies were not fitted to this audit.

Diagnosis considers the focus and ancestors within three edges, requires supported weakness and at least two recent failures, then ranks exact rational weakness, distance, evidence strength and recurrence. It abstains on missing/mixed evidence. Scores are not confidence or causality probabilities. Plans enforce freshness, topology, actual direct-parent readiness and distinct reassessment. A lesson or planned practice never manufactures readiness. Fresh same-run practice after a failure/diagnostic anchor is a workflow predicate, not verified adherence or another correctness-evidence exclusion.

## Data and execution

The unchanged packet has four training, eight development and twelve public final-audit learners, disjoint by learner/scenario group. Items and broad families recur across splits. Annotations are hand-authored assumptions made before the engine existed, kept separate from inference. Public cases were exposed during review: no blind, unseen-family or item-held-out claim is made. Four fixture variants test ties, depth/multiple paths, a graph shortcut and secondary tags. Cloned fixture questions are not a reviewed expanded curriculum or a quality dataset.

The global rate uses only 23 eligible training responses (13 correct), yielding `(13+2)/(23+4)=5/9`. Each test learner starts from the prior; predictions use only their preceding prefix. The final measured implementation is committed as `fc71e487c0e1261928dbe1217a32263f36c255b9`. The v2 manifest honestly records a dirty delivery tree (pending documentation and prior measurement files); every measured implementation file matches that commit after LF normalization. Initial [v1](results/phase2-v1/manifest.json) was measured on a clean tree; v2 repeats the exposed audit after a Windows CLI JSON-output correction, with unchanged policy and metrics. It is regression evidence, not a new independent trial. The manifest records source/input/output hashes, environment, split exposure, comparator seed and command. No new dependency or paid service was added. There was no output-guided final-audit tuning. Development tests corrected implementation defects, including seed-anchored failed-practice handling, before that run.

## Final-audit measurements

| Prediction baseline | Eligible / correct / incorrect | Log loss | Brier | ROC AUC | Average precision |
| --- | --- | ---: | ---: | ---: | ---: |
| Training-only global rate | 50 / 30 / 20 | 0.677044 | 0.241975 | 0.500000 | 0.600000 |
| Prefix concept smoothing | 50 / 30 / 20 | 0.640114 | 0.223396 | 0.695833 | 0.739374 |

Thirteen events are excluded: four unknown-hint first responses, seven hinted first responses, one retry and one lesson. No prediction sees its own outcome. PR AUC means tie-grouped stepwise average precision; log-loss clipping is metric-only at `1e-15`.

Both diagnosis methods have Precision/Recall@1/@3 and MRR of 1.0 on **two labeled-gap cases only**. Both answer 2/12 cases (coverage 0.166667), with no false diagnosis on four no-gap controls. Four missing-evidence and two no-trigger controls remain separate. Precision divides by returned candidates; labeled-case abstention contributes zero. The methods tie; these counts cannot establish diagnosis superiority or general accuracy.

Each recommendation comparator emits 25 items across twelve plans: 25/25 catalog-valid items, 12/12 plans with correct prerequisite ordering/readiness/locks, 3/3 distinct unseen reassessment items, zero repeated questions, and honest exhaustion on 4/4 explicitly annotated controls. Labeled gap coverage is 2/2; mean authored difficulty fit is 0.807905. All twelve plans pass independent invariants for each comparator. Locked steps count as valid; this does not mean every item is currently executable or any learner completed the plan.

Comparators share targets, stages and hard safety constraints. Lowest-estimate changes available-concept priority; random uses fixed per-learner seeds among available concepts/stages. Their aggregate metrics tie in this small two-concept chain. Four annotated controls are the exhaustion denominator; additional naturally exhausted cases remain visible. Both measured splits have zero retained expected-state/invariant failures. Development results are reported separately.

## Limits and next validation

Only twelve questions/two lessons cover two of twelve concepts. The remaining sixty questions and full release/accessibility audit remain later work. Browser persistence, bounded HTTP admission/shared quotas and the deployed loop are now verified in Phase 3; full quota/outage/restore drills remain Phase 5. Fixture graph/tag checks are not full-catalog educational evidence. The completed-cycle helper describes observed synthetic workflow, including hinted attempts, without claiming correctness evidence or learning. The sample does not justify uncertainty intervals or probability calibration.

Re-running this public audit is regression verification. Output-guided tuning requires a new independent versioned audit and exposure disclosure. Future full-catalog evaluation needs competing gaps, varied dependency assumptions and noise; educational benefit needs a separate appropriate real-world study. BKT, DKT, LLMs and paid services are unnecessary for this baseline.

## Phase 3 activation record

The [source-pinned Phase 3 regression](results/phase3-regression-v1/manifest.json) reproduces the same policy and exposed audit metrics with the new API modules. The original measurements above remain historical; current-source verification uses `python -m scripts.evaluate --check ../evaluation/results/phase3-regression-v1`. The actual summary is included in the published immutable package and served through GET /api/v1/analytics/evaluation.

[Live browser proof](../context/evidence/phase3_live.json) verifies Mira's two fresh practices and distinct reassessment: seed evidence 0/3 correct becomes current evidence 3/6, with smoothed estimate 0.5/developing and exhausted fresh questions. Refresh/local reset and a separate fresh browser pass. These observations demonstrate deployed behavior, not new model-quality evidence, verified student adherence or a learning effect. All earlier sample/exposure/calibration limits remain applicable.
