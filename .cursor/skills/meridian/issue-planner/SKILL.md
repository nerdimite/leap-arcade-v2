---
name: meridian-issue-planner
description: Translate a meridian/deep-design output (stubs + Design Doc + jam transcript) into a parent issue and dependency-flagged sub-issues with an explicit batch execution plan. Acts as tech lead + scrum master + PM. Asks the user whether to use Linear MCP (if present) or markdown files. Use after a deep-design jam is complete and you are ready to translate the design into executable work units before invoking meridian/builder.
---

# Meridian — Issue Planner

The second phase of [meridian](../README.md). Takes the design output and produces the issue tree that [meridian/builder](../builder/SKILL.md) consumes. Plays a combined tech-lead + scrum-master + PM role: derives coherent task batches, flags dependencies, and writes the parent issue + sub-issues.

## Inputs

- The stub codebase from `deep-design` (stubs + minimal docstrings + failing tests + edge-case TODO comments)
- `docs/design/<feature>.md` — the Design Doc
- The `deep-design` jam transcript (use as additional reasoning context; the Design Doc is the structured source of truth)

## Output Targets — Ask the User

At the start, ask explicitly:

> "Linear MCP detected — want me to create issues there, or use markdown files? Either is fine."

(Even if Linear MCP is connected, never assume. Project conventions or session preferences may differ.)

- **Linear** → create real Linear parent issue + sub-issues with the structure below.
- **Markdown** → write to `docs/issues/<feature>/parent.md` and `docs/issues/<feature>/sub-<n>-<short-name>.md`.

## How to Read the Inputs

The Design Doc is your primary structural source — it was deliberately built as the human-readable map. Read the stubs only when you need detail (exact signatures, exact test names). Use the jam transcript when reasoning is unclear from the Design Doc alone.

## Structure

### Parent Issue

Anchored to the user's verbatim intent statement from the jam opening. You formalize, do not invent.

```markdown
# <Feature Name>

## Intent
<verbatim from jam opening, lightly formalized — no embellishment>

## Overall Acceptance Criteria
- Full <feature> flow works end-to-end
- All base acceptance tests pass across all layers
- <feature-specific top-level criteria>

## Execution Plan
Batch 1 (parallel): Sub-issue 1, Sub-issue 2
Batch 2 (after Batch 1): Sub-issue 3
Batch 3 (after Batch 2): Sub-issue 4

## References
- Design Doc: `docs/design/<feature>.md`
- Entry point(s): <e.g. `POST /appointments/book`>
```

The **batch execution plan lives on the parent issue** — single source of truth for `builder`. Sub-issues carry their own depends-on/blocks for cross-reference, but the orchestrator reads order from the parent.

### Sub-Issues

Each sub-issue is a **coherent batch of tasks** with tangible output — sized so a single Linear sub-issue (or markdown file) represents a meaningful chunk of work an executor can pick up and finish.

**Sizing heuristic:** a sub-issue should be roughly the size of a single reviewable PR — small enough that a human can walk the diff and the implementation notes in one sitting, large enough that it represents real progress (not a single function rename). Concretely: usually one cohesive file or a small tightly-coupled group of files that ship together. Rough rule of thumb: 30 minutes to 2 hours of executor time. If it's smaller, fold it into a sibling sub-issue. If it's bigger, split it.

For small parent issues, it is fine for the entire feature to be a single sub-issue (i.e. parent ≈ sub ≈ one PR). Don't manufacture sub-issues for the sake of having more than one.

```markdown
## Sub-Issue 2: Booking Service Layer

**Depends on:** Sub-issue 1 (Controller stubs must exist)
**Blocks:** Sub-issue 3 (Notification service needs `BookingResult` type)

### Tasks
- Implement `process_booking()` per Design Doc
- Implement `validate_slot_availability()` per Design Doc
- Fill in edge case tests marked TODO in stubs

### Acceptance Criteria
- All base acceptance tests passing
- `SlotUnavailableError` raised on race condition during hold
- Notification failure does not fail booking

### Code References
- `src/services/appointment_service.py` — primary file
- `src/repositories/slot_repository.py` — dependency, must exist first
- Design Doc §File Map — `appointment_service` section

### Technical Guidelines
- Soft-lock pattern, not DB transaction lock (see Design Doc A1.1)
- No direct slot state mutation outside this service

### Non-Functional Constraints
- p99 latency budget: 200ms (excl. notification fire)
- Idempotent on `(patient_id, slot_id)` within 30s
- Notification failure logged at WARN, never raised
```

Notes:

- **No line numbers in code references.** They will go stale immediately. File-level only — the executor can find what it needs.
- **Technical guidelines** carry forward decisions that are easy to forget mid-implementation (especially rejected-approach reasoning).
- **Non-functional constraints** are pulled directly from the Design Doc's NFR section for the relevant file(s). Always include them on sub-issues whose files have NFRs declared — the executor does not read the full Design Doc, so this is the only place they will see these constraints.

## How to Decide Batches

Use the dependency graph implied by the Design Doc + stubs:

- **A blocks B** when B's stubs reference symbols defined in A's stubs, or when A's behavior contract is needed to write B's tests meaningfully.
- **A and B are parallel** when they touch disjoint files and do not depend on each other's output.
- A coherent sub-issue is roughly: "one self-contained file or tightly-coupled small set of files that ship together."

Apply the same independent-domain logic as `superpowers/dispatching-parallel-agents`: parallel only when there is no shared state and no sequential dependency.

When in doubt, prefer fewer larger batches over many tiny ones — the per-batch review checkpoint in `builder` is where the human re-engages, and too many checkpoints add friction.

## Linear-Specific Notes

When using Linear:

- Create the parent issue with the full markdown above as its description.
- Create sub-issues as Linear sub-issues of the parent.
- Use Linear's relationship features (blocks/blocked-by) where supported; mirror them in the description text either way so they are visible inline.
- Set status to a sensible "Backlog" or "Todo" — `builder` will move them to "In Progress" / "Done" as it executes.
- Surface the created issue URLs back to the user.

## Markdown-Specific Notes

When writing files:

```
docs/issues/<feature>/
  parent.md
  sub-1-<short-name>.md
  sub-2-<short-name>.md
  ...
```

`builder` will read these directly and update a status field at the top of each sub-issue file as work progresses.

## Hand-Off

End by stating:

- The chosen tracking mode (Linear or markdown) and where the issues live.
- The batch execution plan in one block.
- "Ready to invoke `meridian/builder` when you are."

Do not invoke `builder` automatically. The user decides when to start execution.
