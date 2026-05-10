# Fast Implementer Subagent Prompt Template

Use this template when dispatching an implementer subagent for multiple tasks (batch or one-shot).

```
Task tool (general-purpose):
  description: "Implement [batch/all] tasks: [brief summary]"
  prompt: |
    You are implementing multiple tasks as a batch.

    ## Tasks

    [For each task, paste the FULL TEXT from the plan. Don't make the subagent read the file.]

    ### Task N: [task name]
    [Full task description, steps, files, acceptance criteria]

    ### Task M: [task name]
    [Full task description, steps, files, acceptance criteria]

    [... repeat for all tasks in this batch ...]

    ## Context

    [Scene-setting: where these tasks fit in the overall plan, dependencies between them,
     architectural context, any decisions already made in prior batches]

    ## Before You Begin

    If you have questions about:
    - The requirements or acceptance criteria for any task
    - The approach or implementation strategy
    - Dependencies between these tasks
    - Anything unclear in any task description

    **Ask them now.** Raise all concerns before starting work.

    ## Your Job

    Once you're clear on requirements:
    1. Implement each task in order
    2. Write tests for each task (following TDD if task says to)
    3. Verify each task's implementation works before moving to the next
    4. **Commit after each task** (atomic commits, not one giant commit)
    5. After all tasks: self-review the full batch (see below)
    6. Report back

    Work from: [directory]

    **While you work:** If you encounter something unexpected or unclear, **ask questions**.
    It's always OK to pause and clarify. Don't guess or make assumptions.

    ## Commit Discipline

    Even though you're implementing multiple tasks, commit per task (or per logical chunk).
    Each commit should be independently meaningful. Use the **commit** skill which follows
    the conventional commit message format.

    Bad: One commit with "implement all tasks"
    Good: Separate commits for each task or logical unit of work

    ## Before Reporting Back: Self-Review

    Review ALL your work with fresh eyes. For each task, ask yourself:

    **Completeness:**
    - Did I fully implement everything in the spec?
    - Did I miss any requirements in any task?
    - Are there edge cases I didn't handle?

    **Quality:**
    - Is this my best work?
    - Are names clear and accurate?
    - Is the code clean and maintainable?

    **Discipline:**
    - Did I avoid overbuilding (YAGNI)?
    - Did I only build what was requested for each task?
    - Did I follow existing patterns in the codebase?

    **Testing:**
    - Do tests actually verify behavior (not just mock behavior)?
    - Are tests comprehensive for each task?

    **Cross-task consistency:**
    - Do the tasks work together correctly?
    - Are naming conventions consistent across tasks?
    - No duplicate code across tasks?

    If you find issues during self-review, fix them now before reporting.

    ## Report Format

    When done, report per task:

    ### Task N: [name]
    - What you implemented
    - What you tested and test results
    - Files changed
    - Commit SHA

    ### Task M: [name]
    - [same format]

    ### Overall
    - Self-review findings (if any)
    - Cross-task concerns (if any)
    - Any issues or open questions
```
