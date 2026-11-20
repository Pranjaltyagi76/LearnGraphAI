# LearnGraph AI

**Find the concept behind the mistake.**

LearnGraph AI is a planned explainable learning-diagnostics portfolio application. It combines a prerequisite graph, transparent estimates of observed performance, and targeted practice to help explain where a learner may need support.

**Status:** Phase 1 scaffold is implemented: a Next.js preview, FastAPI question/grading slice, versioned 12-question source, migration/seed scripts, and verification suites. The full 72-question curriculum, diagnosis/replay engine, saved progress, and reassessment UI remain later work. Supabase is not connected/provisioned yet, so the real live database gate is pending; no completion of Phase 1 is claimed.

[Hosted infrastructure preview](https://learngraph-ai-web.vercel.app) · [API liveness](https://learngraph-ai-api.vercel.app/health) · [Passing source CI run](https://github.com/Pranjaltyagi76/LearnGraphAI/actions/runs/44700160117)

The public page currently shows a labeled prerecorded example. Live grading remains unavailable until Supabase is connected, provisioned, migrated/seeded, and configured with its runtime role/secret. `/ready` correctly reports `503 not_configured`. This is not a completed Phase 1 live database gate.

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
| Curriculum | 12 recursion/introductory-DP concepts; 72 distinct questions plus lessons. |
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

The tested toolchain is Node.js 24.18.0, Next.js 16.4.6, React 19.3.1, TypeScript 6.0.3, Python 3.12.10, and uv 0.12.23. Runtime/development dependencies are locked separately for each service. TypeScript 7 was rejected by the current lint parser; the verified compatible TypeScript 6 toolchain is pinned.

Frontend, from `frontend/`:

```powershell
npm ci
Copy-Item .env.example .env.local
npm run lint
npm run typecheck
npm run build
npm run start
```

The default local frontend points to `http://127.0.0.1:8000`. Before API/database setup it deliberately shows a labeled prerecorded example; it does not pretend live grading works.

Backend, from `backend/`:

```powershell
uv sync --frozen --group dev
Copy-Item .env.example .env.local
uv run pytest -q
```

For live API startup, first configure the actual runtime/admin environment privately and follow [database setup](backend/migrations/readme.md). With the linked project, database migration/seed, runtime role, and required environment keys verified:

```powershell
uv run python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --env-file .env.local
```

`/health` is process liveness; `/ready` returns `503` until the database, release, quota privileges, and hash secret are available. Phase 1 grading is `POST /api/v1/bootstrap/answer`; deterministic history/diagnosis APIs are Phase 2 work.

Browser checks, after building the frontend:

```powershell
npx playwright install chromium
npm run test:e2e
```

Contract tests use an explicitly labeled fixture; real SQL tests require an isolated local `TEST_DATABASE_URL` ending in `_test` and otherwise skip. CI supplies real PostgreSQL 17. Neither a contract fixture nor a recorded browser example passes the live Supabase deployment gate.

OPEN-01 is resolved by the 72-question target and a tested two-concept authored slice. The remaining design review and the actual free frontend → API → database gate must pass before full-product implementation. See the roadmap for current implementation evidence and external setup requirements.

## Repository and contribution workflow

Repository: [Pranjaltyagi76/LearnGraphAI](https://github.com/Pranjaltyagi76/LearnGraphAI).

Work is delivered in coherent, reviewable commits under the repository owner's configured identity. Future sessions follow [AGENTS.md](AGENTS.md) and record implemented behavior and actual validation rather than marking planned features complete.

Deployment URLs and measured infrastructure checks are recorded in the deployment context when verified. No model benchmark score exists yet. No software license has been selected; public source availability alone does not grant a particular open-source license. Third-party datasets/resources retain their own terms.
