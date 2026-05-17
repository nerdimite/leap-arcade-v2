---
name: implementor
description: Orchestrate implementation from a PRD and parent issue folder by running issue batches in dependency order with fast subagents. Use when the user wants to execute a parent issue, run all sub-issues, or kick off implementation from a PRD/issues plan.
disable-model-invocation: true
---

# Implementor

## Inputs

Expect the user to provide:

- `PRD:` path to the main product requirements document
- `Issues:` path to the parent issue folder or parent issue file

## Workflow

1. Read the PRD and parent issue.
2. Parse the parent issue's execution plan into batches.
3. Run batches sequentially.
4. Within each batch, spawn one subagent per sub-issue in parallel.
5. Prefer `composer-2-fast` for every subagent.
6. If a `composer-2-fast` subagent reports it cannot complete the issue, retry that specific sub-issue once with the inherited/default model.
7. Respect blockers from each issue file even if the parent batch plan already accounts for them.
8. After each subagent completes, verify the sub-issue was implemented and its status was marked `done`.
9. When all issues in a batch are done, update the parent issue to mark that batch/sub-issues done.
10. Continue to the next batch only after the current batch is complete.
11. After all batches complete, verify the parent issue's overall acceptance criteria. Use subagents for verification to avoid bloating the main context.
12. Report any failed acceptance criteria, unfinished issue, blocker, or test failure before claiming completion.

## Subagent Prompt Template

Every implementation subagent prompt must:

- Reference the PRD path as primary context.
- Reference the full sub-issue markdown path as the unit of work.
- Invoke the `/tdd` skill to drive red → green → refactor implementation.
- Carry forward concrete technical steering for this specific sub-issue so the subagent does not re-derive decisions from scratch. Pull this steering from the PRD and parent issue: relevant glossary terms, ADR pointers, affected layers (route → service → DAO → model), specific module/file or directory hints, data shapes that already exist in the PRD, and any non-obvious constraints (e.g. server-authoritative timer, idempotent seeds, deep-module boundaries).
- Tell the subagent to update the sub-issue's status to `done` only after tests are green and acceptance criteria are met, and to surface blockers instead of inventing new scope.

Use this shape, filling each section per sub-issue. Do not paste it verbatim — tailor the steering bullets to that issue's surface area.

```text
Context:
- PRD: <path-to-prd>
- Sub-issue: <path-to-sub-issue-markdown>
- Parent issue: <path-to-parent-issue-markdown>
- Relevant ADRs: <paths or "none">
- Glossary: <CONTEXT.md or equivalent path>

Goal:
Implement only what the sub-issue requires, using TDD. Treat the sub-issue's acceptance criteria as the test contract.

Technical steering:
- Layering: <which of route → service → DAO → model → types this slice touches>
- Deep modules to use or extend: <e.g. WikiScoring, WikiHtmlRewriter, WikipediaClient>
- Data shapes: reuse the DTO/schema/SQL shapes already defined in the PRD; do not redesign them
- Seeds/migrations: <idempotent? new table? alter existing?>
- Tests: <unit vs service-with-fakes vs API e2e with respx fixtures; which is primary for this slice>
- Constraints: <e.g. server-authoritative timer per ADR-0004, redirect = 1 step, no live Wikipedia calls>
- Out of scope for this slice: <call out neighbouring slices that must not be implemented here>

Process:
/tdd implement <path-to-sub-issue-markdown>

When done:
- Run the relevant test suites and confirm green.
- Update the sub-issue's Status to `done`.
- If you cannot complete the slice, stop and report the blocker rather than expanding scope.
```

If retrying with the inherited/default model after a fast-agent failure, prepend a short failure summary above the steering block:

```text
Previous fast-agent attempt could not complete:
<brief failure summary, including last failing test or blocker>
```
