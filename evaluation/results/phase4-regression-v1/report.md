# Phase 2 measured synthetic audit

Public exposed cases; no blind, generalization, causal or learning-gain claim.

## development

Cases: 8; failures: 0.

| Prediction | N | Positive/negative | Log loss | Brier | ROC AUC | Average precision |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| global_rate | 24 | 11/13 | 0.708656 | 0.257716 | 0.5 | 0.4583333333333333 |
| concept_smoothed | 24 | 11/13 | 0.613825 | 0.211019 | 0.7727272727272727 | 0.6414141414141414 |

| Diagnosis | Labeled/all | Precision@1 | Recall@3 | MRR | Coverage | No-gap false rate |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| lowest_estimate | 3/8 | 1.0 | 1.0 | 1.0 | 0.375 | 0.0 |
| prerequisite_aware | 3/8 | 1.0 | 1.0 | 1.0 | 0.375 | 0.0 |

Recommendation counts, all metrics/denominators, excluded events, per-case outputs and observed workflow predicates are in the matching JSON file.

## test

Cases: 12; failures: 0.

| Prediction | N | Positive/negative | Log loss | Brier | ROC AUC | Average precision |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| global_rate | 50 | 30/20 | 0.677044 | 0.241975 | 0.5 | 0.6 |
| concept_smoothed | 50 | 30/20 | 0.640114 | 0.223396 | 0.6958333333333333 | 0.7393739586762842 |

| Diagnosis | Labeled/all | Precision@1 | Recall@3 | MRR | Coverage | No-gap false rate |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| lowest_estimate | 2/12 | 1.0 | 1.0 | 1.0 | 0.16666666666666666 | 0.0 |
| prerequisite_aware | 2/12 | 1.0 | 1.0 | 1.0 | 0.16666666666666666 | 0.0 |

Recommendation counts, all metrics/denominators, excluded events, per-case outputs and observed workflow predicates are in the matching JSON file.

## Interpretation

The global rate is fit on eligible training events only. Concept predictions use the preceding learner prefix, including an internal 1/2 prior for no observations. That prior is never displayed as assessed mastery.

Precision@K divides by returned candidates (zero on labeled-case abstention). Coverage uses all cases; false diagnoses use only no-gap controls. PR AUC means tie-grouped stepwise average precision. Undefined ratios have explicit reasons in JSON.

All plan comparators share targets, catalog, stages and hard readiness/freshness constraints. Lowest-estimate prioritizes available DAG concepts, then the frozen activity score. Random uses fixed per-learner seeds within available concepts/stages. The two-concept chain provides little ranking discrimination.

Prerequisite validity counts returned plans with correct ordering/readiness/locks; this is not a count of currently executable questions. Item counts and gap coverage are separate. Reassessment distinctness does not assert that a learner completed the workflow.

The frozen manifest retains results=not_run as historical definition metadata. This run's manifest and outputs are the measurement record. Production activation and browser storage are outside this audit. Full-catalog engineering checks do not extend this two-concept quality audit's coverage.
