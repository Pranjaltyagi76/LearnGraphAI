import Link from "next/link";
import { notFound } from "next/navigation";
import data from "@/lib/generated/examples-full-v1.json";
import { parse } from "@/lib/protocol";
import type { AnalysisBundle, SeedResponse } from "@/lib/protocol";
import { LearningEvidence, label } from "@/components/learning-evidence";
import { CurriculumOverview } from "@/components/curriculum-overview";
import { EvidenceTimeline } from "@/components/evidence-timeline";

export const dynamicParams = false;
export function generateStaticParams() { return data.examples.map((e) => ({ profile: e.seed.profile.id })); }

export default async function Example({ params }: { params: Promise<{ profile: string }> }) {
  const { profile } = await params;
  const example = data.examples.find((e) => e.seed.profile.id === profile);
  if (!example) notFound();
  const seed = parse<SeedResponse>("SeedResponse", example.seed);
  const bundle = parse<AnalysisBundle>("AnalysisBundle", example.analysis);
  return <main className="learn-shell">
    <header className="learn-header"><Link className="brand" href="/">LearnGraph <span className="brand-ai">AI</span></Link><Link href="/examples">All recorded examples</Link></header>
    <nav className="learn-nav" aria-label="Learning navigation"><Link href="/learn">Live demo</Link><Link href="/methodology">Methodology & limits</Link></nav>
    <div className="learn-intro"><p className="eyebrow">PRERECORDED / SYNTHETIC / READ ONLY</p><h1>{seed.profile.name}&apos;s starting point.</h1><p>{seed.profile.summary}</p></div>
    <div className="learn-notice"><strong>No live submission in this example.</strong><p>Offline snapshot, reference clock {data.recorded_at}. Values reflect the canonical synthetic seed only. Open the live demo to create separate browser-local progress.</p></div>
    <details className="release-details"><summary>Recorded versions & hash</summary><p className="event-id">{seed.versions.release_id} · {seed.versions.catalog_version} · {seed.versions.graph_version} · {seed.versions.model_version} · {seed.versions.seed_id} v{seed.versions.seed_version}</p><p className="event-id">{seed.versions.release_hash}</p></details>
    <CurriculumOverview seed={seed} bundle={bundle} focus={bundle.focus_concept_id} />
    <div className="learning-grid"><div className="learning-main"><LearningEvidence bundle={bundle} seed={seed} /></div><aside className="learning-side">
      <section className="learn-panel"><h2>Recorded plan</h2><p>{label(bundle.plan.status)}</p><ol>{bundle.plan.items.map((i) => <li key={i.activity_id}>{label(i.concept_id)} · {label(i.role)} · {label(i.readiness)} · {label(i.reason)}</li>)}</ol><p className="learn-muted">Displayed for inspection. This page cannot submit responses.</p></section>
      <EvidenceTimeline bundle={bundle} seed={seed} events={[]} /></aside></div>
    <footer className="learn-footer"><Link href={`/learn?profile=${profile}`}>Open a separate live sandbox →</Link><Link href="/methodology">Read the limitations</Link></footer>
  </main>;
}
