# LearnGraph AI

**Find the concept behind the mistake.**

LearnGraph AI is a planned explainable learning-diagnostics portfolio application. It combines a prerequisite graph, transparent estimates of observed performance, and targeted practice to help explain where a learner may need support.

**Status:** Planning and development-context documentation are present. No application code, authored question catalog, measured benchmark, database, or public deployment exists yet. Creating this documentation does not complete the Phase 0 design gate.

**Service budget:** ₹0 / $0. The project uses verified free plans and may temporarily stop live analysis when quotas or dependencies are unavailable. It does not require a paid AI API or a purchased domain.

## Planned learning loop

1. Explore an anonymous synthetic learner profile.
2. Answer a diagnostic question or inspect its existing history.
3. See estimated performance, evidence counts, and prerequisite relationships.
4. Review a supported suspected gap or an explicit request for more evidence.
5. Complete targeted practice and a different same-skill reassessment.
6. See the updated result without affecting another visitor's progress.

These are planned capabilities, not an announcement of a working demo. A baseline correctness estimate is not proof of mastery, causality, or improved learning.

## First-release scope

| Area | P0 plan |
| --- | --- |
| Curriculum | 12 recursion/introductory-DP concepts; 48 distinct questions plus lessons. |
| Demo data | Four contrasting synthetic profiles; no real student records. |
| State | Immutable server-owned seeds; isolated browser-local visitor history. |
| Analysis | Backend grading, deterministic replay, smoothed performance estimates, bounded prerequisite diagnosis, and valid recommendations. |
| Frontend/API | Next.js/TypeScript/Tailwind; lightweight Python/FastAPI. |
| Hosting | Two Vercel Hobby projects and Supabase Free; verify feasibility early. |
| Evaluation | Reproducible baseline comparisons, independent scenarios, and prefix-based prediction. |
| Deferred | Accounts, real mentor access, CSV import, BKT/DKT, EdNet experiments, and optional Gemini wording. |

## Development documentation

| File | Purpose |
| --- | --- |
| [requirement.md](requirement.md) | Testable functional/nonfunctional requirements and scope boundaries. |
| [PROJECT.md](PROJECT.md) | Full product specification, curriculum proposal, algorithm defaults, and release criteria. |
| [AGENTS.md](AGENTS.md) | Instructions for future development sessions, context loading, Git identity, and delivery. |
| [context/system design.md](context/system%20design.md) | User flows, data movement, service contracts, state, and failure behavior. |
| [context/architecture.md](context/architecture.md) | Module boundaries, dependency rules, deployment topology, and decision records. |
| [context/phasewise_roadmap.md](context/phasewise_roadmap.md) | Ordered implementation tasks, gates, current progress, and handoff. |
| [context/deployment.md](context/deployment.md) | Free-plan verification, environment ownership, release, rollback, and recovery. |
| [context/performance_review.md](context/performance_review.md) | Proposed performance budgets and actual-review recording protocol. |
| [context/benchmark.md](context/benchmark.md) | Evaluation datasets, leakage prevention, baselines, metrics, and reporting. |

Start a development session with this file, the requirements, and the roadmap. Consult the relevant context document before changing that area. Document decisions in their owning files and reconcile changes with the full specification.

## Running the project

There are no application setup commands yet: `frontend/`, `backend/`, dependency manifests, and migrations are planned. Do not run imagined `npm`, API, or deployment commands from this README. Phase 1 will add verified local commands, pinned tool versions, a placeholder-only `.env.example`, and working setup instructions.

The next work is Phase 0: resolve the documented question-budget/evidence-gate conflict (OPEN-01), review the graph and evidence rules, define precise contracts, author a small question slice, and establish evaluation splits. The current four-items-per-concept budget leaves too few fresh items for both practice and reassessment after a supported diagnosis. Then prove the free frontend → API → database path before implementing the full product.

## Repository and contribution workflow

Repository: [Pranjaltyagi76/LearnGraphAI](https://github.com/Pranjaltyagi76/LearnGraphAI).

Work is delivered in coherent, reviewable commits under the repository owner's configured identity. Future sessions follow [AGENTS.md](AGENTS.md) and record implemented behavior and actual validation rather than marking planned features complete.

No live-demo link or benchmark score is published yet. No software license has been selected; public source availability alone does not grant a particular open-source license. Third-party datasets/resources retain their own terms.
