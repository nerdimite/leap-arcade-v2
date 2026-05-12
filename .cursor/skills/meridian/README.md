# Meridian Skills

Canonical home for the Meridian skill set. Per-project consumers symlink or snapshot this folder into their `.cursor/skills/meridian/`.

A deliberate, top-down, LLD-in-code workflow for serious work. The collection has three sub-skills that chain together:

1. **`deep-design`** — free-form design jam that walks the call graph from intent to execution through conversation, then compiles a YAML spec into an interactive HTML design map via [meridian-cli](../). No code is written during design.
2. **`issue-planner`** — translates the design output into a parent issue + dependency-flagged sub-issues with an explicit batch execution plan. Linear MCP if available (asks first), markdown otherwise.
3. **`builder`** — orchestrator that drives execution through the batch plan by spawning fast-model subagent executors per sub-issue, then writes per-batch implementation notes for the human to review before commit.

Use the sub-skills directly (e.g. "use meridian/deep-design") or invoke them in sequence as the work progresses.

## Philosophy

- **Human is the brain. AI is the hands.** The user stays in control of design decisions and final review. The AI types, drafts, traverses, and executes.
- **Design is conversation first, artifact second.** Free-form discussion without structural interruptions, then a YAML spec compiled to an interactive HTML map on demand. No stubs or tests during design — those happen during implementation.
- **Spec is the source of truth.** The design map HTML is a build artifact. The YAML is what you edit, version, and review.
- **Failing tests as acceptance criteria, not coverage.** Test plans are captured in the spec per node. Tests are written during implementation (stub → failing test → implement), not as separate design artifacts.
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
[deep-design]    ──► <feature>.meridian.yaml + compiled HTML map + transcript
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

- [deep-design/spec_authoring_guide.md](deep-design/spec_authoring_guide.md) — how to author the YAML spec consumed by `meridian compile`. Required reading for `deep-design` (colocated with that skill).
- [deep-design/sample_spec.yaml](deep-design/sample_spec.yaml) — canonical, full-fidelity reference spec (Rapid Fire). Copy its shape when in doubt.
- [references/testing-guidelines.md](references/testing-guidelines.md) — test-writing principles, pytest patterns, mock-vs-fake guidance, and anti-patterns. Required reading for writing or modifying tests in `builder`.
- [references/glossary.md](references/glossary.md) — shared vocabulary (phases, roles, artifacts, modes, naming conventions).
