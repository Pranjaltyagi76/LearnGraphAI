# Development instructions

## Read before working

1. Read `readme.md` for actual repository status and document navigation.
2. Read `requirement.md` for release requirements and stable requirement IDs.
3. Read `context/phasewise_roadmap.md` for the current phase and its exit gate.
4. Read the relevant context file: `system design.md`, `architecture.md`, `deployment.md`, `performance_review.md`, or `benchmark.md`.
5. Consult `PROJECT.md` for the full approved product rationale and algorithm defaults.

User instructions take precedence. Keep the requirements, detailed specification, and context documents consistent when a decision changes. Resolve routine implementation details within the approved scope; document material design changes and their reasons. Do not treat an unchecked roadmap item as already implemented.

## Non-negotiable project constraints

- Recurring service budget: ₹0 / $0. No paid plan, API, GPU, domain, automatic top-up, or reliance on expiring credits. No payment setup without a new explicit user instruction changing this constraint.
- P0: 12 concepts, 48 distinct questions plus lessons, four synthetic profiles, anonymous browser-local sandboxes, deterministic FastAPI analysis, and a real practice/reassessment loop.
- Default hosting: two Vercel Hobby projects and Supabase Free, verified early. Render Free is only an alternative; no paid fallback.
- No real student data, public signup, arbitrary code execution, LLM dependency, hosted training, or required BKT/DKT in P0.
- Never invent benchmark numbers, screenshots of nonexistent behavior, deployment URLs, completed tasks, or learning gains.
- Store secrets only in appropriate local/provider secret configuration; never commit them. Grading rules in this public educational source are not a confidential examination bank.

## Development workflow

- Complete one reviewable vertical slice at a time, starting with the current phase. Run checks appropriate to the change and record actual evidence.
- Keep production API dependencies separate from research packages/data. Preserve deterministic replay and versioned input/output contracts.
- Update current status and handoff notes in `context/phasewise_roadmap.md` when meaningful progress changes them. Update performance/benchmark reports only after actual measurements.
- Link documents with repository-relative Markdown links. Keep `PROJECT.md` as the detailed specification; do not create competing copies of formulas or thresholds without checking consistency.
- Prefer existing tools and direct Git operations for this repository. Do not create extra services or install integrations just for documentation work.

## Git identity and delivery preferences

- Repository: `https://github.com/Pranjaltyagi76/LearnGraphAI.git`; normal branch: `main` until a later agreed branching workflow changes it.
- Use author and committer `Pranjal Tyagi <207156329+Pranjaltyagi76@users.noreply.github.com>`. This repository-local GitHub-linked noreply identity uses the owner's verified public account ID for contribution attribution while keeping the personal email out of new public commits. Verify effective identities before committing; do not replace them with assistant identities.
- Add no assistant co-author trailers or assistant signatures. Do not rewrite someone else's existing authorship/history to change contributors.
- The user prefers 4–6 meaningful commits per work batch. Group by coherent outcome, with clear imperative subjects and useful bodies; do not manufacture empty or arbitrary splits to hit a count.
- Push when the user authorizes delivery. An explicit “do not push” instruction overrides the standing workflow for that task. The documentation/context setup is authorized for a push.
- Inspect the remote before pushing, stage explicit paths, review staged content, and verify the remote commit afterward. Never force-push or overwrite unrelated remote work.
