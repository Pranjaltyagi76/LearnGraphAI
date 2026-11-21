# Protocol v1 freeze — 20 November 2026

**State:** implemented by the Phase 2 engine/evaluator and activated through the verified Phase 3 API/browser loop. Legacy bootstrap routes remain compatible. Python models in [contracts.py](../backend/app/contracts.py) and generated JSON Schemas in this directory define structural types; the semantic rules here remain mandatory. The active `phase1-v1` bootstrap release retains its existing shape and content. No visitor history is stored server-side.

## Compatible release and publication

The reviewed draft is `learngraph-review-v1`: graph `graph-v1`, catalog `catalog-slice-v1`, model/config `baseline-v1`, and four individually versioned seeds. [release-manifest.json](release-manifest.json) binds exact runtime-artifact SHA-256 hashes and a compatible version tuple. Its frozen file manifest retains reviewed-draft provenance; Phase 3 has separately published and activated the exact package bytes in the immutable database row. [Publication evidence](../context/evidence/phase3_release.json).

Artifact hashes are SHA-256 over file bytes with LF line endings enforced by .gitattributes. `release_hash` hashes only the manifest's `identity` object using lg-c14n-v1, excluding status/review dates and the hash itself. Identity includes release/contract versions and each artifact's path/hash. Publication copies one fully validated compatible package into a **new** immutable release; future analysis activation uses a separate `ANALYSIS_RELEASE_ID`, followed by deployment and verification. Legacy `RELEASE_ID=phase1-v1` remains compatible with the bootstrap preview. No mutation, partial activation, or automatic history migration. Retain previous compatible artifacts for rollback. The new graph cannot be silently paired with legacy seeds.

## Routes and rollout compatibility

The existing `/api/v1/demo/profiles`, `/api/v1/demo/profiles/{id}/seed`, and `/api/v1/bootstrap/answer` keep their Phase 1 shapes/release while the current preview uses them. Do not change their response schema during analysis activation. The first full-analysis protocol uses new routes:

| Route | Success schema |
| --- | --- |
| GET /api/v1/demo/release | ReleaseSummary: active analysis release pointer; no-store. |
| GET /api/v1/releases/{release_id}/profiles | ProfilesResponse: full immutable version references per profile. |
| GET /api/v1/releases/{release_id}/profiles/{profile_id}/seed | SeedResponse: selected versions, canonical events and safe public content. |
| POST /api/v1/demo/analyze | AnalyzeRequest → AnalysisBundle. |
| GET /api/v1/analytics/evaluation | EvaluationSummary only after an actual measured artifact is published; otherwise 404 evaluation_not_published. |

HealthResponse and ReadyResponse preserve the existing liveness/readiness structures. [index.json](index.json) maps schema references and implementation status. The Phase 0 review did not implement routes; Phase 3 now implements and deploys all five new routes. Handlers accept only the configured active analysis tuple; future deliberately retained compatible analysis versions must be explicit. As specified, unsupported tuples return 409, never silent rescoring. A client pins the release returned by the pointer and uses release-scoped reads for its session. Roll out backend support before the new frontend; retained Phase 1 routes keep older browser assets working. Full-analysis breaking changes require a new contract/path major version, not an in-place schema replacement.

## Request and event dictionary

`POST /api/v1/demo/analyze` accepts `AnalyzeRequest`: contract version, full `versions`, profile ID, focus concept, sandbox UUID, local revision, optional trigger UUID, and the complete visitor event prefix. No canonical seed array, grade, tags, difficulty, role, provenance, or error-label field is accepted from visitors. All nested objects reject unknown fields.

