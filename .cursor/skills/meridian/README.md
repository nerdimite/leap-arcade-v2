# Meridian

A deliberate, top-down, LLD-in-code workflow for serious work. The collection has three sub-skills that chain together:

1. **`deep-design`** — design jam that walks the call graph from intent to execution and produces stub code + minimal docstrings + failing acceptance tests + a Design Doc, all written inline as the jam progresses.
2. **`issue-planner`** — translates the design output into a parent issue + dependency-flagged sub-issues with an explicit batch execution plan. Linear MCP if available (asks first), markdown otherwise.
3. **`builder`** — orchestrator that drives execution through the batch plan by spawning fast-model subagent executors per sub-issue, then writes per-batch implementation notes for the human to review before commit.

Use the sub-skills directly (e.g. "use meridian/deep-design") or invoke them in sequence as the work progresses.

## Philosophy

- **Human is the brain. AI is the hands.** The user stays in control of design decisions and final review. The AI types, drafts, traverses, and executes.
- **Design lives in code.** Stubs + minimal docstrings + failing tests are the design artifact. The Design Doc is a thin running-notes index over them, not a prose tome to re-review.
- **Failing tests as acceptance criteria, not coverage.** Tests are written during design to define exact expected behaviour, not after-the-fact for a coverage number.
- **Three control points, not constant oversight.** You're deep in the design jam, hands-off during execution, deliberate at the per-batch review and commit. No spec-reviewer / code-quality-reviewer ceremony — your eyes are the final gate.
- **No auto-commits.** The builder stages, never commits. You commit when you've walked the reading order and approved.

## When to Use

Use Meridian for: major features, new services, major refactors, anything that benefits from a real top-down design pass.

It is not gatekept — if you want to use it on a small CRUD addition because you feel like being deliberate, that is fine. But the overhead is not worth it for trivial bug fixes.

## Flow at a Glance

```
intent
  │
  ▼
[deep-design]    ──► stubs + tests + Design Doc (docs/design/<feature>.md)
  │
  ▼
[issue-planner]  ──► parent issue + sub-issues + batch execution plan
  │                  (Linear if asked, else docs/issues/<feature>/)
  ▼
[builder]        ──► orchestrator + fast-model executor subagents
                     per-batch implementation notes
                     staged changes, awaiting your commit
```

Each sub-skill is documented standalone — read its `SKILL.md` when you invoke it. The three are tightly coupled by their input/output formats; do not mix-and-match with other planning/execution skills mid-flow without translating artifacts.

## What This Replaces (and Why)

This workflow exists because the existing `superpowers/{brainstorming → writing-plans → subagent-driven-development}` chain has real strengths but a few specific gaps for this user:

- Design docs and plan docs become too verbose to humanly review.
- Spec-compliance and code-quality reviewer subagents are redundant when the human is doing the PR review anyway — they add hours without buying much.
- Auto-commits remove the human's natural review-and-commit checkpoint.
- The user wanted to be more *involved* during design (jamming layer-by-layer at the function level), not less.

Meridian keeps the good ideas — TDD iron law, dispatching parallel agents, severity-aware push-back, junior-dev-handoff framing — and reshapes the structure around the three control points described above.

## Cross-Cutting Constraints

These apply to all three sub-skills:

- **Read the patterns folder first.** If the repo has a `docs/patterns/`, `.cursor/rules/`, `AGENTS.md`, `.impeccable.md`, or equivalent, read it before starting. Cross-cutting constraints belong there, not in the per-session capture.
- **State assumptions, do not interrogate.** Open with a brief "here is what I read, here is what I assume" summary and let the user correct only what is wrong. Avoid upfront questionnaires.
- **Senior-engineer judgment throughout.** Check existing code before proposing new things. Notice extraction opportunities. Recommend with reasoning. Push back proportionally to severity.
- **Linear MCP is opt-in per session.** Even if connected, ask the user whether to use it. Default to markdown.

## Sub-Skill Index

- [deep-design/SKILL.md](deep-design/SKILL.md) — the design jam
- [issue-planner/SKILL.md](issue-planner/SKILL.md) — design-to-issues translator
- [builder/SKILL.md](builder/SKILL.md) — orchestrator + executor subagents

## References

- [references/testing-guidelines.md](references/testing-guidelines.md) — test-writing principles, pytest patterns, mock-vs-fake guidance, and anti-patterns. Required reading for writing or modifying tests in any Meridian phase.
- [references/glossary.md](references/glossary.md) — shared vocabulary (phases, roles, artifacts, modes, naming conventions).
