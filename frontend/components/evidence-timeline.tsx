"use client";

import { useState } from "react";
import type { AnalysisBundle, Event, SeedResponse } from "@/lib/protocol";
import { label } from "./learning-evidence";

export function EvidenceTimeline({ bundle, seed, events }: { bundle: AnalysisBundle; seed: SeedResponse; events: Event[] }) {
  const [filter, setFilter] = useState("all");
  const inputs = new Map([...seed.seed_events, ...events].map((e) => [e.event_id, e]));
  const visible = bundle.graded_events.filter((g) => filter === "all" || g.provenance === filter);
  return <section className="learn-panel" aria-labelledby="timeline-title"><h2 id="timeline-title">Response timeline</h2>
    <label className="timeline-filter">Show evidence <select aria-label="Timeline evidence" value={filter} onChange={(e) => setFilter(e.target.value)}>
      <option value="all">Seed and local responses</option><option value="canonical_seed">Canonical seed only</option><option value="visitor_demo">Your local responses</option>
    </select></label>
    <p className="learn-muted">{visible.length} recorded events. Only server-marked eligible responses contribute to estimates.</p>
    <ol className="timeline">{visible.map((g) => {
      const input = inputs.get(g.event_id);
      const item = seed.activities.find((a) => a.id === g.activity_id);
      const option = input?.kind === "response" && item?.kind === "question" ? item.options.find((o) => o.id === input.response.option_id) : null;
      return <li key={g.event_id} id={`event-${g.event_id}`}>
        <strong>{label(g.concept_id)} · {g.is_correct === null ? "lesson read" : g.is_correct ? "correct" : "incorrect"}</strong>
        <span>{g.provenance === "canonical_seed" ? "Synthetic seed" : "Local response"} · {label(g.catalog_role)} · attempt {g.attempt_number}</span>
        <span>{g.eligible ? "Counts as evidence" : "Excluded from estimate"} · {label(g.eligibility_reason)}</span>
        <details><summary>Inspect this event</summary>
          <p>{item?.kind === "question" ? item.prompt : item?.title}</p>
          {option && <p>Selected: {option.id.toUpperCase()} · {option.text}</p>}
          {input?.kind === "response" && <p>Hints: {input.hints_used === null ? "unknown" : input.hints_used}.</p>}
          <p>{g.explanation}</p><time dateTime={g.occurred_at}>{g.occurred_at}</time>
          <p className="event-id">Event ID: {g.event_id}</p><p className="event-id">Activity: {g.activity_id} v{g.activity_version}</p>
        </details>
      </li>;
    })}</ol>
    {!visible.length && <p className="learn-muted">No events in this view. Accepted responses appear after the service grades them.</p>}
  </section>;
}
