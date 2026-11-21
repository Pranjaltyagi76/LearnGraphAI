# Full curriculum engineering review — 21 November 2026

The separate [full catalog](catalog-full.v1.json) contains 72 distinct questions and 12 lessons. The [full manifest](../contracts/releases/full-v1.json) pins it, the unchanged graph/policy/protocol, and [four synthetic seeds](profiles-full.v1.json). The original [reviewed slice](review.md), its 14 activities and their versions remain unchanged. Full-v1 is new content, not a silent edit to saved histories.

Each concept has one diagnostic, four practice questions, one reassessment, and a lesson. Three initial distinct observations leave two fresh practice questions and a distinct reassessment. [Actual review output](../context/evidence/phase4_content.json) records coverage and all 13 newly authored executable output traces checked in isolated offline Python subprocesses. Bug-identification snippets and partial examples are intentionally not executed. The application only grades selected options; it never executes visitor code.

| Concept | Question coverage reviewed |
| --- | --- |
| Function calls | Original reviewed six questions preserved, including arguments, return values and nested calls. |
| Call stack | Latest active frame, separate locals, maximum active depth, unwind order, return point and removal of a returned frame. |
| Base cases | Original reviewed six questions preserved, including boundary selection and its returned value. |
| Recursive progress | Decreasing count, repairing direction, skipped odd boundary, shrinking interval, integer halving and a non-progressing branch. |
| Recursive tracing | Additive unwind, before/after ordering, doubling, suffix product, branching and a deliberately unfamiliar boundary. |
| Recurrence relations | Prefix sum, binary-string count, small recurrence evaluation, disjoint stair alternatives, optimization choice and work versus result recurrence. |
| Overlapping subproblems | Repeated states in a call tree, a non-overlapping chain, complete coordinate keys, invocation counts, stable reuse and duplicate state pairs. |
| State definition | Prefix length versus index, concrete prefix sum, capacity pair, empty state meaning, missing coordinate and fixed-string suffix. |
| State transitions | Prefix indexing, actual totals, minimum-cost predecessor, stair counts, impossible alternatives and sum versus product repair. |
| DP base cases | Empty sum, empty path, unreachable amount, empty product, grid origin and empty-string boundary repair. |
| Memoization | Complete key, zero-valued membership, actual cache misses, storing completed values, fixed-input cache scope and falsey-zero repair. |
| Tabulation | Ascending dependencies, actual filled table, descending suffix dependencies, 0/1 in-place direction, premature reads and dependency availability. |

Review checked the stated domains, single keyed option, distinct distractor text, explanation consistency, original provenance and fresh-item roles. The 60 additions are original conceptual, code-tracing and bug-identification items, not renamed copies of the original twelve. Recurring themes across state definition, recurrence and transition are intentional; each asks a different operation or constraint. Engineering review is **not independent educator validation**, a difficulty calibration, or an assertion that these distractors diagnose a particular misconception.

Full profiles deliberately separate product demonstrations from quality-audit labels:

| Profile | Canonical events | Focus and intended observed behavior |
| --- | ---: | --- |
| Mira | 6 | Base-case target weakness with ready function calls. |
| Arjun | 27 | Memoization focus with supported upstream overlapping-subproblems weakness; assessed dependencies distinguish it from missing evidence. |
| Leena | 1 | Early state-definition evidence, unknown remaining concepts, and no failed trigger. |
| Kabir | 15 | Mixed tabulation evidence with ready DP prerequisites; ambiguous rather than a supported gap. |

`python -m scripts.check_full_curriculum` verifies these actual outputs and reproduces the bundled read-only examples. `tests/test_full_curriculum.py` additionally runs the full two-practice/distinct-reassessment loop for each of the twelve concepts with explicitly ready dependency fixtures, then checks the honest 0.5/developing exhausted result. These fixtures establish workflow feasibility, not realistic learning or independent prediction quality.

The exposed [quality audit](../evaluation/model_card.md) still covers only the original two-concept slice. Full-v1 publishes no incompatible quality summary. Independent full-track scenarios, curriculum feedback and release/recovery stress gates remain future validation work.
