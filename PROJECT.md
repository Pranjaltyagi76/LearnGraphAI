# LearnGraph AI

## Knowledge Gap Diagnosis & Personalized Remediation Engine

> **Project type:** Explainable learning analytics, knowledge graphs, and lightweight ML.
>
> **Primary use case:** Identify evidence-supported prerequisite gaps behind repeated mistakes and recommend a focused next activity.
>
> **Target domain:** An independently built technical-education portfolio prototype, initially covering recursion and introductory dynamic programming.
>
> **Deployment goal:** A publicly accessible personal portfolio demo using only free plans, with a strict recurring service budget of **₹0 / $0**.
>
> **Status:** Revised implementation roadmap; implementation has not started. Algorithm parameters and curriculum edges below are initial design choices to validate, not measured results.
>
> **Last revised:** 20 November 2026.

This revision replaces the broader first-release curriculum, mandatory Render backend, paid fallback, shared editable demo profiles, and ambiguous model/evaluation rules. The roadmap now includes an early Vercel deployment check, an isolated anonymous demo, actual practice and reassessment in P0, and separate later research milestones.

---

## 1. Executive summary

LearnGraph AI analyzes a learner's activity history, estimates performance by concept, follows prerequisite relationships, and recommends a short remediation or assessment plan. It explains the evidence behind each suggestion and can abstain when the evidence is insufficient.

The complete product loop is:

**Diagnostic answer → updated performance estimate → suspected gap or evidence request → targeted practice → different reassessment question → refreshed dashboard.**

For example, repeated memoization mistakes and independent evidence of weak base-case reasoning may justify practicing base cases first. If base-case knowledge has never been assessed, the system should recommend a diagnostic question instead of declaring a weakness.

A diagnosis is an evidence-supported hypothesis, not proof that a prerequisite caused an error. The baseline estimates observed correctness; it does not directly measure latent understanding. The interface must communicate those limits.

The first release requires no LLM, GPU, hosted training, coding judge, account registration, or paid service.

---

## 2. Problem statement

A wrong answer can reflect an insecure prerequisite, a misconception in the current skill, implementation confusion, an unusually hard question, or an unreliable question tag. Generic recommendations treat these different situations alike.

The proposed solution combines:

- A small, reviewed concept prerequisite graph.
- A transparent baseline estimate from previous responses.
- A diagnosis engine that ranks supported gaps and identifies missing evidence.
- A recommendation engine that respects prerequisites and the available catalog.
- Template explanations with evidence, limitations, and plausible alternatives.
- A reassessment loop that uses different items to test the same skill.

Learners receive a manageable next step and a readable explanation. A later mentor view can support intervention review when access controls are implemented.

This is an independent prototype. It uses no private Scaler records, claims no verified gap in Scaler's internal systems, and makes no unmeasured claim of improved learning outcomes.

---

## 3. Product goals and non-goals

### First-release goals

1. Provide an anonymous, clearly labeled synthetic demo.
2. Represent a focused curriculum with stable concept IDs and reviewed prerequisites.
3. Grade authored questions and process a bounded attempt history deterministically.
4. Distinguish unassessed concepts, early estimates, and supported evidence of weakness.
5. Recommend assessment when evidence is missing and remediation when weakness is supported.
6. Show evidence, prerequisite paths, alternative explanations, and ranking limitations.
7. Complete practice and reassessment using distinct questions.
8. Update the dashboard from a single consistent analysis result.
9. Publish reproducible baseline evaluation and a model card.
10. Deploy and operate within free quotas, allowing graceful unavailability rather than charges.

### Non-goals for the first release

- A complete LMS, arbitrary code execution, or a coding judge.
- Public registration, email delivery, private learner records, or real mentor access.
- General chat, unrestricted solutions, agents, or an LLM in the prediction path.
- A graph database, hosted experiment tracker, hosted model training, or GPU inference.
- BKT, DKT, EdNet processing, and cohort analysis as release requirements.
- Proof of causal diagnosis or educational effectiveness.
- Unlimited traffic, guaranteed uptime, or permanent availability of a provider's free plan.

---

## 4. Target users and core workflows

### Learner/demo workflow — P0

1. Open one of four labeled synthetic profiles without registering.
2. Create a local sandbox from its immutable history.
3. Complete a diagnostic question or inspect existing evidence.
4. View performance estimates and unknown concepts on the dashboard and graph.
5. Inspect a suspected gap, its evidence, and alternatives; an abstention is a valid outcome.
6. Complete the suggested lesson and authored practice questions.
7. Answer a different reassessment item for the same primary skill.
8. Receive one refreshed history/mastery/diagnosis/plan result.
9. Refresh to resume the local sandbox or reset it to its original seed.

### Isolation and persistence contract — P0

- Seed profiles are immutable and have no public update/reset endpoint.
- Each browser stores its own synthetic sandbox history under a profile- and version-specific storage key. Different profiles remain separate; different browsers do not share mutations. Tabs using the same browser storage share that local sandbox and must handle storage updates without overwriting newer state.
- Visitor events are kept in browser storage; the API replays the bounded history against the canonical seed and catalog. P0 does not persist visitor attempts to shared learner rows.
- Browser history is editable, untrusted demo input, not a verified educational record. The API validates it and derives grades itself.
- Local persistence is best effort: clearing storage removes progress; cross-device sync is not provided. If storage is unavailable, show a session-only notice and keep the sandbox in memory.
- Reset clears only the visitor's local changes. No browser can reset or modify another visitor's state.
- Pending answers are visibly pending until analysis succeeds. An unavailable API must not appear to have accepted an answer.
- A graph/catalog/model version mismatch requires an explicit reset or a documented migration; never silently reinterpret an old answer under a new question.

### Mentor workflow — later milestone

After authentication and explicit mentor–learner assignments exist, a mentor may inspect assigned learners, review a diagnosis, submit corrections, and inspect later performance. A synthetic mentor preview may be added earlier as read-only portfolio polish, but real learner access remains deferred.

### Unavailable-service workflow

The landing page and bundled example views remain available without live API/database access. An example is explicitly labeled **prerecorded synthetic example** with its versions and date. Live submission is disabled with a retry action; pending local work is retained. Do not silently substitute example results for a live analysis.

---

## 5. Core features and release priorities

### P0 — Required for the first deployed release

- Four synthetic profiles: supported prerequisite weakness, target-skill weakness with secure prerequisites, sparse/unknown evidence, and ambiguous/noisy performance.
- A 12-concept recursion/introductory-DP curriculum and 72 distinct authored questions, plus short linked lessons.
- Immutable seeds, isolated local sandboxes, refresh/resume, and local reset.
- Validated event replay, backend grading, deterministic deduplication, and bounded requests.
- Baseline performance estimates with distinct-activity counts and evidence labels.
- Bounded prerequisite diagnosis, abstention, and assessment requests for unknown skills.
- A bounded recommendation plan with valid IDs, reasons, and prerequisite ordering.
- An actual diagnostic → practice → different reassessment loop with a before/after view.
- Template explanations, learner dashboard, accessible graph, and responsive layouts.
- FastAPI API, backend tests, frontend checks, and critical browser-flow tests.
- Reproducible baseline evaluation, model card, free public deployment, and recovery documentation.
- Clearly labeled example views when a live dependency is unavailable.

### P1 — Product extensions after P0 passes

- Diagnosis feedback and reviewed corrections.
- Read-only synthetic mentor/analytics preview and evaluation dashboard.
- Browser-generated learning-plan export; no hosted document-generation dependency.
- Validated CSV import, with row/byte limits, preview, and explicit imported-evidence provenance.
- Authentication, owned server persistence, deletion/export, and cross-device sync as one complete milestone.
- Real mentor access only after assignments, authorization tests, and access auditing exist.

