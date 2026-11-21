import type { AnalysisBundle, SeedResponse } from "@/lib/protocol";

export const label = (value: string) => value.replaceAll("_", " ");

export function LearningEvidence({ bundle, seed }: { bundle: AnalysisBundle; seed: SeedResponse }) {
  const focus = bundle.estimates.find((e) => e.concept_id === bundle.focus_concept_id)!;
  const original = bundle.graded_events.filter((e) => e.provenance === "canonical_seed" &&
    e.concept_id === focus.concept_id && e.eligible);
  return <>
    <section className="learn-panel" aria-labelledby="evidence-title">
      <div className="panel-kicker">01 / THE EVIDENCE</div>
      <h2 id="evidence-title">What the responses tell us</h2>
      <div className="evidence-summary">
        <div><span className="metric-value">{focus.estimate === null ? "—" : `${(focus.estimate * 100).toFixed(1)}%`}</span>
          <span>Smoothed observed correctness</span></div>
        <div><span className="metric-value">{focus.successes}<small> / {focus.eligible_count}</small></span>
          <span>Eligible correct responses</span></div>
      </div>
      <p className="state-pill">{label(focus.evidence_state)} · {label(focus.performance_state)}</p>
      <p className="learn-muted">Seed evidence: {original.filter((e) => e.is_correct).length}/{original.length} correct.
        Current evidence: {focus.successes}/{focus.eligible_count} correct across distinct eligible questions.
        Lessons and retries add no observations. A changed estimate does not prove learning.</p>
      <details><summary>All twelve concepts</summary><ul className="concept-evidence">
        {bundle.estimates.map((e) => <li key={e.concept_id}><span>{label(e.concept_id)}</span>
          <span>{e.estimate === null ? "Not assessed" : `${e.successes}/${e.eligible_count} · ${label(e.performance_state)}`}</span></li>)}
      </ul></details>
    </section>
    <section className="learn-panel" aria-labelledby="diagnosis-title">
      <div className="panel-kicker">02 / THE CONNECTION</div>
      <h2 id="diagnosis-title">{bundle.diagnosis.status === "supported_gap" ? "A supported hypothesis" : label(bundle.diagnosis.status)}</h2>
      {bundle.diagnosis.candidates.map((c) => <article className="gap-card" key={c.concept_id}>
        <strong>{label(c.concept_id)}</strong><span className="learn-muted">{label(c.relation)} gap</span>
        <p>{c.path.map(label).join(" → ")}</p>
        <details><summary>Inspect diagnosis evidence</summary><p>Ranking score: {c.score.toFixed(4)} · {label(c.reason)}. A ranking score is not a probability of cause.</p><ul>{c.evidence_event_ids.map((id) => <li className="event-id" key={id}><a href={`#event-${id}`}>{id}</a></li>)}</ul></details>
        <p className="learn-muted">Based on {c.evidence_event_ids.length} eligible responses. The prerequisite path is an instructional hypothesis, not a proven cause.</p>
      </article>)}
      {bundle.diagnosis.evidence_requests.map((r) => <p key={r.concept_id} className="evidence-request">
        <strong>{label(r.concept_id)}</strong>: {r.needed_observations} more eligible observations needed ({label(r.reason)}).
      </p>)}
      {bundle.diagnosis.status === "ambiguous" && <p>Mixed or recently contradictory responses do not support a consistent gap. Further practice may help gather evidence.</p>}
      {bundle.diagnosis.status === "no_supported_gap" && <p>The current evidence does not support a gap on this path.</p>}
      {bundle.diagnosis.status === "no_failed_trigger" && <p>No failed focus response was found. We do not invent a failure diagnosis.</p>}
      {bundle.diagnosis.alternatives.length > 0 && <p className="learn-muted">Other possibilities: {bundle.diagnosis.alternatives.map(label).join(", ")}. These are possibilities, not observed misconceptions.</p>}
      <details><summary>Prerequisites in this release</summary><ul className="concept-evidence">
        {seed.edges.map((e) => <li key={`${e.prerequisite}:${e.dependent}`}>{label(e.prerequisite)} → {label(e.dependent)}</li>)}
      </ul></details>
    </section>
  </>;
}
