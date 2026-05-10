# Meridian — Glossary

Shared vocabulary across [deep-design](../deep-design/SKILL.md), [issue-planner](../issue-planner/SKILL.md), and [builder](../builder/SKILL.md). Use these terms consistently in the skills, the Design Doc, the issue tree, and the implementation notes.

## Phases

- **Deep Design (the jam)** — Phase 1. Top-down call-graph traversal that produces stubs + failing tests + Design Doc. The jam is the conversation; the artifact is the codebase + Design Doc that result.
- **Issue Planner** — Phase 2. Translates the Design Doc + stubs into a parent issue + sub-issues + batch execution plan.
- **Builder** — Phase 3. Orchestrator drives execution by spawning executor subagents per sub-issue, batch by batch, writing implementation notes for human review.

## Roles

- **Human** — the user. Brain of the workflow. Deeply involved during the jam, hands-off during execution, deliberate at per-batch review.
- **Orchestrator** — the full-model agent running the `builder` skill. Reads the parent issue and Design Doc, dispatches executors, judges escalations, writes implementation notes. Never commits.
- **Executor (subagent)** — a fast-model subagent (e.g. `composer-2-fast`) spawned via Cursor's `Task` tool. Implements one sub-issue at a time. Narrow context, narrow task.

## Artifacts

- **Stub** — a function with `raise NotImplementedError` as its body and a one- or two-line docstring. Written during the jam.
- **Acceptance test** — a failing pytest test written during the jam that defines the contract for one behaviour. The executor turns these from red to green.
- **Base acceptance tests** — the always-required tests covering the happy path and the most important failure modes. Written for every public function during the jam.
- **TODO edge-case comment** — a `# TODO (executor): ...` block above a test class listing edge cases the executor must add tests for during execution. Part of the spec, not optional.
- **Design Doc** — the inline-written running-notes markdown at `docs/design/<feature>.md`. The human-readable map. Sections: Intent, Entry Points, Traversal Strategy, File Map, Non-Functional Constraints, Key Design Decisions, Open Edge Cases, Appendix.
- **Parent issue** — top-level issue (Linear or markdown) capturing Intent, Overall Acceptance Criteria, Execution Plan, References. Anchored to the user's verbatim intent statement from the jam opening.
- **Sub-issue** — a coherent batch of tasks roughly the size of one reviewable PR. Has Tasks, Acceptance Criteria, Code References, Technical Guidelines, Non-Functional Constraints, depends-on/blocks. Each maps to one executor invocation in `builder`.
- **Batch** — a group of sub-issues that can run in parallel (no shared state, no sequential dependency). The execution plan on the parent issue is a list of batches in order.
- **Implementation notes** — markdown the orchestrator writes after each batch (and a final consolidated one at the end). Sections: What Was Done, Reading Order, Decisions Made, Flags, Test Status, Files Changed, optional Amendments. The reading order is curated for tractable human review.

## Modes & Concepts

- **Greenfield** — entry mode for the jam where there is no existing code in this area. Lighter orientation pass.
- **Extension** — entry mode for the jam where existing code is being extended or refactored. Requires a codebase orientation pass before designing.
- **Wide-first traversal** — map all branches at the same depth before going deep on any. Use for multi-entry-point features, refactors, or anything with cross-cutting concerns.
- **Deep-first traversal** — go all the way down one branch before starting the next. Use for single end-to-end flows or exploratory features.
- **Default mode (builder)** — orchestrator stops after each batch for human review.
- **Auto mode (builder)** — orchestrator runs through all batches without stopping; consolidated note at the end.
- **Two-attempt rule** — an executor gets one self-correction attempt on failing tests. After that, it must escalate, not keep trying.
- **Severity-proportional pushback** — three tiers (light touch / moderate / hard stop) based on reversibility, blast radius, and depth in the call graph.
- **Amendment loop** — defined path back into `deep-design` (and forward through `issue-planner`) when execution reveals the design itself is wrong. Two flavors: patch in place (small) or re-jam (large).
- **Non-Functional Constraints (NFRs)** — performance, concurrency, latency, retry semantics, observability requirements that don't fit cleanly into stubs+tests. Captured in the Design Doc per file/flow and carried forward as Technical Guidelines on sub-issues.

## Naming Conventions

- Design Doc path: `docs/design/<feature>.md`
- Markdown issues path: `docs/issues/<feature>/parent.md`, `docs/issues/<feature>/sub-<n>-<short-name>.md`
- Sub-issue numbering: `Sub-Issue 1`, `Sub-Issue 2`, ... in order of intended execution within the batch plan.
- Batch numbering: `Batch 1`, `Batch 2`, ... strictly sequential.
- Test classes: `Test<FunctionName>` or `Test<ClassName>`, with method names `test_<observable_behavior>` (snake_case, behavioural, never `test_works`).
- Fakes: `Fake<RealName>` (e.g. `FakeSlotRepository`). Mocks: only when the call itself is the contract — see [testing-guidelines.md](testing-guidelines.md).