P1 features must independently satisfy the ₹0 constraint. Unavailable free capabilities remain deferred rather than introducing a paid dependency.

### P2 — Optional research and expansion

- BKT versus the frozen baseline, evaluated offline.
- EdNet or another suitably licensed dataset as a separate knowledge-tracing experiment.
- Recency weighting, difficulty adjustment, and richer recommendation experiments.
- DKT only with sufficient sequential data, local compute, and a justified comparison.
- Optional Gemini wording, disabled by default, only if verified free access is available.
- Additional DSA topics, domains, and offline cohort analysis.

BKT, EdNet, Gemini, and DKT are not prerequisites for completing P0 or publishing its evaluation.

---

## 6. First curriculum and content contract

### Canonical assessed concepts

Use stable lowercase IDs. Topic groups such as “Recursion” and “Dynamic programming” are navigation metadata, not additional assessed nodes.

| Concept ID | Definition |
| --- | --- |
| `function_calls` | Follow arguments, return values, and execution across function calls. |
| `call_stack` | Track active calls and how returns unwind them. |
| `base_cases` | Identify stopping conditions and boundary behavior in recursion. |
| `recursive_progress` | Verify that recursive calls move toward a stopping condition. |
| `recursive_tracing` | Trace a recursive computation using calls, progress, and base cases. |
| `recurrence_relations` | Express a problem in terms of smaller instances and boundary conditions. |
| `overlapping_subproblems` | Recognize repeated equivalent subproblems. |
| `state_definition` | Define the information needed to identify a subproblem. |
| `state_transitions` | Relate a state to the states used to compute it. |
| `dp_base_cases` | Initialize valid boundary states in a DP formulation. |
| `memoization` | Cache results using a correct state key in top-down evaluation. |
| `tabulation` | Evaluate DP states in an order that makes dependencies available. |

Assume basic variables, conditionals, loops, and array indexing. Explain this entry requirement in the UI; do not infer mastery of those unassessed skills.

### Initial prerequisite edges

The convention is **prerequisite → dependent**. These are proposed instructional dependencies for this track and require review during Phase 0:

```text
function_calls -> call_stack
function_calls -> base_cases
base_cases -> recursive_progress
call_stack -> recursive_tracing
base_cases -> recursive_tracing
recursive_progress -> recursive_tracing
recursive_tracing -> recurrence_relations
recursive_tracing -> overlapping_subproblems
recurrence_relations -> state_definition
state_definition -> state_transitions
base_cases -> dp_base_cases
state_definition -> dp_base_cases
overlapping_subproblems -> memoization
state_transitions -> memoization
dp_base_cases -> memoization
state_transitions -> tabulation
dp_base_cases -> tabulation
```

Do not make recursion or memoization a universal prerequisite for every DP technique. Review the path for the actual activities being taught.

Store edge type, source/rationale, review status, and graph version. Keep `part_of`/`related_to` relationships separate from prerequisite edges; they must not drive prerequisite diagnosis.

Graph validation must reject unknown IDs, self-edges, duplicate edges, and prerequisite cycles. Render arrows in the documented direction; diagnosis walks backward to prerequisites and plan ordering walks forward.

### Activity catalog

- Author **72 distinct questions**: one diagnostic, four practice, and one reassessment item per concept. Short lessons are additional catalog entries and do not count as answered evidence.
- Each question has exactly one primary assessed concept. Secondary concepts are context tags and receive no baseline correctness update.
- Record stable activity ID, immutable activity version, role, primary/secondary concepts, authored difficulty in `[0,1]`, answer options, grading rule, explanation, and content provenance/license.
- Use multiple-choice, code-tracing, and bug-identification questions. Display code as text; never execute user code.
- Separate diagnostic, practice, and reassessment IDs and wording. Reassessment must test the same skill with an independently authored problem.
- Mark content intended to be answerable with only assumed entry skills as `foundational`; this permits entry diagnostics without pretending all their prerequisites have already been measured.
- Write original questions/lessons or link to resources with appropriate attribution. Do not copy proprietary question banks.
- The public source repository may contain authored grading rules. This is an inspectable educational demo, not a secure examination system: withholding future answers from the normal API/UI is a teaching behavior, not a claim that a determined visitor cannot find them in source.
- The 72-item catalog demonstrates a bounded loop; it is not enough to claim robust psychometric assessment. When unseen items are exhausted, say so and offer a clearly labeled review rather than fabricating fresh evidence.

**Resolved budget decision (OPEN-01, 20 November 2026):** Increase the target to 72 questions, six per concept: one diagnostic, four practice, and one reassessment. Three initial eligible items can leave two fresh practice questions and a distinct reassessment. The authored two-concept Phase 1 fixture and its catalog test prove this item-availability trace; the full 72-item catalog still needs authoring/review. This budget does not guarantee threshold crossing, educational benefit, or unlimited fresh content. See [the operational roadmap](context/phasewise_roadmap.md).

---

## 7. System architecture

```text
Browser: Next.js UI + isolated synthetic history in browser storage
   | HTTPS; canonical seed ID + bounded response history
   v
FastAPI on Vercel: validation -> grading/replay -> estimates
                    -> diagnosis -> plan -> template explanation
   | pooled Postgres access; small bounded operations
   v
Supabase Free: versioned curriculum/catalog/seeds + atomic quota counters

Local Python research -> evaluation JSON/plots + small reviewed artifacts
                              -> bundled public evaluation/example views
```

### Hosting layout

- One Git repository, initially two Vercel Hobby projects: `frontend/` for Next.js and `backend/` for FastAPI. Configure each project's root directory explicitly.
- Prefer the stable, documented FastAPI deployment path. Verify it with a minimal deployment in Phase 1 before building the full application.
- Browser-to-API calls use the configured API origin; allowlist the actual production/local origins and deliberately configured preview origins. Do not add a second Next.js API proxy by default.
- Both Vercel projects share applicable account/team quotas; creating two projects does not double the free allowance.
- Use Supabase Free for the existing planned managed Postgres capability. Do not provision additional databases, Redis, queues, or hosted tracking services for P0.

### Runtime principles

- Pure deterministic analysis functions consume validated, versioned input. Training and evaluation run outside request handlers.
- Load small immutable artifacts when an instance starts; tolerate multiple instances and cold starts. Never depend on process memory or local disk for durable shared state.
- A single analysis response contains history digest, versions, estimates, diagnosis/abstention, and plan. The UI replaces the displayed analysis together.
- Browser state is synthetic and untrusted. Server-owned catalog metadata and grading rules determine the result.
- Database-backed quota enforcement is shared across instances. If enforcement is unavailable, live analysis fails closed while static example pages remain available.
- No LLM is required by the architecture. Optional later wording must not change scores, evidence, or allowed activity IDs.

---

## 8. Algorithm and event design

### 8.1 Response events, provenance, and replay

Example client-submitted visitor event, appended to a request's bounded history:

```json
{
  "schema_version": 1,
  "event_id": "b5b06733-2c94-4ba3-b052-e81c9c88d988",
  "sequence_number": 1,
  "activity_id": "base_cases_diagnostic_01",
  "activity_version": 1,
  "assessment_run_id": "d33fc28e-1a59-40c2-a68d-f49ef27b46d6",
  "occurred_at": "2026-11-20T07:00:00Z",
  "response": {"option_id": "b"},
  "hints_used": 0,
  "time_spent_seconds": 75
}
```

The request envelope also includes seed ID, seed version, graph version, catalog version, model/config version, and the ordered event array. The server loads the immutable seed history itself; clients cannot replace it.

