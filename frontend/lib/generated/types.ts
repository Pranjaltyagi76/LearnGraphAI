// Generated from frozen protocol v1. Run python -m scripts.generate_browser_contracts.
export type AnalysisBundle = {
  accepted_visitor_events: number;
  contract_version: 1;
  diagnosis: Diagnosis;
  digest_algorithm: "sha256-lg-c14n-v1";
  estimates: Array<Estimate>;
  focus_concept_id: string;
  graded_events: Array<GradedEvent>;
  history_digest: string;
  local_revision: number;
  persisted: false;
  plan: Plan;
  profile_id: string;
  requested_trigger_event_id: (string | null);
  sandbox_id: string;
  versions: Versions;
};

export type AnalyzeRequest = {
  contract_version: 1;
  events: Array<(ResponseEvent | LessonEvent)>;
  focus_concept_id: string;
  local_revision: number;
  profile_id: string;
  sandbox_id: string;
  trigger_event_id?: (string | null);
  versions: Versions;
};

export type Diagnosis = {
  alternatives: Array<"item_difficulty" | "response_error" | "tag_mismatch" | "mixed_evidence">;
  candidates: Array<GapCandidate>;
  evidence_requests: Array<EvidenceRequest>;
  status: "supported_gap" | "insufficient_evidence" | "ambiguous" | "no_supported_gap" | "no_failed_trigger";
  trigger_event_id: (string | null);
};

export type DiagnosisSummary = {
  all_cases: number;
  baseline: "lowest_estimate" | "prerequisite_aware";
  coverage: number;
  false_diagnosis_rate: (number | null);
  labeled_gap_cases: number;
  missing_evidence_cases: number;
  mrr: number;
  no_gap_cases: number;
  no_trigger_cases: number;
  precision_at_1: number;
  precision_at_3: number;
  recall_at_1: number;
  recall_at_3: number;
};

export type ErrorDetail = {
  path: string;
  reason: "required" | "invalid_type" | "invalid_value" | "unknown_reference" | "out_of_range";
};

export type ErrorEnvelope = {
  code: "invalid_request" | "invalid_response" | "invalid_order" | "invalid_timestamp" | "invalid_trigger" | "unknown_activity" | "profile_not_found" | "not_found" | "http_error" | "event_conflict" | "version_mismatch" | "payload_too_large" | "body_timeout" | "quota_exhausted" | "not_configured" | "dependency_unavailable" | "analysis_timeout" | "evaluation_not_published";
  details: Array<ErrorDetail>;
  message: string;
  request_id: string;
};

export type Estimate = {
  concept_id: string;
  distinct_questions: number;
  eligible_count: number;
  estimate: (number | null);
  evidence_event_ids: Array<string>;
  evidence_state: "not_assessed" | "early_estimate" | "supported_estimate";
  last_evidence_at: (string | null);
  performance_state: "unknown" | "early" | "weak" | "developing" | "ready";
  recent_failures: number;
  successes: number;
  total_attempts: number;
};

export type EvaluationSummary = {
  catalog_version: string;
  contract_version: 1;
  diagnosis: Array<DiagnosisSummary>;
  evaluation_version: string;
  graph_version: string;
  limitations: Array<string>;
  measured_at: string;
  model_version: string;
  prediction: Array<PredictionSummary>;
  recommendation: Array<RecommendationSummary>;
  scenario_version: string;
  source_commit: string;
  split_manifest_hash: string;
  synthetic_only: true;
};

export type EvidenceRequest = {
  concept_id: string;
  needed_observations: number;
  reason: "not_assessed" | "early_estimate";
};

export type GapCandidate = {
  concept_id: string;
  distance: number;
  evidence_event_ids: Array<string>;
  path: Array<string>;
  reason: "supported_target_weakness" | "supported_upstream_weakness";
  relation: "target" | "upstream";
  score: number;
};

export type GradedEvent = {
  activity_id: string;
  activity_version: number;
  attempt_number: number;
  catalog_role: "diagnostic" | "practice" | "reassessment" | "lesson";
  concept_id: string;
  eligibility_reason: "eligible" | "repeat_activity" | "hints_used" | "hints_unknown" | "lesson";
  eligible: boolean;
  event_id: string;
  explanation: (string | null);
  is_correct: (boolean | null);
  kind: "response" | "lesson_completed";
  occurred_at: string;
  provenance: "canonical_seed" | "visitor_demo";
};

export type HealthResponse = {
  service: "learngraph-ai-api";
  stage: string;
  status: "ok";
};

export type LessonEvent = {
  activity_id: string;
  activity_version: number;
  assessment_run_id: string;
  event_id: string;
  kind: "lesson_completed";
  occurred_at: string;
  schema_version: 1;
  sequence_number: number;
  time_spent_seconds?: (number | null);
};

export type OptionResponse = {
  option_id: string;
};

export type PendingSubmission = {
  event: (ResponseEvent | LessonEvent);
  focus_concept_id: string;
  request_revision: number;
  trigger_event_id: (string | null);
};

