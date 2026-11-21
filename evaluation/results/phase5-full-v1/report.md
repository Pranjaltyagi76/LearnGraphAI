# Full-track synthetic release audit — v1

Frozen before first measurement at commit 4b1ffe3. Baseline implementation already known; public, not blind. No output-guided tuning. Same product items/families are reused across disjoint learner groups. Labels are authored assumptions, not educator/student or causal truth.

Training: 12 learner groups / 48 eligible responses. Development: 12 cases. Final synthetic audit: 24 cases, 659 eligible predictions (592 correct/67 incorrect), six excluded events.

| Prediction baseline | Log loss | Brier | ROC AUC | Average precision |
| --- | ---: | ---: | ---: | ---: |
| global_rate | 0.415177 | 0.119409 | 0.500000 | 0.898331 |
| concept_smoothed | 0.540454 | 0.175670 | 0.926243 | 0.984753 |

Per-concept smoothing is worse on test log loss/Brier despite better ranking metrics. The test set is heavily correct-skewed with many assessed-ready controls. This does not establish overall superiority for either method. Development log loss/Brier differ in direction; all raw results are retained.

Both diagnosis baselines tie: 16 labeled-gap cases, Precision@1=1, Recall@3=1, MRR=1; coverage 16/24, zero false diagnoses on three no-gap controls. Missing-evidence and no-trigger controls number three and two. These small constructed counts are not a general accuracy estimate.

| Plan baseline | Emitted items | Checked plans | Catalog validity | Prerequisite validity | Distinct reassessment | Exhaustion honesty |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| random_eligible | 85 | 24 | 1.0 | 1.0 | 1.0 | 1.0 |
| lowest_estimate | 85 | 24 | 1.0 | 1.0 | 1.0 | 1.0 |
| prerequisite_aware | 85 | 24 | 1.0 | 1.0 | 1.0 | 1.0 |

Both measured splits have zero retained diagnosis-state/plan-invariant failures. Full per-case outputs, counts, undefined-denominator reasons, source/input hashes, environment, exposure and training-only fit are in the adjacent JSON files. Engineering success does not imply calibrated mastery, student learning or independent educational validation.

The original two-concept audit remains archived and reproduces independently; these results never overwrite that historical sample or the immutable published full-v1 package.
