# Batch Spec Compliance Reviewer Prompt Template

Use this template when dispatching a spec compliance reviewer for multiple tasks (batch or one-shot).

**Purpose:** Verify implementer built what was requested for ALL tasks (nothing more, nothing less)

```
Task tool (general-purpose):
  description: "Review spec compliance for [batch/all] tasks"
  prompt: |
    You are reviewing whether an implementation matches its specification
    across multiple tasks.

    ## Tasks and Their Requirements

    [For each task, paste the FULL TEXT of requirements]

    ### Task N: [task name]
    **Requirements:**
    [Full task requirements from the plan]

    ### Task M: [task name]
    **Requirements:**
    [Full task requirements from the plan]

    [... repeat for all tasks in this batch ...]

    ## What Implementer Claims They Built

    [Paste the implementer's per-task report]

    ## CRITICAL: Do Not Trust the Report

    The implementer finished multiple tasks in a single session. Their report may be
    incomplete, inaccurate, or optimistic — especially for later tasks where context
    fatigue sets in. You MUST verify everything independently.

    **DO NOT:**
    - Take their word for what they implemented
    - Trust their claims about completeness
    - Accept their interpretation of requirements
    - Assume later tasks got the same attention as earlier ones

    **DO:**
    - Read the actual code for every task
    - Compare actual implementation to requirements line by line, task by task
    - Check for missing pieces they claimed to implement
    - Look for extra features they didn't mention
    - Pay extra attention to the LAST tasks (fatigue errors are most common there)

    ## Your Job

    For EACH task, read the implementation code and verify:

    **Missing requirements:**
    - Did they implement everything that was requested?
    - Are there requirements they skipped or missed?
    - Did they claim something works but didn't actually implement it?

    **Extra/unneeded work:**
    - Did they build things that weren't requested?
    - Did they over-engineer or add unnecessary features?

    **Misunderstandings:**
    - Did they interpret requirements differently than intended?
    - Did they solve the wrong problem?

    **Cross-task issues:**
    - Are there inconsistencies between tasks?
    - Did they duplicate work across tasks that should share code?
    - Did they miss integration points between tasks?

    **Verify by reading code, not by trusting report.**

    ## Report Format

    Report per task, then an overall summary:

    ### Task N: [name]
    - ✅ Spec compliant OR ❌ Issues found
    - [If issues: list specifically what's missing or extra, with file:line references]

    ### Task M: [name]
    - ✅ Spec compliant OR ❌ Issues found
    - [If issues: list]

    ### Summary
    - Tasks compliant: N/M
    - Tasks with issues: N/M
    - [If issues in > half the tasks, explicitly flag: "BAIL-OUT RECOMMENDED: Issues found
      in more than half the tasks. Consider switching to per-task mode."]

    IMPORTANT: The controller uses your task-level pass/fail counts to decide whether
    to bail out of fast mode. Be precise — mark a task as ❌ only if there are genuine
    spec gaps, not style preferences.
```
