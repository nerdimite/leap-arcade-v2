---
name: meridian-builder
description: Orchestrator that executes a meridian/issue-planner output by spawning fast-model executor subagents (e.g. composer-2-fast) per sub-issue, batch by batch. Writes implementation notes after each batch with reading order, decisions made, flags, and test status — then stops for human review (default mode) or continues (auto mode). Never commits; commit workflow is left entirely to the human. Use after meridian/issue-planner has produced a parent issue and sub-issues and you are ready to implement.
---

# Meridian — Builder

The third phase of [meridian](../README.md). The orchestrator (you, full model) drives execution; executor subagents (fast model) do the implementation work. Per-batch implementation notes are written for the human to review before any commit.

## Mental Model

- **Orchestrator (full model) = brain.** Reads parent issue + Design Doc, plans, dispatches, judges, consolidates, writes implementation notes.
- **Executor subagents (fast model) = hands.** Narrow, focused, one sub-issue at a time. Implement → run tests → report back.
- **Human = final gate.** Reviews each batch's implementation notes, walks the reading order. The commit workflow itself (when, how, granularity) lives outside Meridian — the orchestrator just never commits on its own.

There are no spec-compliance or code-quality reviewer subagents. The human's review *is* the review.

## Opening

1. Ask: "Tracking via Linear or markdown?" (even if Linear MCP is present, do not assume).
2. Read the parent issue → grab Intent, Overall Acceptance Criteria, Execution Plan (batches).
3. Read the Design Doc end-to-end. This is your reference throughout — do not delegate it to the executors.
4. Ask the user which mode:
   - **Default mode** — stop after each batch for review.
   - **Auto mode** — continue through all batches without stopping; consolidated note at the very end.

State the chosen mode and the batch plan back, then begin Batch 1.

## Per-Batch Loop

For each batch in order:

