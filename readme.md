# LearnGraph AI

**Find the concept behind the mistake.**

LearnGraph AI is a planned explainable learning-diagnostics portfolio application. It combines a prerequisite graph, transparent estimates of observed performance, and targeted practice to help explain where a learner may need support.

**Status:** Phase 1 is complete: the public Next.js preview delivers a question through FastAPI and Supabase Free, grades an answer on the server, and displays real feedback. TLS, restricted database access, immutable content, shared quotas, deployment resources, and reseeding were verified. Phase 2 now implements the deterministic offline diagnosis/replay engine and measured evaluation. The full 72-question curriculum, saved progress, live analysis routes, and reassessment UI remain later work.

**Phase 0 review is also complete:** [reviewed curriculum](curriculum/review.md), [frozen protocol/schema](contracts/protocol.md), [browser storage contract](context/browser_storage.md), and [synthetic evaluation definitions](evaluation/readme.md) define the implementation inputs. Phase 2 implements analysis/evaluation; browser storage remains Phase 3 work. The new graph, twelve reviewed questions/two lessons, and four profiles are unpublished draft assets; the live preview still serves the immutable Phase 1 slice.

[Live infrastructure preview](https://learngraph-ai-web.vercel.app) · [API readiness](https://learngraph-ai-api.vercel.app/ready) · [Passing source CI run](https://github.com/Pranjaltyagi76/LearnGraphAI/actions/runs/44730530223)

Click **Check live connection**, choose an answer, and select **Check my response**. The page starts with a labeled prerecorded example and switches to a live question only after database readiness succeeds. Grading does not save learner progress. Supabase Free can pause after inactivity; the unavailable/example state remains available when the live dependency is down.

**Service budget:** ₹0 / $0. The project uses verified free plans and may temporarily stop live analysis when quotas or dependencies are unavailable. It does not require a paid AI API or a purchased domain.

## Planned learning loop

1. Explore an anonymous synthetic learner profile.
2. Answer a diagnostic question or inspect its existing history.
3. See estimated performance, evidence counts, and prerequisite relationships.
4. Review a supported suspected gap or an explicit request for more evidence.
5. Complete targeted practice and a different same-skill reassessment.
6. See the updated result without affecting another visitor's progress.

This full learning loop is planned; Phase 1 implements only live question delivery and grading. A baseline correctness estimate is not proof of mastery, causality, or improved learning.

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
| [contracts/protocol.md](contracts/protocol.md) | Frozen API/events, hashes, errors, readiness/exhaustion policy, and rollout compatibility. |
| [curriculum/review.md](curriculum/review.md) | Concept/edge/item review, profile definitions, and fresh-item feasibility limits. |
| [context/browser_storage.md](context/browser_storage.md) | IndexedDB transactions, pending snapshots, refresh/reset, cross-tab conflicts, and session-only fallback. |
| [evaluation/readme.md](evaluation/readme.md) | Frozen 4/8/12 synthetic splits, annotation provenance, public-audit limits, and evaluator rules. |

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

`/health` is process liveness; `/ready` returns `503` until the database, release, quota privileges, and hash secret are available. Phase 1 grading is `POST /api/v1/bootstrap/answer`; full-history HTTP analysis is Phase 3 work; the pure engine and offline CLI are implemented.

Browser checks, after building the frontend:

```powershell
npx playwright install chromium
npm run test:e2e
```

Contract tests use an explicitly labeled fixture; real SQL tests require an isolated local `TEST_DATABASE_URL` ending in `_test` and otherwise skip. CI supplies real PostgreSQL 17. Neither a contract fixture nor a recorded browser example passes the live Supabase deployment gate.

OPEN-01 and Phase 0 contract/content review are complete. The free frontend → API → database gate passed. Phase 2 CLI analysis and measured offline evaluation now pass. Next is Phase 3: publish a compatible analysis release, integrate the HTTP routes and browser sandbox, and verify the live learning loop. See the roadmap and [measured infrastructure evidence](context/performance_review.md) for exact scope and limitations.

## Repository and contribution workflow

Repository: [Pranjaltyagi76/LearnGraphAI](https://github.com/Pranjaltyagi76/LearnGraphAI).

Work is delivered in coherent, reviewable commits under the repository owner's configured identity. Future sessions follow [AGENTS.md](AGENTS.md) and record implemented behavior and actual validation rather than marking planned features complete.

Deployment URLs and measured infrastructure checks are recorded in the deployment context when verified. The [measured public synthetic audit and model card](evaluation/model_card.md) report actual results and their small-sample/exposure limits. No software license has been selected; public source availability alone does not grant a particular open-source license. Third-party datasets/resources retain their own terms.

## Offline Phase 2 analysis and evaluation

From `backend/`, after the locked development environment is installed:

```powershell
uv run --frozen python -m scripts.analyze --profile demo_base_cases --explain
uv run --frozen python -m scripts.evaluate --check ../evaluation/results/phase2-v2
```

Use `--request path.json --received-at 2026-11-21T00:00:00+00:00` for a complete frozen AnalyzeRequest. The received-at argument is explicit admission time, never a scoring feature. To record a new measurement, use `python -m scripts.evaluate --output ../evaluation/results/a-new-run-id`; existing runs are never overwritten. The saved audit reproduces exact outputs and verifies implementation/input hashes. See the [report](evaluation/results/phase2-v2/report.md), [model card](evaluation/model_card.md) and [handoff](context/phasewise_roadmap.md).

This milestone uses no provider request, new package, or paid service. The live preview continues to serve Phase 1 until Phase 3 activation.