export type Plan = {
  items: Array<PlanItem>;
  mode: "remediation" | "assessment" | "practice" | "none";
  status: "ready" | "blocked" | "catalog_exhausted" | "no_suitable_activity";
};

export type PlanItem = {
  activity_id: string;
  activity_version: number;
  blocked_by_concept_ids: Array<string>;
  concept_id: string;
  depends_on_activity_ids: Array<string>;
  readiness: "ready" | "locked";
  reason: "gap_practice" | "gather_evidence" | "reassessment" | "lesson_support" | "further_practice";
  role: "diagnostic" | "practice" | "reassessment" | "lesson";
  score: number;
};

export type PredictionSummary = {
  baseline: "global_rate" | "concept_smoothed";
  brier: number;
  eligible_predictions: number;
  excluded_events: number;
  log_loss: number;
  negative_outcomes: number;
  positive_outcomes: number;
  pr_auc: (number | null);
  roc_auc: (number | null);
};

export type ProfileInfo = {
  archetype: "upstream_gap" | "target_gap" | "sparse" | "ambiguous";
  focus_concept_id: string;
  id: string;
  name: string;
  summary: string;
  synthetic: true;
};

export type ProfileSeed = {
  archetype: "upstream_gap" | "target_gap" | "sparse" | "ambiguous";
  events: Array<(ResponseEvent | LessonEvent)>;
  focus_concept_id: string;
  name: string;
  profile_id: string;
  seed_id: string;
  seed_version: number;
  summary: string;
  synthetic: true;
};

export type ProfileSummary = {
  archetype: "upstream_gap" | "target_gap" | "sparse" | "ambiguous";
  focus_concept_id: string;
  id: string;
  name: string;
  summary: string;
  synthetic: true;
  versions: Versions;
};

export type ProfilesResponse = {
  contract_version: 1;
  profiles: Array<ProfileSummary>;
};

export type Provenance = {
  attribution: string;
  created_on: string;
  license_status: "not_licensed";
  origin: "original";
};

export type PublicConcept = {
  definition: string;
  group: "recursion" | "dynamic_programming";
  id: string;
};

export type PublicEdge = {
  dependent: string;
  prerequisite: string;
  type: "prerequisite";
};

export type PublicLesson = {
  active: true;
  body: string;
  difficulty: number;
  foundational: boolean;
  id: string;
  kind: "lesson";
  primary_concept_id: string;
  provenance: Provenance;
  role: "lesson";
  secondary_concept_ids: Array<string>;
  title: string;
  version: number;
};

export type PublicOption = {
  id: string;
  text: string;
};

export type PublicQuestion = {
  active: true;
  code: (string | null);
  difficulty: number;
  foundational: boolean;
  id: string;
  kind: "question";
  options: Array<PublicOption>;
  primary_concept_id: string;
  prompt: string;
  provenance: Provenance;
  question_type: "multiple_choice" | "code_tracing" | "bug_identification";
  role: "diagnostic" | "practice" | "reassessment";
  secondary_concept_ids: Array<string>;
  version: number;
};

export type ReadyResponse = {
  release_id: string;
  status: "ready";
};

export type RecommendationSummary = {
  baseline: "random_eligible" | "lowest_estimate" | "prerequisite_aware";
  cases: number;
  catalog_validity: (number | null);
  emitted_items: number;
  exhaustion_cases: number;
  exhaustion_honesty: (number | null);
  prerequisite_checks: number;
  prerequisite_validity: (number | null);
  reassessment_distinctness: (number | null);
  reassessment_items: number;
};

export type ReleaseSummary = {
  catalog_version: string;
  contract_version: 1;
  graph_version: string;
  model_version: string;
  profiles_version: string;
  release_hash: string;
  release_id: string;
};

export type ResponseEvent = {
  activity_id: string;
  activity_version: number;
  assessment_run_id: string;
  event_id: string;
  hints_used?: (number | null);
  kind: "response";
  occurred_at: string;
  response: OptionResponse;
  schema_version: 1;
  sequence_number: number;
  time_spent_seconds?: (number | null);
};

export type SandboxRecord = {
  acknowledged_events: Array<(ResponseEvent | LessonEvent)>;
  analysis_history_digest: (string | null);
  analysis_input_revision: (number | null);
  key: string;
  last_analysis: (AnalysisBundle | null);
  pending: (PendingSubmission | null);
  persistence: "indexeddb" | "session";
  profile_id: string;
  revision: number;
  sandbox_id: string;
  schema_version: 1;
  versions: Versions;
};

export type SeedResponse = {
  activities: Array<(PublicQuestion | PublicLesson)>;
  concepts: Array<PublicConcept>;
  contract_version: 1;
  edges: Array<PublicEdge>;
  profile: ProfileInfo;
  seed_events: Array<(ResponseEvent | LessonEvent)>;
  versions: Versions;
};

export type Versions = {
  catalog_version: string;
  graph_version: string;
  model_version: string;
  release_hash: string;
  release_id: string;
  seed_id: string;
  seed_version: number;
};
export type Event = ResponseEvent | LessonEvent;