1. For each sub-issue in the batch:
   - Mark sub-issue "In Progress" (Linear status update or markdown status field).
   - Construct the executor prompt (see "Executor Prompt Template" below).
   - **Spawn a subagent** via the Cursor `Task` tool with `subagent_type: generalPurpose` and `model: composer-2-fast` (or another fast slug if explicitly chosen). See "Spawning Executor Subagents" below for the exact mechanics. Sub-issues that are independent within the batch can be spawned in parallel by issuing multiple `Task` calls in a single message; sequential within-batch dependencies are unusual but if present, run sequentially.
   - Receive the executor's report.
   - **Two-attempt rule:** if the executor reports tests still failing after one self-correction attempt, do not let it spiral. Surface the specific failure in the implementation notes and stop the batch (or that sub-issue's chain) — escalate to the human in default mode, or flag-and-continue in auto mode at your judgment.
   - On success, mark sub-issue "Done".
2. Once all sub-issues in the batch are done (or escalated), **write the implementation notes for the batch**.
3. **Default mode:** stop and wait for user review.  **Auto mode:** continue to the next batch.

Repeat until all batches are done. Then write the final consolidated implementation note.

## Spawning Executor Subagents

Cursor 3 supports native subagent dispatch via the `Task` tool. The orchestrator (you) just calls it; Cursor handles the subprocess.

```
Task(
  description: "<short title — e.g. 'Implement booking service'>",
  prompt: "<the full Executor Prompt — see template below>",
  subagent_type: "generalPurpose",
  model: "composer-2-fast",
  run_in_background: false
)
```

Notes:

- **Use a fast model by default** (`composer-2-fast` or whichever fast slug the user has standardized on). Executors do narrow, well-specified work — they do not need full-model reasoning.
- **Parallel within a batch:** issue multiple `Task` calls in one message to dispatch executors concurrently. Only do this for sub-issues with disjoint files; same-file conflicts will corrupt state.
- **Sequential within a batch:** await one before issuing the next.
- **`run_in_background: false`** is the default — you want the result inline so you can write the implementation notes. Use background only if you need to multitask, which is uncommon for the orchestrator role.
- **Each executor invocation is fresh context.** The orchestrator does not get to share its in-memory understanding for free — everything the executor needs must be in the prompt. That is why the prompt template inlines file contents, the relevant Design Doc excerpt, and the testing-guidelines pointer.

## Executor Prompt Template

The executor is a fast model with narrow context. Give it everything it needs in the prompt — do not make it read large files unnecessarily.

```markdown
You are an executor subagent for the Meridian builder. Implement ONE sub-issue.

## Sub-Issue
<paste the full sub-issue markdown — tasks, AC, code references, technical guidelines, depends-on/blocks>

## Relevant File Contents
<paste the current contents of files in Code References, especially the stub file>

## Design Doc Excerpt
<paste only the relevant File Map section(s) and any referenced Appendix entries>

## Required Reading
Before writing or modifying any test, read `.cursor/skills/meridian/references/testing-guidelines.md`. Apply its anti-patterns and mock-vs-fake guidance.

## Your Job (Red → Green → Refactor)
The stubs already raise `NotImplementedError` and the failing tests already exist — that is the RED state. Your job is to make them green, then clean up. Do not invent new behaviour beyond what the tests and Design Doc specify.

1. **Confirm RED first.** Run `pytest <test paths from Code References> -v`. Verify the listed tests fail because the function is unimplemented (not because of import errors, fixture typos, etc.). If failures look wrong (collection errors, import failures), fix those before writing any implementation.
2. **Fill in the TODO edge-case tests** called out as comments above the test classes. Treat them as part of the spec — do not skip.
3. **Confirm those new tests also fail** for the right reason before implementing.
4. **Write the minimal implementation** to make the tests pass. Replace `raise NotImplementedError` with real logic. Do NOT add features, options, or "improvements" the tests do not ask for (YAGNI).
5. **Confirm GREEN.** Run the full test path. All targeted tests pass, no new failures elsewhere, output is clean (no warnings, no stray prints).
6. **Refactor only while green.** Remove duplication, improve names, extract helpers — re-running tests after each meaningful change. Never refactor with red tests.
7. **If anything is genuinely uncertain** (architectural call, cross-cutting concern, ambiguous spec), STOP and report — do not guess.

## Test Discipline (non-negotiable)
- **Do not weaken or delete a failing test to make it pass.** If a test seems wrong, flag it in your report — do not silently rewrite it.
- **Assert on observable behavior**, not on mock call counts. Use the fakes already set up in the test file; if you must add a new collaborator double, prefer a fake over `MagicMock`.
- **No production code without a failing test first.** If you discover behaviour that needs to exist but has no test, write the failing test, watch it fail, then implement.
- **Tests must be deterministic.** No real network, no real DB, no `time.sleep`, no flaky timing. Inject the clock and use fakes.

When filling in TODO edge-case tests or adding any new test, follow [../references/testing-guidelines.md](../references/testing-guidelines.md) — anti-patterns table, mock-vs-fake-vs-stub guidance, and the full set of test-writing principles. Include a one-line note in the prompt to executor subagents pointing them at this file.

## Reporting Format (return verbatim)
- **What I did:** <bullet list, one line each>
- **Tests:** <X/Y passing, list of any failures with the exact pytest node ids>
- **TODO edge cases filled in:** <list — confirm none were skipped>
- **Decisions made:** <each decision + one-line reasoning>
- **Uncertain / want input:** <anything you flagged instead of guessing>
- **Files changed:** <list>

## Constraints
- Do NOT commit. Do NOT stage. Leave changes in the working tree as-is — the orchestrator and the human handle commit workflow themselves.
- Do NOT modify files outside the Code References without explicit reason (call it out if you do).
- Do NOT add features beyond the sub-issue scope.
- Do NOT modify a failing test to make it pass — flag it instead.
- If tests fail after one self-correction attempt, STOP and report the failure — do not keep trying.
```

Tighten or expand based on sub-issue size, but keep the spirit: focused, self-contained, structured report.

## Implementation Notes Format

Per batch:

```markdown
# Implementation Notes — Batch <N> (<feature>)
Date: YYYY-MM-DD

## What Was Done
- Sub-issue 1: <one-line summary>
- Sub-issue 2: <one-line summary>

## Reading Order
1. `path/to/file.py` — start here, this is the entry point for the batch
2. `path/to/file.py` — read second, contains the core logic
3. `path/to/file.py` — skim, mostly mechanical

## Decisions Made
- <decision> — <one-line reasoning> — okay?
- <decision> — <one-line reasoning> — okay?

## Flags
- <specific thing> — <why flagging> — <what you need to decide>

## Test Status
- Sub-issue 1: X/Y passing
- Sub-issue 2: X/Y passing
- Failing: `test_name` — <why it's failing if known>

## Files Changed
- `path/to/file.py`
- `path/to/file.py`

> Changes are in the working tree, untouched by git. Review the reading order above; staging and committing is yours.
```

The final consolidated note (after all batches) follows the same format, scoped across batches, and ends with: "Ready for your review."

## Junior-Dev-to-Senior-Dev Voice

The implementation notes are the executor's "junior dev explaining to senior dev" handoff. Frame decisions as "I did X — is this what you wanted?" rather than "X has been implemented." The reading order is curated specifically for tractable human review — do not just dump every changed file in alphabetical order; order by what the human needs to understand first.

## Amendment Loop — When the Design Was Wrong

Sometimes execution reveals that the design itself is wrong: a missed branch, a contract that does not actually work, a behaviour that conflicts with reality the jam did not see. There must be a defined path back, or the "three control points" model breaks down.

Two flavors:

**Patch in place (small)** — the design needs a tweak, not a rethink. E.g. one extra parameter, one renamed return field, one missed error case.
1. Orchestrator updates the affected stub signature(s) and the matching Design Doc entry inline.
2. Updates the affected sub-issue(s) — Tasks, AC, Code References — with a brief "Amended: <date> — <reason>" line at the top.
3. Re-spawns the executor for the affected sub-issue with the amended prompt.
4. Records the amendment in the next batch's implementation notes under a new "Amendments" section so the human review pass sees what changed and why.

**Re-jam (large)** — the design needs a real rethink, not a patch. E.g. a whole branch was missed, the chosen architecture does not work, an NFR is unsatisfiable as designed.
1. **Stop the batch.** Do not keep executing on a broken design.
2. Surface the issue to the human in the current batch's implementation notes under "Design Issue Discovered" — what was found, why it breaks the design, what is affected.
3. Hand back to the human to re-invoke `meridian/deep-design` (in extension mode this time, since the partial implementation is part of the existing context).
4. After the re-jam updates the Design Doc and stubs, the human re-invokes `meridian/issue-planner` to amend or replace the affected sub-issues.
5. The human re-invokes `meridian/builder` to resume.

Judging which flavor: if the amendment touches one sub-issue and does not change the batch plan or the file map structure, it is a patch. If it changes the file map, the batch plan, or any cross-cutting decision, it is a re-jam. When in doubt, escalate to re-jam — silently patching a deeper problem accumulates worse debt than pausing.

The orchestrator never makes a re-jam call unilaterally. It surfaces and stops.

## Hard Rules

- **Never commit. Never stage.** Leave the working tree as-is. The human owns the entire commit workflow.
- **Two-attempt max** per executor on failing tests. Then escalate, do not spiral.
- **No spec/quality reviewer subagents.** The human is the reviewer.
- **Respect dependency ordering.** Never start a sub-issue whose blockers are not done.
- **Per-batch implementation notes always**, even in auto mode. The notes are also the audit trail.
- **No dispatching parallel implementer subagents on the same files.** Within a batch, parallelize only across disjoint files.
- **If the executor escalates,** make the call yourself with full context — do not just re-spawn the same subagent blindly.
- **Surface design issues, do not patch them silently.** If the design seems wrong, follow the Amendment Loop above.

## Status Updates

- **Linear mode:** update sub-issue status in real time (In Progress when spawned, Done when complete, Blocked if escalated unresolved). The Linear board reflects live progress.
- **Markdown mode:** update a `Status:` line at the top of each sub-issue file at the same moments.

## Closing

After the final consolidated note, stop. Do not commit. Do not stage. Do not move to anything else. The human takes it from here.
