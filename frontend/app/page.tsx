import { ConnectionPreview } from "@/components/connection-preview";
import Link from "next/link";

const repository = "https://github.com/Pranjaltyagi76/LearnGraphAI";

export default function HomePage() {
  return (
    <div className="site-shell">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="site-header">
        <Link href="/" className="brand" aria-label="LearnGraph AI home">
          <span className="brand-mark" aria-hidden="true">
            L<span>↗</span>
          </span>
          LearnGraph<span className="brand-ai">AI</span>
        </Link>
        <nav aria-label="Main navigation">
          <a href="#how-it-works">The approach</a>
          <Link href="/methodology">
            Methodology <span aria-hidden="true">↗</span>
          </Link>
          <a className="source-link" href={repository}>
            View source <span aria-hidden="true">↗</span>
          </a>
        </nav>
      </header>
      <main id="main">
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero-copy">
            <p className="eyebrow">
              <span className="status-dot" /> A MORE THOUGHTFUL WAY TO PRACTICE
            </p>
            <h1 id="hero-title">
              Find the concept
              <br />
              behind the <em>mistake.</em>
            </h1>
            <p className="hero-description">
              A wrong answer is a starting point. Trace the prerequisites,
              understand the evidence, and find a clearer next step.
            </p>
            <Link className="primary-link" href="/learn">
              Explore the learning loop <span aria-hidden="true">↗</span>
            </Link>
            <p className="hero-note">
              Synthetic learners. Explainable estimates. No account needed.
            </p>
            <div
              className="curriculum-path"
              aria-label="Example learning path: function calls, base cases, memoization"
            >
              <span>Function calls</span>
              <b aria-hidden="true">→</b>
              <span>Base cases</span>
              <b aria-hidden="true">→</b>
              <span className="path-muted">Memoization</span>
            </div>
            <p className="path-caption">
              A small view of the prerequisite journey. Explore the guided demo
              for evidence, practice, and distinct reassessment.
            </p>
          </div>
          <ConnectionPreview />
        </section>
        <section
          id="how-it-works"
          className="approach"
          aria-labelledby="approach-title"
        >
          <div className="section-heading">
            <p className="eyebrow">THE LEARNING LOOP</p>
            <h2 id="approach-title">Less guessing. More understanding.</h2>
            <p>
              Explore the guided learning loop, or use this original connection
              preview to check the question and grading path.
            </p>
          </div>
          <div className="approach-grid">
            <article>
              <span className="step-number">01 / OBSERVE</span>
              <h3>Start with the evidence</h3>
              <p>
                Use distinct responses and show what is known, uncertain, or
                still unassessed.
              </p>
            </article>
            <article>
              <span className="step-number">02 / CONNECT</span>
              <h3>Look one layer deeper</h3>
              <p>
                Follow reviewed prerequisites to surface supported gaps and ask
                for evidence where it is missing.
              </p>
            </article>
            <article>
              <span className="step-number">03 / REASSESS</span>
              <h3>Make the next step count</h3>
              <p>
                Practice with fresh questions, then reassess the same skill
                using a different problem.
              </p>
            </article>
          </div>
        </section>
        <aside className="scope-note">
          <strong>Built to explain, not overclaim.</strong>
          <p>
            This is an independent portfolio prototype. Synthetic examples and
            correctness estimates do not prove mastery, causality, or real
            learning gains.
          </p>
        </aside>
      </main>
      <footer>
        <span>
          LearnGraph AI <span aria-hidden="true">/</span> An independent
          learning experiment
        </span>
        <a href={`${repository}/tree/main/context`}>Development notes ↗</a>
      </footer>
    </div>
  );
}
