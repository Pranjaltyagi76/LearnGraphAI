"use client";

import { useState } from "react";
import type { AnalysisBundle, SeedResponse } from "@/lib/protocol";
import { label } from "./learning-evidence";

const positions: Record<string, [number, number]> = {
  function_calls: [100, 70], call_stack: [330, 70], base_cases: [330, 190],
  recursive_progress: [560, 190], recursive_tracing: [790, 70],
  overlapping_subproblems: [1020, 70], state_definition: [100, 430],
  recurrence_relations: [330, 430], state_transitions: [560, 360],
  dp_base_cases: [560, 530], memoization: [1020, 290], tabulation: [790, 530],
};

export function CurriculumOverview({ seed, bundle, focus, onFocus, disabled = false }: {
  seed: SeedResponse; bundle: AnalysisBundle | null; focus: string;
  onFocus?: (id: string) => void; disabled?: boolean;
}) {
  const [view, setView] = useState<"graph" | "list">("graph");
  const estimates = new Map(bundle?.estimates.map((e) => [e.concept_id, e]));
  return <section className="learn-panel curriculum-panel" aria-labelledby="curriculum-title">
    <div className="curriculum-heading"><div><div className="panel-kicker">YOUR LEARNING LANDSCAPE</div>
      <h2 id="curriculum-title">Twelve concepts. Connected.</h2></div>
      <div className="view-switch" role="group" aria-label="Curriculum view">
        <button aria-pressed={view === "graph"} onClick={() => setView("graph")}>Graph view</button>
        <button aria-pressed={view === "list"} onClick={() => setView("list")}>List view</button>
      </div></div>
    <p className="learn-muted">Arrows run from a prerequisite to its dependent concept. Each state is named in text.
      Unassessed concepts remain unknown; they do not inherit a weakness label from a neighbor.</p>
    {view === "graph" && <figure className="concept-map">
      <div className="graph-scroll" role="region" aria-label="Prerequisite graph; scroll horizontally, or use the concept list below" tabIndex={0}>
        <svg viewBox="0 0 1120 610" aria-hidden="true" focusable="false">
          <defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#738578" /></marker></defs>
          {seed.edges.map((e) => {
            const [x1, y1] = positions[e.prerequisite]; const [x2, y2] = positions[e.dependent];
            const down = x1 === x2;
            return <path key={`${e.prerequisite}:${e.dependent}`} className="graph-edge" markerEnd="url(#arrow)"
              d={down ? `M ${x1} ${y1 + 37} L ${x2} ${y2 - 37}` :
                `M ${x1 + 90} ${y1} C ${x1 + 125} ${y1}, ${x2 - 125} ${y2}, ${x2 - 90} ${y2}`} />;
          })}
          {seed.concepts.map((c) => {
            const [x, y] = positions[c.id]; const estimate = estimates.get(c.id);
            const words = label(c.id).split(" ");
            return <g key={c.id} transform={`translate(${x},${y})`}>
              <rect x="-90" y="-37" width="180" height="74" rx="10" className={focus === c.id ? "graph-node focused" : "graph-node"} />
              <text textAnchor="middle" y="-12" className="graph-title">{words.length > 1 ? words.slice(0, -1).join(" ") : words[0]}</text>
              {words.length > 1 && <text textAnchor="middle" y="4" className="graph-title">{words.at(-1)}</text>}
              <text textAnchor="middle" y="25" className="graph-state">{label(estimate?.performance_state ?? "unknown")}{focus === c.id ? " · focus" : ""}</text>
            </g>;
          })}
        </svg>
      </div><figcaption>Instructional prerequisites for this track, not proven causes of a mistake. The same connections and evidence are listed below.</figcaption>
    </figure>}
    <ul className="concept-cards" aria-label="Concept evidence and prerequisites">
      {seed.concepts.map((c) => {
        const e = estimates.get(c.id);
        const parents = seed.edges.filter((edge) => edge.dependent === c.id).map((edge) => edge.prerequisite);
        return <li key={c.id} className={focus === c.id ? "concept-card is-focus" : "concept-card"}>
          <div className="concept-card-title"><strong>{label(c.id)}</strong><span className="state-pill">{label(e?.performance_state ?? "unknown")}</span></div>
          <p>{c.definition}</p>
          <p className="learn-muted">{e?.estimate == null ? "Not assessed · no correctness estimate" :
            `${e.successes}/${e.eligible_count} eligible correct · ${label(e.evidence_state)} · ${(e.estimate * 100).toFixed(1)}% observed correctness`}</p>
          <p className="learn-muted">Prerequisites: {parents.length ? parents.map(label).join(", ") : "none in this track"}.</p>
          {onFocus && <button aria-label={`Focus on ${label(c.id)}`} aria-pressed={focus === c.id} disabled={disabled}
            onClick={() => onFocus(c.id)}>{focus === c.id ? "Current focus" : "Explore this concept"}</button>}
        </li>;
      })}
    </ul>
  </section>;
}