Rules:

- Require IDs, versions, sequence, timestamp, and a valid response. Missing optional timing/hint fields become `null`, not invented measurements. Unknown hint usage is ineligible for unassisted baseline evidence.
- Validate UUIDs, option IDs, catalog versions, finite numeric ranges, nonnegative times/hints, allowed timestamp skew, and bounded arrays/strings. The illustrative activity ID must exist in the authored catalog before use.
- Derive primary concept, secondary tags, difficulty, correct answer, grade, phase, and attempt number from the catalog and replay. Reject client-supplied authoritative grades or tags.
- Keep receipt time as request telemetry, separate from event occurrence time. Record provenance as canonical synthetic seed, visitor demo, or later imported/reviewed evidence.
- Visitor sequence numbers start at 1 after the seed. Deduplicate identical event IDs and payloads before validating a contiguous sequence; conflicting reuse returns `409`. Reject duplicate sequence numbers, gaps, or decreasing occurrence times with `422`; no silent reordering.
- Chronological seed events precede visitor events. Browser-generated times must be consistent with that seed's timeline. Versions and ordering determine replay; current wall-clock time must not change the P0 estimate.
- Repeating an identical full-history request returns the same semantic analysis and history digest. Request IDs/receipt telemetry may differ. The client appends an acknowledged event once by ID.
- P0 does not promise durable server-side idempotency or verified attempt receipts: there is no visitor-event database write. Once owned server persistence is introduced, use a unique owner/event constraint and a database transaction for event storage and derived state.
- `error_type` is optional reviewed/imported metadata, never a trusted diagnosis label supplied by a public visitor. Do not train or evaluate against an unavailable oracle label.

### 8.2 Evidence features

P0 uses correctness, distinct eligible activities, recent distinct failures, and prerequisite paths. Show all submissions, hints, provenance, and last evidence time as context. Raw elapsed time is not a proxy for ability.

Recency weighting, difficulty adjustment, and hint-aware scoring are later experiments; do not imply that the baseline already includes them.

### 8.3 Baseline estimate and evidence states

For each concept, use the **first submitted response to each distinct question** whose primary concept matches and whose `hints_used` is known to be zero. Retried responses to the same question, hinted responses, lessons, and secondary tags do not add baseline observations. A later unhinted retry does not turn an initially hinted question into fresh evidence.

```text
n(c) = number of eligible distinct question responses
s(c) = number of correct eligible responses
estimate(c) = (s(c) + 2) / (n(c) + 4)
```

This is a smoothed estimate of observed performance, not a calibrated probability of latent mastery. The Beta-style prior is a transparent baseline assumption; correlated questions and synthetic histories limit its interpretation.

Initial configurable display rules:

| Evidence | Display and interpretation |
| --- | --- |
| `n = 0` | `not_assessed`; retain the internal prior if needed, but show no 50% mastery claim. |
| `1 <= n < 3` | `early_estimate`; show evidence counts and avoid a supported weakness claim. |
| `n >= 3` | `supported_estimate`; show the estimate with counts and limitations. |
| Supported estimate `< 0.45` | Evidence of weakness for the baseline's configured activity mix. |
| Supported estimate `>= 0.65` | Prerequisite readiness threshold for this demo. |
| Supported estimate in between | Developing/mixed evidence; not automatically weak or secure. |

These thresholds are proposed defaults, not validated educational cutoffs. Version all parameters and tune only on development data. Report eligible/distinct/all-attempt counts, successes, evidence state, last evidence time, and provenance. Use evidence labels rather than invented confidence percentages.

New distinct practice/reassessment questions can change the estimate. Completing a lesson, retrying a memorized item, or simply waiting does not automatically improve it. The UI may show little or no numerical change and must explain why.

### 8.4 Later knowledge-tracing experiments

BKT models initial knowledge, learning, guessing, and slipping. It is a P2 offline comparison, not a P0 dependency. Distinguish latent-knowledge estimates from next-response probabilities: BKT's response prediction includes guess and slip terms.

Fit parameters and preprocessing on training learners only. Evaluate on untouched learners and causal event prefixes as described in Section 10. DKT remains optional and must fit available local compute. Promote an experimental model only after documented comparisons; do not silently swap the deployed baseline.

### 8.5 Prerequisite-aware diagnosis

Analyze a failed question's primary concept and prerequisite ancestors up to **three edges** backward. Include the target itself as a distinct candidate so the system can identify a target-skill gap when prerequisites appear secure. Use the shortest prerequisite path for scoring and include its evidence IDs in the output.

Initial factor definitions for candidate `c`:

```text
d(c) = shortest prerequisite distance; target has distance 0
weakness(c) = 1 - estimate(c)
relevance(c) = 1 / (1 + d(c))
evidence_strength(c) = min(n(c) / 5, 1)
recent_failures(c) = failures among the latest 3 eligible distinct responses
recurrence(c) = min(recent_failures(c) / 2, 1)
score(c) = weakness(c) * relevance(c) * evidence_strength(c) * recurrence(c)
```

Each factor and the resulting score are in `[0,1]`. Rank only candidates with `n >= 3`, estimate `< 0.45`, and at least two recent failures. Return at most three, ordered by descending score, then shortest distance, then concept ID. No score normalization is required; normalized values would still not be causal probabilities.

- A supported prerequisite gap may produce remediation. An unknown/early prerequisite produces an evidence request, never an inferred weakness.
- If no candidate qualifies, return `insufficient_evidence`, `ambiguous`, or `no_supported_gap` with reasons. Include separate assessment suggestions where useful.
- Distinguish direct target weakness from upstream weakness in wording. A failure must not automatically propagate to every ancestor.
- Explain that the latest failed response is evidence for a retrospective diagnosis. In predictive evaluation, that same answer must not be available before its prediction.
- Alternatives include current-item difficulty, ordinary response error, misleading tags, and contradictory recent evidence. Do not fabricate a specific misconception without reviewed supporting information.
- Evidence strength is an observation-count indicator, not a calibrated confidence probability. Include graph, catalog, seed, and model/config versions with every output.

### 8.6 Recommendation selection

Select the recommendation mode before ranking:

1. Supported weakness: remediation for the gap and its supported weak prerequisites.
2. Missing prerequisite evidence: a short assessment, labeled as evidence gathering.
3. Mixed/adequate evidence: suitable further practice or an explicit no-supported-gap result.

Hard constraints precede scores:

- Only active, version-matched catalog activities with valid IDs may appear.
- Remediation practice requires prerequisite readiness, or an earlier supporting step in the plan. Unknown prerequisites require assessment first; supported weak ones require remediation first.
- A diagnostic may assess an unknown skill, but missing prerequisites make its result ambiguous. Prefer foundational/root diagnostics when possible.
- Use prerequisite topological order. Do not interpret a lesson completion as measured mastery.
- Reassessment must use a different, unused question for the same primary concept. Never relabel an immediate retry as a fresh reassessment.
- Bound plans to five items, including lessons, practice, and reassessment. Recompute after each answer; a planned later item stays locked until its readiness condition is met.

Initial configurable activity ranking within those constraints:

```text
gap_match = 1 if the primary concept is a selected gap/evidence target, else 0
prerequisite_coverage = 1 if the primary concept is a needed prerequisite, else 0
desired_difficulty = 0.2 if not assessed, else clip(estimate, 0.2, 0.8)
difficulty_fit = 1 - abs(authored_difficulty - desired_difficulty)
novelty = 1 if the activity has never been answered, else 0
recent_repeat = 1 if the activity occurs in the latest 5 submissions, else 0
score = 0.5*gap_match + 0.2*prerequisite_coverage
        + 0.2*difficulty_fit + 0.1*novelty - 0.5*recent_repeat
```

