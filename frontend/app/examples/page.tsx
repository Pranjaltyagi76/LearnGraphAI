import Link from "next/link";
import data from "@/lib/generated/examples-full-v1.json";

export const metadata = { title: "Recorded synthetic examples · LearnGraph AI" };

export default function Examples() {
  return <main className="learn-shell document-shell"><Link className="brand" href="/">LearnGraph <span className="brand-ai">AI</span></Link>
    <nav className="learn-nav" aria-label="Learning navigation"><Link href="/learn">Live demo</Link><Link href="/methodology">Methodology & limits</Link></nav>
    <p className="eyebrow">ALWAYS AVAILABLE / READ ONLY</p><h1>Four starting points.</h1>
    <p className="document-lede">Prerecorded synthetic examples, evaluated offline with a fixed reference clock on 21 November 2026. Each is pinned to its release, catalog, model, and seed. Opening an example makes no live analysis request and accepts no submissions.</p>
    <div className="example-grid">{data.examples.map(({ seed, analysis }) => <article className="learn-panel" key={seed.profile.id}>
      <span className="state-pill">Prerecorded · synthetic · read only</span><h2>{seed.profile.name}</h2><p>{seed.profile.summary}</p><p className="learn-muted">{analysis.diagnosis.status.replaceAll("_", " ")} · {seed.seed_events.length} seed responses</p>
      <Link className="example-link" href={`/examples/${seed.profile.id}`}>Inspect {seed.profile.name}&apos;s example →</Link>
    </article>)}</div><footer className="learn-footer"><p>These examples demonstrate behavior, not independent benchmark cases or learning gains.</p></footer>
  </main>;
}