| Field | Frozen rule |
| --- | --- |
| Version/ID fields | Required, case-sensitive lowercase ASCII IDs, maximum 80 characters. Seed/activity versions are positive integers. Release hash is 64 lowercase hex characters. |
| UUID fields | Hyphenated UUID v4 or v5; normalize hexadecimal letters to lowercase. Browser IDs use v4; deterministic authored fixtures use v5. |
| Local revision | Integer 0 through 2^53−1; echoed for stale-response protection, not evidence or digest identity. |
| Event kind | `response` or `lesson_completed`, discriminated by `kind`; schema version is integer 1. |
| Event sequence | Positive integer; canonical seed and visitor streams each start at 1. Seed precedes visitor stream. |
| Response | Catalog option ID only, 1–8 lowercase ASCII characters. Every option/activity/version reference must exist in the selected catalog. |
| Hints | Integer 0–100 or null. Missing becomes null, never zero. Lesson events cannot carry a response or hint count. |
| Elapsed time | Integer seconds 0–86,400 or null; missing becomes null. Context only, never a performance feature. |
| Assessment run | Required UUID grouping submissions into a browser-selected practice cycle; not a verified server receipt or proof of readiness. |
| Occurrence time | Explicit RFC3339 timezone, 0–3 fractional digits; normalize to UTC milliseconds. Reject naive/invalid dates, leap seconds, and finer precision rather than truncating. |

Raw visitor array ≤200 before deduplication; canonical seed ≤100; request body ≤262,144 UTF-8 bytes independently of event count, including chunked input. Strings and response lists have model bounds. Integers reject booleans, strings, and fractional values. NaN/infinity are not valid JSON or permitted measurements.

Deduplicate by normalized event UUID and **complete normalized payload**, keeping first occurrence order. Identical duplicates disappear; changed option, sequence, run, timestamp, hints, or timing under the same ID is `409 event_conflict`. Explicit null and omitted optional metadata are identical. After deduplication, require visitor sequence 1..N with no gaps/repeats and nondecreasing UTC occurrence times. Never sort malformed history into validity. Seed IDs and visitor IDs must be disjoint.

Every visitor timestamp must be strictly after the selected seed's final timestamp and at most receipt time +300 seconds. No historical-age cutoff. Receipt time is an explicit admission argument, excluded from scoring and hashes. An unchanged previously admitted prefix remains valid as ordinary time advances. A clock-ahead error asks the visitor to correct the device clock; never silently rewrite a pending event or skip events. Timestamp order/skew checks apply to complete history, not only the newest event.

## Deterministic semantic identity

lg-c14n-v1 uses UTF-8 JSON, ASCII object keys sorted lexicographically, no whitespace/BOM/newline, `ensure_ascii=false`, and no nonfinite values. Semantic input has only safe integers, booleans, nulls, strings and arrays/objects; no floating-point number enters this digest. Strings in this input are ASCII IDs/UUIDs/normalized timestamps. Display text and authored numeric difficulty are not serialized here; the release hash binds their source files.

Hash `{contract_version, versions, profile_id, focus_concept_id, trigger_event_id, events}` after normalization/deduplication. Preserve event-array order. Optional metadata is explicit null. Include timing/hints/run IDs because they are part of the submitted event identity even where they do not affect scores. Exclude sandbox UUID, local revision, request UUID, receipt time, network/client identifiers, server timings and response wording. Returned `history_digest` is lowercase SHA-256 with algorithm name `sha256-lg-c14n-v1`.

An omitted/null trigger hashes as null and is resolved deterministically to the most recent failed response for the focus concept in seed+visitor replay. An explicit trigger must reference an actual failed response with that primary concept, or return `422 invalid_trigger`. If none exists, return `no_failed_trigger`; estimates and evidence requests remain valid. Explicit and automatic trigger selection are different request identities even if they choose the same event. No wall-clock recency feature exists.

## Authoritative evidence and policy

[PROJECT.md §8](../PROJECT.md) owns the formulas; [model-config.v1.json](../curriculum/model-config.v1.json) freezes parameters. Grade from the selected catalog, replay seed before visitor history, and keep all-attempt context. The first response to each activity ID consumes that question's first-response slot even if hints are positive or unknown. Later unhinted retries cannot rescue it. Activity-version conflicts are rejected, not counted as a new question. Only the primary concept receives an observation; lessons and secondary tags contribute none.

