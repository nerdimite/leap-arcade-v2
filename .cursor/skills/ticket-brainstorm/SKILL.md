---
name: ticket-brainstorm
description: "Facilitate collaborative requirements discussion before creating a PM ticket. Use when the user wants to brainstorm, discuss, define, or refine requirements for a ticket, issue, or task — before actually writing it in any PM tool."
---

# Ticket Brainstorm

Refine a vague idea into well-defined requirements through conversational Q&A, then hand off to the appropriate PM tool for ticket creation.

<HARD-GATE>
Do NOT invoke any PM skill, MCP tool, or CLI command to create a ticket until the user explicitly says they are ready. Stay in requirements-discovery mode until then.
</HARD-GATE>

## Checklist

Create a task for each step and complete them in order:

1. **Understand the problem** — what needs to happen and why
2. **Ask clarifying questions** — one at a time, refine scope and acceptance criteria
3. **Summarize requirements** — present back to user for validation
4. **Transition to ticket creation** — detect available PM tool and offer handoff

## The Process

**Understanding the problem:**

- Skim relevant code or docs only if needed for context — don't deep-dive
- Ask the user to describe the problem or need in their own words
- Listen for: who is affected, what's broken or missing, why it matters now

**Asking clarifying questions:**

- Use the `AskQuestion` tool when available; fall back to conversational questions
- One question per message — don't overwhelm
- Prefer multiple-choice when possible
- Cover these areas (skip what's already clear):
  - **Scope** — what's in, what's explicitly out
  - **Acceptance criteria** — what does "done" look like
  - **Edge cases** — anything tricky or ambiguous
  - **Dependencies** — blocked by or blocking anything
  - **Priority / urgency** — how important relative to other work
  - **Assignee** — who should own this

**Summarizing requirements:**

- Present a concise summary: problem statement, scope, acceptance criteria, priority
- Ask if anything is missing or wrong
- Revise until the user confirms

## Transition to Ticket Creation

When the user is ready to create the ticket:

1. **Check for PM skills** — look for skills like `linear-issue` or similar PM-focused skills
2. **Check for PM MCP servers** — look for Linear, ClickUp, Jira, or other PM MCPs in the available servers
3. **Fall back to GitHub Issues** — if no PM skill/MCP is available and the workspace is a git repo, offer to create a GitHub Issue via `gh issue create`
4. **Manual fallback** — if nothing is available, present the requirements formatted as a ready-to-paste ticket body

Invoke the detected skill or tool with the refined requirements as context. The terminal state is handing off to the PM tool — do NOT begin implementation planning.

## Key Principles

- **Requirements only** — no architecture, no design, no implementation details
- **One question at a time** — keep it conversational
- **Multiple choice preferred** — easier to answer than open-ended
- **YAGNI** — push back on scope creep during discussion
- **Tool-agnostic** — work with whatever PM tool is available
- **Stay in discovery** — don't rush to ticket creation; the user decides when they're ready