Tie-break by activity ID after prerequisite ordering. Authored difficulty is an ordinal design aid, not calibrated item difficulty. Scores do not estimate expected learning gain. Return a reason and readiness condition for every item. If no valid unused item exists, return `catalog_exhausted` or `no_suitable_activity`; offer a labeled review without counting it as new evidence.

### 8.7 Explanations

P0 uses templates populated from validated evidence IDs, estimates, counts, graph paths, permitted activities, and abstention reasons. Wording must distinguish “not assessed” from “evidence of weakness.”

An optional P2 LLM may reword this structured result only. It cannot create scores, change diagnosis ordering, invent causal certainty, recommend outside the allowed catalog, expose private data, or turn a hint into an unrestricted solution. Validate its output and fall back to templates on timeout, quota exhaustion, or invalid output. Ship with the integration disabled.

---

## 9. Data strategy and governance

### P0 data

- Manually reviewed concept graph and original, versioned questions/lessons.
- Four compact synthetic seed histories with no real personal information.
- A reproducible synthetic benchmark generator with documented assumptions and fixed seeds.
- Bounded canonical seed histories of at most 100 events and visitor histories of at most 200 events per sandbox. Do not silently discard old evidence when a cap is reached; offer reset or later export.

The generator should include supported gaps, secure prerequisites with target weakness, sparse histories, ordinary slip/guess noise, hints, retries, missing optional metadata, and ambiguous cases. Invalid records belong in ingestion tests, not silently in a valid training dataset.

### Prevent circular evaluation

Separate generator code from diagnosis code. Do not compute ground-truth labels by calling the ranking function being evaluated. Freeze an untouched test set before tuning. Different random seeds alone do not establish independent assumptions: include hand-authored holdout scenarios and generator variants with different noise or dependency behavior.

Synthetic results show implementation behavior under stated assumptions; they do not establish real-world educational effectiveness.

### EdNet — optional P2 research