For n=0, public estimate is null and state `not_assessed`; the internal prior must not become a displayed 50% mastery. n=1..2 is `early_estimate`; n≥3 is `supported_estimate`. Weak is strictly below 0.45; ready is at least 0.65; the supported interval in between is developing. These are initial policy cutoffs, not calibrated educational probabilities.

For a failed trigger, include target plus ancestors within three edges. Candidate path is prerequisite→...→target, selecting a shortest path and then lexicographically smallest full path on ties. Rank only supported weak candidates with ≥2 failures among the latest three eligible distinct responses. Use the PROJECT score, exact rational arithmetic (authored decimal difficulty parsed from its decimal representation), then distance and concept ID. Round scores/estimates to six decimal places **only for output**, never before ranking or threshold comparisons. At most three candidates; count strength and scores are not confidence/causality probabilities.

Diagnosis precedence: any qualifying candidate → `supported_gap`; otherwise any unknown/early candidate → `insufficient_evidence`; otherwise supported mixed evidence or a weak estimate failing the recent-failure gate → `ambiguous`; otherwise → `no_supported_gap`. No failed trigger takes precedence over ranking. Unknown/early evidence requests are returned separately even when supported gaps exist. Do not infer a specific misconception from the synthetic archetype/labels. Alternatives are generic possibilities, not observed facts.

## Recommendation, readiness, and exhaustion

Choose remediation if supported gaps exist; otherwise assessment for missing evidence; otherwise further practice. A plan has ≤5 items, respects graph topological order (lexicographic Kahn tie-break), then descending activity score and activity ID within each concept/stage. Select at most one optional support lesson, up to two fresh practice questions, and one fresh reassessment per chosen concept before filling another gap; respect the global five-item cap. Prioritize earlier prerequisites if slots are insufficient.

All questions are active/version-matched and unused anywhere in seed+visitor responses, even if their earlier response was hinted/ineligible. Lessons can be reread but only one instance of an activity ID appears per plan; do not automatically reinsert a lesson already completed in the current practice cycle. For ranking novelty/repetition only, an activity occurring in any event (including lesson completion) is seen. This never gives a lesson correctness evidence. Gather additional observations with unused diagnostic first, then unused practice; one diagnostic alone does not provide three observations. No unassessed concept is declared weak merely to create a recommendation.

Remediation/further-practice/reassessment requires every **direct prerequisite** to have supported estimate ≥0.65. Diagnostics may assess an unknown concept when foundational or its direct prerequisites are ready; otherwise gather upstream/root evidence first. Later supporting steps may be shown locked, but an earlier lesson or merely planned answer never unlocks them. Recompute after each response; direct requirements are checked again. Lessons may be read without claiming measured prerequisite readiness.

Reassessment never requires its **own concept** to cross 0.65: that would prevent measuring a weak skill. A claimed completed reassessment cycle requires an unused same-primary-skill reassessment, different from practice, with at least one prior fresh practice response in the same assessment run after the cycle's failure/diagnostic anchor. Practice need not be correct. A seed failure may anchor a later visitor run. These are workflow/display predicates, not extra exclusions from the baseline first-response rule. Valid answers submitted outside a recommended order can still be graded; browser-controlled history is not proof that a plan was followed.

Return `catalog_exhausted` when the needed fresh question pool is empty, `no_suitable_activity` for uncovered skills/roles, and `blocked` when readiness prevents available items. Nonempty usable prefixes may accompany an exhausted/blocked plan; never claim a complete fresh loop without its distinct reassessment. Offer clearly labeled review, not new evidence. Lesson completion and item count do not guarantee threshold crossing.

Ready means at least one currently permitted question action exists; readable lessons alone do not override blocked/exhausted question status. Readiness checks include **all direct parents**, even if a fixture DAG puts one outside the diagnosis radius. Mark that item blocked and identify the parent; do not ignore its evidence or recursively expand beyond the three-edge diagnosis bound. The visitor can choose that parent as a new focus.

## Response consistency and errors

One `AnalysisBundle` echoes versions/profile/focus/sandbox/revision, requested_trigger_event_id (including null), digest, all graded seed+visitor events, twelve estimates, diagnosis/evidence requests, and plan. Diagnosis.trigger_event_id is the resolved failed event and may differ from an automatic/null request selector. `persisted=false` states no shared visitor write. Accepted visitor count is deduplicated length. Feedback is present only for submitted activities; future public catalog projection excludes correct options and question explanations. Domain validation must check counts, unique concepts, actual event/path/catalog references, grades, formula consistency, topological order and readiness in addition to JSON Schema.

Return graded events in seed-then-visitor order, estimates by concept ID, evidence IDs in eligible chronology, evidence requests in lexicographic topological order, and candidates/plans in the policy order above. Generic alternatives have fixed order item_difficulty, response_error, tag_mismatch, mixed_evidence when applicable. Never depend on hash-set/database iteration order. A cached bundle must match the acknowledged history digest; pending focus/trigger selectors are persisted so refresh reconstructs the same request.

| HTTP | Codes / behavior |
| --- | --- |
| 404 | `profile_not_found`, `not_found`; evaluation route uses `evaluation_not_published` until a measured artifact exists. |
| 408 / 413 | `body_timeout` / `payload_too_large`; bounded byte receiver before parsing/replay. |
| 409 | `version_mismatch` for incompatible/unknown version/hash tuples; `event_conflict` for conflicting IDs. No partial acceptance. |
| 422 | `invalid_request`, `invalid_order`, `invalid_timestamp`, `unknown_activity`, `invalid_response`, `invalid_trigger`. Do not retry unchanged invalid data. |
| 429 | `quota_exhausted`; positive integer `Retry-After` seconds (1–86,400). Shared atomic quota is mandatory. |
| 503 | `not_configured`, `dependency_unavailable`, `analysis_timeout`. Never bypass unavailable quota storage. |

Errors use `{code,message,request_id,details}`; ≤10 safe `{path,reason}` details, never raw submitted values/DSNs/stack traces. When present, HTTP `X-Request-ID` equals the envelope UUID; early body-receiver failures can precede context/timing headers. Readiness is bounded and reveals no credentials. API responses use no-store and exact CORS.

Ordering: enforce raw body/schema bounds → reserve quota → validate release/profile and load immutable inputs → deduplicate/order/reference/timestamp validation → grade/derive/analyze → validate complete response → return. Reserved attempts, semantic validation failures and retries consume quota; no refunds. Zero automatic POST retries; one in-flight submission per sandbox. The browser uses a 15-second deadline and an explicit retry action with the same snapshot/event IDs, honoring `Retry-After`.

## Normative and implementation references

- [Pydantic strict validation](https://docs.pydantic.dev/latest/concepts/strict_mode/) and [JSON Schema generation](https://docs.pydantic.dev/latest/concepts/json_schema/): structural schema, with semantic constraints documented above.
- [Storage state machine](../context/browser_storage.md), [curriculum review](../curriculum/review.md), and [benchmark definition](../evaluation/readme.md).
- Generated schemas and golden fixtures are checked in CI. They originally froze structure only. Phase 2/3 now provide the tested engine, actual benchmark, deployed endpoint and browser store; the current evidence is linked from the roadmap.

## Phase 4 compatible release rollout

Protocol/schema/policy remain unchanged. The separately frozen [full-v1 manifest](releases/full-v1.json) selects `catalog-full-v1` and `demo-profiles-full-v1` under `learngraph-full-v1`. It keeps every slice activity value/version unchanged. The runtime supports the active full release and explicitly retained `learngraph-review-v1`, with a two-package maximum and allowlisted artifact sets. Unsupported IDs still return 409. Browser keys isolate the release/hash/seed tuples; explicit old-release navigation never migrates history. Legacy `RELEASE_ID=phase1-v1` routes keep their original contracts.

Full-v1 has no compatible full-catalog quality summary, so the active evaluation endpoint returns `404 evaluation_not_published`; no old slice score is relabeled. The actual original summary remains in the immutable reviewed package.