[EdNet](https://github.com/riiid/ednet) contains educational interactions rather than this project's DSA curriculum. Its repository describes CC BY-NC 4.0 research use. Review current terms and attribution requirements before use. Do not map its skill tags to DSA concepts without a defensible mapping or claim its users are Scaler learners.

Process only a documented local subset if the experiment fits available disk/RAM. Publish aggregate metrics and reproducibility instructions; keep raw records and large processed artifacts outside Git and hosted runtime bundles. EdNet is not needed for the P0 demo.

### Governance

- No scraping authenticated educational platforms or using private student submissions.
- Attribute linked resources and dataset licenses; keep code and third-party data licenses distinct.
- Label synthetic profiles and prerecorded examples throughout the UI and screenshots.
- No public personal-data uploads in P0. Before real accounts/imports, define consent, retention, deletion, export, access controls, and logging boundaries.

---

## 10. Evaluation plan

### Prediction protocol

Predict the next eligible response from the event prefix **before** observing that response. Record the prediction and outcome, then update state. Start each held-out learner from the prior and allow only their earlier observed responses to update their state. Never initialize from their complete history or fit global parameters on test learners.

Split by learner for generalization and use temporal prefixes within each sequence. Report an additional item-held-out evaluation only if the catalog/data support it; otherwise disclose item reuse. Any tuned thresholds, feature processing, or model fitting use training/development data only.

The deployed baseline may show all submitted attempts, but its reported prediction metrics use its documented eligible-event policy. Include hints/retries as separate robustness analyses rather than quietly changing the denominator.

### P0 comparisons and metrics

| Evaluation | Required comparisons | Metrics and reporting |
| --- | --- | --- |
| Next-response prediction | Training-only global-correctness baseline; per-concept smoothed baseline | Log loss and Brier score; ROC-AUC/PR-AUC only where classes support them; counts and class balance. |
| Diagnosis | Lowest-estimate concept; prerequisite-aware heuristic | Precision/Recall@K, MRR, top-1 on labeled cases; state whether labels are single or multiple; abstention coverage and error among answered cases. |
| Recommendation | Fixed-seed random selection from eligible activities; lowest-estimate-first; prerequisite-aware policy | Prerequisite validity, catalog validity, weak-concept coverage, repetition, exhaustion, and authored difficulty fit. Ranking relevance metrics only when independent labels exist. |
| Robustness | Untouched sparse/noisy/ambiguous scenarios | Unknown-versus-weak behavior, retry invariance, malformed input rejection, and sensitivity to graph/tag errors. |

Use the same hard safety/catalog constraints for recommendation comparisons so the experiment isolates ranking quality. Report sample sizes, denominators, seeds, configuration versions, split manifests, and failures. Undefined metrics must be `N/A` with a reason. Use repeated seeds or learner-level bootstrap intervals when sample size supports them; do not imply narrow certainty from tiny synthetic samples.

Report evidence strength as a heuristic label, not probabilistic diagnosis calibration. Confidence calibration requires separately defined outcomes and enough independent labeled cases.

### Reassessment and learning claims

Show changes on distinct, matched-skill items, including unchanged or worse outcomes. Synthetic pre/post changes demonstrate UI and algorithm behavior, not real learning gains. Claims of educational benefit require an appropriate real-world pilot or controlled evaluation beyond P0.

### P2 research report

Add BKT and optionally DKT only after P0. Compare on the same eligible protocol or explicitly explain the changed observation model. Keep EdNet results separate from DSA diagnosis results. Publish measured results even if the advanced model does not improve on the baseline.

---

## 11. Database and state design

Use Supabase Free Postgres for small canonical data and quota enforcement. UUIDs, timestamps, foreign keys, relevant indexes, and migrations are required. A profile template is not an authenticated user.

| Entity | Stage | Persistence and purpose |
| --- | --- | --- |
| `curriculum_versions`, `concepts`, `concept_edges` | P0 | Immutable published graph revisions with provenance/review metadata. |
| `catalog_versions`, `activities`, `activity_options`, `activity_concepts` | P0 | Versioned question/lesson content, grading metadata, role, primary/secondary tags. |
| `demo_profiles`, `demo_seed_events` | P0 | Immutable synthetic profiles and canonical seed responses. |
| `model_versions` | P0 | Estimator, thresholds, scoring configuration, artifact hashes, and release metadata. |
| `quota_buckets` | P0 | Atomic counters with expiry for shared request budgets; no raw learner content. |
| Visitor events, assessment runs, analysis bundle | P0 | Browser-local synthetic sandbox; replayed by API, not written to shared learner tables. |
| `profiles`, owned `assessment_runs`, `attempts` | P1 accounts | Auth-linked identity and owned history with unique `(owner_id, event_id)`. |
| `mastery_snapshots`, `diagnoses`, `recommendation_plans`, `recommendation_items` | P1 accounts | Owned versioned results tied to an input-history digest and evidence events. |
| `mentor_assignments`, `diagnosis_feedback`, `audit_events` | P1 mentor | Explicit authorized relationships, feedback, and sensitive-access audit trail. |

Do not create all future tables before the baseline demo works. Keep canonical history and catalog versions needed to reproduce published examples. A historical result must identify seed/input digest, graph, catalog, and model/config versions.

### Authorization and connections

- Public visitors have no write access to canonical data or answer-key tables. Public API responses omit answer keys until the relevant feedback is due.
- Use RLS and grants for exposed database tables. Choose and document the runtime database role; privileged Postgres/service credentials can bypass RLS, so RLS is not a substitute for API authorization.
- Keep credentials server-side. Canonical-data reads and the narrowly scoped quota update function should use least privilege; migrations/seeding use separate administrative access.
- Use the Supabase shared transaction pooler for serverless runtime access, a deliberately small client pool, TLS, and driver-appropriate prepared-statement settings. Use a compatible session/direct route for migrations as documented by the provider.
- Never use a public request's learner ID as proof of ownership. Before P1 persistence, verify tokens, scope every query to the owner/assignment, and test cross-user denial.
- Never put a visitor SQLite database or durable state on a function's local filesystem.
- For later public signup, prefer a complete verified free OAuth flow if suitable. Supabase's default SMTP is restricted to authorized team addresses; do not assume it supports general public email confirmation or password recovery. Any email-based flow needs a separately verified free delivery arrangement and tested recovery behavior before release.

---

## 12. API design and consistency

Version product routes under `/api/v1`. The initial contract uses replay so stateless function instances do not need a durable visitor session.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Lightweight process health; no expensive analysis or secret output. |
| `GET` | `/ready` | Bounded dependency check; unavailable dependencies return `503`. |
| `GET` | `/api/v1/demo/profiles` | Profile summaries and published versions. |
| `GET` | `/api/v1/demo/profiles/{id}/seed` | Immutable canonical history, public catalog, graph, and versions; omit grading secrets. |
| `POST` | `/api/v1/demo/analyze` | Validate full visitor history; grade/replay; return one consistent estimates/diagnosis/plan bundle. |
| `GET` | `/api/v1/analytics/evaluation` | Static, versioned, measured public evaluation summary. |

The analysis bundle contains a semantic history digest, versions, graded events and permitted feedback, estimates/counts, graph annotations, diagnosis or abstention, evidence requests, and a bounded plan. Failed validation returns no partially accepted result.

Use strict Pydantic schemas, bounded arrays/strings, consistent errors `{code, message, request_id, details}`, and pagination for future history endpoints. Do not expose stack traces or answer keys for unanswered items.

Initial application limits, to be validated in the deployment check:

- Maximum request body: **256 KiB**, checked by byte count even when `Content-Length` is missing; maximum 200 visitor events plus a server-owned seed of at most 100.
- Maximum plan length: five items; maximum prerequisite search depth: three edges.
- Maximum analysis time budget: ten seconds, with tighter bounded database operations. Measure cold and warm behavior and display retry/unavailable states when the budget is exceeded.
- Initial shared quota policy: ten analysis requests per minute per short-lived hashed client identifier and 1,000 per day globally, whichever is exhausted first. These are tunable application defaults, not provider quotas or a cost guarantee.
- Hash identifiers using a rotating server secret; expire buckets within 48 hours. Treat identifiers as coarse abuse signals, not identity; shared networks may share limits. Quota enforcement must use atomic database operations across instances.
- Quota exhaustion returns `429` with retry guidance. Quota-store/API dependency failure returns `503`; static example views still work. Protect metadata endpoints with appropriate caching and platform-level controls as available on the free plan.

CORS is an origin policy, not authentication or a defense against non-browser abuse. Do not rely on an in-memory limiter as the global budget. Debounce client analysis, disable duplicate submit actions, and retry transient failures with bounded backoff using the same history/event IDs.

For P1 server persistence, introduce owned attempt/feedback endpoints only with authentication, durable idempotency, transactional updates or versioned recomputation, and concurrency checks. The UI must never combine a new attempt list with stale mastery or an old plan.

---

## 13. Technology stack and dependency boundaries

### Frontend

- Next.js App Router, TypeScript, and Tailwind CSS.
- An accessible component system such as shadcn/ui.
- React Flow with an accessible list alternative for graph navigation.
- Recharts only for charts actually needed; add TanStack Query only if server-state complexity justifies it.
- Browser storage for P0 synthetic progress and static bundled evaluation/example assets.

### Production API

- A currently supported Python version verified on Vercel; pin the version and exact dependency versions during setup.
- FastAPI, Pydantic, a compatible Postgres driver, and NetworkX if useful for the small graph.
- A lightweight pure-Python baseline and scoring functions; the smoothing formula does not require scikit-learn at runtime.
- SQLAlchemy/Alembic if chosen for database/migrations; keep development tooling outside the runtime dependency set.
- Small reviewed JSON configuration/artifacts. Never deserialize an untrusted pickle/joblib file.

### Local research and development

- pandas, NumPy, scikit-learn, notebooks, and plotting tools for offline generation/evaluation.
- Optional local MLflow; PyTorch only for a justified later experiment.
- pytest, Ruff, type checking, frontend lint/type/build checks, and a small critical browser suite.
- Separate runtime, development, and research dependencies so training/data packages are excluded from deployment.
- Docker Compose is an optional reproducibility path. Document ordinary Python-venv and Node setup so Docker is not a required hosted or paid dependency.

Choose current stable compatible versions at implementation time and commit lockfiles. Dependency updates and framework upgrades should be deliberate and verified, not an unbounded use of `latest`.

---

## 14. Strict free-tier and deployment plan

### Budget policy

The project's recurring service budget is **₹0 / $0**. Use free plans only. No paid fallback, paid subscription, paid API, paid GPU, purchased domain, automatic top-up, or reliance on temporary trial credits is allowed under this roadmap.

Do not attach a payment method or enable paid billing for this project. If a provider requires paid billing/card-backed usage for a capability, defer it or choose a verified free alternative. Alerts help observation but do not enforce a zero bill. Never work around quotas by creating duplicate accounts or artificial keepalive traffic.

Exhausted quotas may reduce functionality or pause services. Recheck eligibility, availability, and terms before provisioning and release; if a free plan changes, reduce scope or disable the dependent feature rather than incur charges.

### Default topology and constraints

| Layer | Default | Required handling |
| --- | --- | --- |
| Frontend | Vercel Hobby, `frontend/` | Personal noncommercial portfolio scope; cache static assets and keep the example view bundled. |
| API | Second Vercel Hobby project, `backend/` | Verify native FastAPI support and actual bundle, CPU, memory, payload, and duration in Phase 1; quotas are shared where applicable. |
| Database | Supabase Free | Small canonical data and quotas; no real student records; inactivity/limit recovery documented. |
| URL/TLS | Included `vercel.app` domains | No purchased domain or paid certificate. |
| Source/CI | GitHub Free public repository | Standard runners only, short artifact retention, bounded caches, no purchased runners/storage. |
| Research | Existing local computer | No hosted training, paid notebook runtime, GPU, or hosted MLflow. |
| Explanations | Templates | No API key required. Gemini remains disabled P2 work. |
| Alternative API host | Render Free only if needed | Verify current free eligibility and no billing method; measure sleep/cold start; never upgrade to a paid instance. |

### Verified documentation snapshot — 20 November 2026

These are planning reference values, not an entitlement guarantee. Deployment must recheck the linked sources and the actual account's available resources.

- Vercel documents native FastAPI deployment. Hobby currently lists one million function invocations, four active CPU hours, 360 GB-hours provisioned memory, and 100 GB fast data transfer; each applicable quota can constrain the demo. [FastAPI](https://vercel.com/docs/frameworks/backend/fastapi), [Hobby](https://vercel.com/docs/plans/hobby).
- Function limits currently include a 300-second Hobby maximum duration, 2 GB Hobby memory, a standard 500 MB Python bundle, and 4.5 MB request/non-streamed response payloads. Our application limits are intentionally smaller and must be measured. Do not rely on beta large-function features to make P0 deployable. [Function limits](https://vercel.com/docs/functions/limitations).
- Hobby is intended for personal, noncommercial use. This roadmap is for a personal portfolio prototype, not a commercial student platform. Exceeding Hobby allowances can pause features; never assume unlimited hosting. [Pricing/eligibility](https://vercel.com/pricing).
- Supabase Free currently lists a 500 MB database, 5 GB egress, inactivity pausing after one week, and no included automatic backups. [Supabase pricing](https://supabase.com/pricing).
- Render Free currently sleeps after 15 idle minutes, may take about a minute to restart, and grants 750 free instance hours per workspace/month. Bandwidth/build overages can be billed with a payment method; without one, relevant service/build access can be suspended. Render's free Postgres expires, so it is not the planned database. [Render Free](https://render.com/docs/free).
- Standard GitHub-hosted runners in public repositories are free; larger runners and excess storage can incur charges. Use short retention and the free path only. [Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions).

### Recovery without payment

1. Preserve migrations, authored canonical seeds, and versioned example outputs in Git; keep secrets and large data outside Git.
2. When Supabase pauses, show static examples and disable live analysis. The owner follows the provider's restore process; recreate and reseed if restoration is unavailable. Verify migrations and seeded version hashes before enabling live requests.
3. Manual exports/backups must exclude raw client identifiers and any future sensitive records from public Git. Canonical synthetic content should be rebuildable from source.
4. If the API is cold, unavailable, or quota-limited, use bounded retry with the same event IDs and then show a clear unavailable state. No paid upgrade or recurring keepalive is part of recovery.
5. If Vercel's free API path fails the measured deployment check, test Render Free with the same lightweight API. If no free live path fits, reduce workload; retain explicitly prerecorded portfolio examples until a compatible free path is verified.
6. Document usage checks and restoration steps. A prerecorded fallback is graceful degradation and does not satisfy the P0 live-loop release criterion by itself.

---

## 15. Security, privacy, and reliability

- P0 accepts synthetic quiz interactions only, never arbitrary executable code or real personal-data uploads.
- Keep credentials in provider environment variables; commit `.env.example` with names/placeholders only. No service credentials in browser bundles or logs.
- Separate admin migration/seeding access from runtime privileges. Protect canonical profiles, answer keys, and quota functions with appropriate grants/RLS.
- Before accounts, define token verification, owned data queries, mentor assignment checks, CSRF/session handling as appropriate, deletion/export, and cross-user tests. Never rely on frontend role checks.
- Bound byte size, events, graph depth, page sizes, database timeouts, and retry counts. Use atomic distributed quotas and fail closed if the shared guard is unavailable.
- Log only minimal request IDs, durations, error codes, and version information. No full responses, code submissions, raw client identifiers, or future personal data.
- Document browser-only demo persistence, local reset, and the synthetic/unverified nature of visitor history in the privacy notice.
- Restrict CORS to configured origins; validate every request regardless of origin.
- Pin dependencies, run appropriate checks, and review dependency vulnerabilities. Do not publish secrets, local databases, raw datasets, or caches in build artifacts.
- Use `/health` for lightweight liveness and `/ready` for bounded dependency readiness. Never simulate availability when live analysis fails.
- Test restart/cold-start behavior, duplicate retries, response ordering, concurrent tabs, and dependency failures. No durable state depends on a warm process or writable deployment disk.

---

## 16. UI/UX specification

### Landing and demo entry

- Headline: “Find the concept behind the mistake.”
- Clear product explanation, synthetic-data label, scope, and limitations.
- CTA to explore a demo learner without registration.
- A small graph preview and the analyze → diagnose → practice → reassess flow.
- Links to repository, measured evaluation, model card, and setup/deployment notes.
- No fake testimonials, invented learning gains, or fabricated production usage.

### Learner dashboard

- Evidence state, estimated performance, eligible distinct count, and total submissions.
- Different visual treatment for not assessed, early evidence, developing, and supported weakness/readiness.
- Timeline with hints/retries shown separately from counted evidence.
- A short plan with explanations, locks/readiness conditions, and catalog-exhaustion states.
- Local persistence notice, reset, pending-answer state, and same-browser tab synchronization behavior.

### Diagnosis and graph

- Suspected gap or explicit abstention; evidence cards link to actual event IDs.
- Shortest prerequisite path, direction legend, alternatives, and evidence-strength wording.
- No causal probability or invented confidence percentage.
- Node labels, keyboard navigation, adequate contrast, and an accessible ordered-list alternative. Never use color alone.

### Practice and reassessment

- Authored options, code tracing, or bug identification; no code execution UI.
- Feedback after the relevant submission; do not reveal future answer keys.
- Distinct reassessment question and before/after evidence counts, including unchanged/worse outcomes.
- A lesson or repeated correct answer must not display an automatic mastery increase.

### Reliability and later mentor work

- Loading, empty, invalid-input, insufficient-evidence, `429`, dependency failure, and exhausted-catalog states.
- Explicit prerecorded-example banner and versions whenever the fallback is shown.
- Responsive mobile/desktop layouts, reduced-motion support where needed, semantic labels, and usable focus states.
- Mentor preview, feedback controls, account UI, and CSV import appear only when their P1 backend/authorization workflows exist.

---

## 17. Planned repository structure

```text
learngraph-ai/
├── frontend/
│   ├── app/
│   ├── components/              # dashboard, graph, diagnosis, practice, UI
│   ├── lib/                     # API contract, local sandbox, version handling
│   ├── public/examples/         # labeled prerecorded outputs; no secrets
│   ├── tests/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint verified on host
│   │   ├── api/v1/
│   │   ├── core/                # configuration, errors, shared quotas
│   │   ├── db/
│   │   ├── schemas/
│   │   └── services/            # grading, replay, estimates, graph, plans
│   ├── migrations/
│   ├── tests/
│   ├── pyproject.toml           # runtime/dev dependencies, pinned runtime
│   └── deployment config       # only the verified host configuration
├── curriculum/
│   ├── concepts.json
│   ├── prerequisite_edges.json
│   ├── activities.json         # authored source; grading stays server-side
│   └── versions.json
├── data/
│   ├── synthetic/              # compact canonical demo seeds
│   ├── raw/                    # ignored
│   ├── processed/              # ignored
│   └── README.md
├── research/
│   ├── notebooks/
│   └── requirements.lock       # separate offline dependencies
├── evaluation/
│   ├── scenarios/              # independent benchmark/holdout definitions
│   ├── manifests/
│   └── results/                # compact measured metrics and plots
├── scripts/                    # graph validation, generation, seeding, evaluation
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   ├── model_card.md
│   ├── evaluation.md
│   └── deployment.md
├── .github/workflows/ci.yml
├── .env.example
├── .gitignore
├── README.md
└── PROJECT.md
```

This is a plan, not a claim that these files already exist. Create folders as their phase needs them. Configure monorepo shared-source inclusion deliberately; deployment checks must prove the backend bundle can access its versioned curriculum without packaging research data. Optional local Docker files may be added later.

---

## 18. Implementation roadmap

All tasks below are planned and unchecked. No provider provisioning or deployment has been performed by this document revision.

### Phase 0 — Freeze the focused product and data contracts

- [ ] Review the 12 canonical concepts, entry assumptions, definitions, and proposed prerequisite edges.
- [x] Resolve OPEN-01 with the 72-question decision and a tested two-concept fresh-item trace; full catalog authoring remains pending.
- [ ] Validate IDs, edge direction, graph acyclicity, and topic-versus-skill separation.
- [ ] Define activity roles, authored grading, event/replay rules, and version/digest contracts.
- [ ] Review initial evidence thresholds, diagnosis factors, recommendation rules, and exhaustion behavior.
- [ ] Define immutable demo seeds, browser isolation/reset, and unavailable-service behavior.
- [ ] Plan the 72 questions and short lessons; author a small first slice before the deployment check.
- [ ] Freeze benchmark split/labeling principles and the P0/P1/P2 boundary.
- [ ] Record the strict ₹0 provider policy and planned request/retention limits.

**Exit condition:** A reviewed graph, data dictionary, initial content slice, API contract, and testable acceptance criteria exist. OPEN-01 is resolved with a feasible fresh practice/reassessment trace. Parameters are marked as initial hypotheses.

### Phase 1 — Verify free deployment before full implementation

- [ ] Initialize the repository and minimal Next.js/FastAPI projects with supported pinned versions and lockfiles.
- [ ] Configure separate frontend/backend Vercel Hobby projects from their correct root directories; verify personal noncommercial scope and no paid billing.
- [ ] Create the planned Supabase Free project, apply only initial canonical-data/quota migrations, and seed the small versioned slice.
- [ ] Verify the FastAPI entrypoint, production runtime/bundle size, shared-source inclusion, and excluded research dependencies.
- [ ] Test browser → API → pooled database → JSON response, including production CORS and environment variables.
- [ ] Implement `/health`, `/ready`, minimal shared quotas, and a labeled static example/failure state.
- [ ] Measure cold/warm behavior, request bounds, database connections, and current free-plan limits.
- [ ] Test Render Free only if the default measured API path fails; keep all alternatives at ₹0.
- [ ] Document exact deployment and recovery steps without secret values.

**Exit condition:** A minimal public frontend/API/database round trip works on verified free plans. There is a measured viable live path before substantial feature work; fallback-only examples do not pass this gate.

### Phase 2 — Build and evaluate the deterministic baseline locally

- [ ] Implement server grading, strict event validation, replay/deduplication, and semantic input digests.
- [ ] Implement first-response evidence rules, estimates, evidence states, and no-data display behavior.
- [ ] Implement bounded graph traversal, target/prerequisite candidates, scoring, alternatives, and abstention.
- [ ] Implement assessment/remediation modes, prerequisite readiness, ranking, and catalog-exhaustion handling.
- [ ] Build reproducible synthetic histories and independent benchmark scenarios with frozen splits.
- [ ] Run prefix-based predictive evaluation and initial diagnosis/recommendation comparisons.
- [ ] Test duplicate/conflicting events, unknown tags, cycles, hints/retries, sparse evidence, and deterministic outputs.

**Exit condition:** A CLI can reproduce baseline estimates, diagnoses, plans, and measured evaluation from versioned inputs. No BKT, LLM, or hosted training is required.

### Phase 3 — Ship one complete live learning loop

- [ ] Implement the P0 profile/seed/analyze API and single consistent analysis response.
- [ ] Build a minimal learner view and an isolated browser sandbox with refresh/resume/reset.
- [ ] Complete one full diagnostic → supported diagnosis or evidence request → practice → distinct reassessment flow.
- [ ] Show evidence counts, alternatives, before/after results, and unchanged-estimate explanations.
- [ ] Add idempotent client retries, pending states, response-order protection, and same-browser tab updates.
- [ ] Verify the deployed flow with two separate browser contexts and without any LLM key.

**Exit condition:** A visitor completes the real live loop without developer intervention, refreshes without losing local progress, and cannot change another browser's sandbox or the canonical seeds.

### Phase 4 — Complete P0 content and learner experience

- [ ] Finish and review all 72 distinct questions and linked lessons across 12 concepts.
- [ ] Seed all four contrasting learner profiles and their versioned histories.
- [ ] Add dashboard, prerequisite graph/list, diagnosis detail, plan locks, and reassessment view.
- [ ] Cover unknown, early, ambiguous, no-supported-gap, no-suitable-item, and catalog-exhausted states.
- [ ] Add mobile, keyboard, contrast, focus, loading, error, and reduced-motion handling.
- [ ] Produce versioned prerecorded example views and public methodology/limitations pages.

**Exit condition:** All P0 features work across the full authored catalog; sparse/noisy profiles and accessibility states are represented honestly.

### Phase 5 — Release verification, evaluation, and cost recovery

- [ ] Run the critical browser/API tests and backend/frontend CI checks on standard free runners.
- [ ] Confirm immutable seeds, retry invariance, atomic quota behavior, bounded requests, and version-mismatch handling.
- [ ] Test `429`, API failure, unavailable quota storage/database, cold start/restart, and static-example fallback.
- [ ] Verify no credential leaks, premature answer disclosures in normal API/UI responses, privileged public writes, raw datasets, or research dependencies in runtime artifacts.
- [ ] Re-run the frozen P0 evaluation; publish actual metrics, sample counts, split manifests, limitations, and model card.
- [ ] Exercise restore/reseed from authored sources and verify version hashes; document manual backup/recovery.
- [ ] Recheck provider terms, zero-payment settings, quotas shared across projects, storage retention, and live public URLs.
- [ ] Run the entire deployed loop from a clean browser and complete the Section 19 release checklist.

**Exit condition:** Every P0 release criterion passes, a viable free live demo exists, and dependency/quota failures degrade clearly without enabling charges.

### Phase 6 — Portfolio presentation and optional P1 product work

- [ ] Publish README, architecture diagram, setup/deployment instructions, screenshots, and a two-to-three-minute walkthrough.
- [ ] Explain measured baseline results, synthetic-data limits, free-hosting trade-offs, and the absence of causal/learning-gain claims.
- [ ] Add optional export, feedback, or read-only synthetic mentor/evaluation views one at a time.
- [ ] Treat CSV import and accounts/server persistence as separately tested features with their full provenance/security requirements.
- [ ] Before accounts, choose a complete verified free login flow, retention/deletion/export design, and durable ownership/idempotency model.
- [ ] Before real mentor access, implement assignments, access checks, audit records, and cross-user denial tests.

**Exit condition:** The portfolio can be understood, used, and independently reproduced. Optional P1 features do not block or destabilize the completed P0 release.

### Phase 7 — Optional P2 research

- [ ] Add offline BKT with a comparable prediction protocol and publish gains or lack of gains honestly.
- [ ] Consider a licensed EdNet subset as a separate experiment; keep its claims distinct from DSA diagnosis.
- [ ] Test recency/difficulty changes against the frozen baseline before promotion.
- [ ] Add optional free-tier Gemini wording only behind a disabled-by-default flag, strict limits, and template fallback.
- [ ] Consider DKT, cohort analysis, or expanded curricula only when data/local compute and free deployment constraints permit.

**Exit condition:** Each experiment has a reproducible independent report and remains optional. No paid runtime or experiment is introduced.

---

## 19. P0 release acceptance criteria

### Free public deployment

- [ ] A clean browser can open the public frontend and reach the actual API/database path.
- [ ] The setup uses free plans and included subdomains with no paid billing, purchased resources, or trial-credit dependency.
- [ ] Runtime bundle/dependency limits and cold/warm behavior were measured and documented.
- [ ] Quota/dependency exhaustion returns a controlled state without a paid fallback.
- [ ] Labeled prerecorded examples remain accessible when live analysis is unavailable; they are never presented as live results.

### Content, isolation, and live loop

- [ ] Four contrasting synthetic profiles and 12 canonical concepts are available.
- [ ] The 72 authored questions have valid primary tags, roles, grading, and versions; lessons remain ungraded context.
- [ ] Prerequisite edges reference known nodes, contain no cycles, and render in the correct direction.
- [ ] Two separate browser contexts have independent progress; neither can modify canonical seeds.
- [ ] Refresh restores local progress; reset restores only that local profile; unavailable storage produces a clear session-only notice.
- [ ] The visitor can answer a question, inspect the result, practice, and take a different same-skill reassessment.
- [ ] Dashboard history, estimates, diagnosis, and plan correspond to the same acknowledged input digest and versions.
- [ ] Pending/failed requests never look accepted; late responses cannot overwrite newer analysis.

### Evidence and algorithms

- [ ] A concept with no evidence shows `not_assessed`, not a 50% mastery claim.
- [ ] Unknown prerequisites generate evidence requests; only qualifying evidence supports a weakness diagnosis.
- [ ] Identical event/request retries do not add evidence; conflicting IDs and invalid ordering return documented errors.
- [ ] Hinted responses, repeated questions, lessons, and secondary tags follow the declared evidence policy.
- [ ] A diagnosis includes actual evidence IDs, paths, alternatives, versions, and a nonprobabilistic evidence-strength label.
- [ ] Ambiguous/sparse cases can abstain; secure prerequisites do not get automatically blamed for a target failure.
- [ ] Plans contain valid IDs, honor readiness and prerequisite order, and stop honestly when fresh activities are exhausted.
- [ ] New distinct eligible evidence can update estimates; lesson completion and memorized retries do not invent improvement.
- [ ] The complete application works with no LLM configuration.

### Quality, evaluation, and recovery

- [ ] Backend tests, frontend checks/build, and critical deployed browser-flow checks pass.
- [ ] Cross-instance quota tests confirm atomic enforcement; oversized requests, `429`, and failed quota storage are handled.
- [ ] Prefix-based evaluation uses no future answers or test-fitted parameters; independent holdout scenarios remain untouched by tuning.
- [ ] Public baseline comparisons contain real metrics, counts, seeds, split/config versions, and limitations; BKT is not required.
- [ ] No credentials, real student data, or large research data are publicly exposed; normal API/UI responses withhold answers until feedback is due. Public authored source is not treated as a secret examination bank.
- [ ] Mobile and keyboard flows are usable and graph information has a non-color, non-pointer alternative.
- [ ] Restore/reseed and version mismatch behavior are exercised; local setup and deployment documentation match the actual application.

---

## 20. Risks and mitigation

| Risk | Mitigation |
| --- | --- |
| Free provider changes, pauses, or rejects the workload | Verify early, recheck before release, reduce scope or suspend live features; no paid upgrade. |
| API/database quota exhaustion or abuse | Shared atomic limits, bounded work, cached metadata, visible `429`/unavailable states, and usage checks. |
| Supabase inactivity and lack of free automatic backups | Authored canonical sources, manual restore/reseed procedure, version hashes, and bundled examples. |
| A static fallback hides a broken application | Label it explicitly and require the actual live loop to pass release criteria. |
| Shared mutable demo or forged browser history | Immutable seeds, browser-local sandbox, server grading/replay, and explicit unverified-demo labeling. |
| Sparse or ambiguous evidence | Separate unknown/early states, collect diagnostics, and abstain instead of blaming ancestors. |
| Overstated mastery, certainty, or causation | Observed-performance language, counts, heuristic evidence labels, alternatives, and no causal probability. |
| Repeats/hints inflate results | First-response eligible-question policy and distinct reassessment items. |
| Synthetic benchmark rewards its own generator | Independent scenarios/variants, untouched splits, robustness tests, and limited claims. |
| Small catalog runs out or cannot resolve a skill | Explicit exhaustion/review states; expand authored content only after the loop is validated. |
| Privileged database access bypasses RLS | Least-privilege runtime access, explicit authorization design, and denial tests before owned records. |
| Runtime bundle grows with research code/data | Separate dependency sets and measured production builds; no hosted training. |
| LLM adds cost or unsupported claims | Disabled P2 feature, verified free access only, strict inputs/limits, and templates. |
| Product scope expands before shipping | P0 release gate; accounts, mentor access, BKT, and imports remain separate milestones. |
| Weak external validation | Present a prototype, seek feedback, and avoid claiming verified platform gaps or learning gains. |

---

## 21. Portfolio differentiation

Demonstrate the complete, testable loop and explain decisions a reviewer can verify:

- Why correctness alone does not identify the source of a mistake.
- How prerequisite traversal helps and when the system declines to diagnose.
- How unknown concepts differ from supported weaknesses.
- How retries, hints, multiple tags, and distinct reassessment affect evidence.
- How the baseline is evaluated without future-answer leakage.
- How the application stays useful during free-service interruptions.
- How frontend, API, database, and local research boundaries fit together.

Suggested resume wording, only after implementation:

> Built LearnGraph AI, an explainable learning-diagnostics prototype combining observed-performance estimates and prerequisite graphs to recommend targeted assessment and practice; deployed a Next.js/FastAPI portfolio demo with PostgreSQL and reproducible baseline evaluation.

Add measured metrics only after experiments. Mention BKT or other advanced models only if actually implemented and evaluated.

---

## 22. Implementation and cost decisions

| Decision | Agreed default |
| --- | --- |
| Budget | Strict ₹0 / $0 recurring services; no paid subscriptions, APIs, GPU, domains, auto-top-ups, or trial-credit dependency. |
| Frontend | Next.js/TypeScript/Tailwind on Vercel Hobby. |
| API | Lightweight FastAPI on a second Vercel Hobby project, verified early; Render Free is an alternative only. |
| Database | Supabase Free for canonical data and quotas; visitor history stays local for P0. |
| Curriculum | 12 recursion/introductory-DP concepts, 72 distinct questions, short lessons, and four synthetic profiles. |
| Graph | Reviewed prerequisite DAG with canonical IDs; no graph database. |
| Baseline | Transparent observed-performance estimate and explicit evidence eligibility/states. |
| Live consistency | Bounded stateless replay, deterministic grading/deduplication, and one versioned analysis bundle. |
| Explanations | Templates only in P0. |
| Research | Local generation/evaluation; BKT/EdNet/DKT optional after release. |
| Accounts/mentors | Deferred until complete free authentication, ownership, retention, and authorization designs exist. |
| CI | GitHub standard runners for a public repository, with bounded artifacts/caches. |
| Failure policy | Clear unavailable states and labeled bundled examples; never automatically enable payment. |

The demo is designed to operate at ₹0 within available free quotas. This is not a promise of uninterrupted uptime, unlimited usage, or permanent provider terms. A commercial service or real student deployment requires a separate scope review and must not be silently introduced into this portfolio roadmap.

---

## 23. Official references

- [Vercel FastAPI deployment](https://vercel.com/docs/frameworks/backend/fastapi)
- [Vercel Hobby plan and allowances](https://vercel.com/docs/plans/hobby)
- [Vercel function limits](https://vercel.com/docs/functions/limitations)
- [Vercel pricing and Hobby eligibility](https://vercel.com/pricing)
- [Render free deployment and restrictions](https://render.com/docs/free)
- [Supabase pricing, pausing, and backup availability](https://supabase.com/pricing)
- [Supabase connection methods and pooling](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Supabase Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Supabase default SMTP restrictions](https://supabase.com/docs/guides/auth/auth-smtp)
- [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
- [EdNet dataset and license](https://github.com/riiid/ednet)
- [Gemini pricing and free-tier conditions](https://aistudio.google.com/docs/pricing)
- [FastAPI](https://fastapi.tiangolo.com/)
- [NetworkX](https://networkx.org/documentation/stable/)
- [scikit-learn](https://scikit-learn.org/stable/)
- [Next.js](https://nextjs.org/docs)
- [React Flow](https://reactflow.dev/)

---

**Project principle:** Prove the smallest complete diagnosis/practice/reassessment loop, evaluate it honestly, and deploy within the strict free-service budget before expanding scope.
