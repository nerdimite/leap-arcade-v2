---
name: agents-md
description: Scaffold a new AGENTS.md file or audit an existing one against research-backed best practices. Use when the user asks to create, write, review, improve, or scaffold an AGENTS.md (or CLAUDE.md) file, or when setting up a new project's agent configuration.
---

# AGENTS.md Scaffolding & Audit

Write or audit the highest-leverage configuration file for coding agents. Every line goes into every session — make each one count.

**Announce at start:** "I'm using the agents-md skill to [scaffold / audit] the AGENTS.md file."

## Decide Mode

- **AGENTS.md exists and is non-empty** → run Audit workflow
- **AGENTS.md is empty or missing** → run Scaffold workflow
- User can request either mode explicitly

---

## Scaffold Workflow

### Phase 1: Gather Context

Explore the project before asking questions:

1. Read `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, or equivalent
2. Check top-level directory structure (one level deep only)
3. Look for existing docs, READMEs, CI configs
4. Check for monorepo indicators (workspaces, multiple service dirs)

### Phase 2: Ask the Three Questions

Ask the user **one question at a time**. Prefer multiple choice when possible.

**WHAT** — Tech stack, project structure, what each part does:
- "What's the tech stack?" (often inferrable from Phase 1 — confirm rather than ask)
- For monorepos: "What are the apps/packages and what does each one do?"
- "Any non-obvious project structure the agent should know about?"

**WHY** — Purpose and intent:
- "In one sentence, what does this project do?"
- "What are the key domain concepts an agent needs to understand?"

**HOW** — Build, test, verify:
- "How do you build and run this project?"
- "How do you run tests?"
- "Any non-standard tooling?" (e.g., `uv` not `pip`, `bun` not `npm`, `just` not `make`)
- "Any critical gotchas an agent should know?" (e.g., "never modify migrations directly")

### Phase 3: Draft AGENTS.md

Write the file following the Content Rules below. Present it to the user for review before saving.

### Phase 4: Progressive Disclosure Setup

Create `docs/patterns/` with an `index.md` listing placeholders for future pattern docs:

```markdown
# Pattern Documentation Index

Task-specific docs that agents read on demand. Add files here as needed.

| File | Purpose |
|------|---------|
| (add entries as you create pattern docs) |
```

Reference this directory from AGENTS.md so agents know where to find deeper docs.

### Phase 5: Save & Commit

1. Write AGENTS.md to the project root
2. Create `docs/patterns/index.md`
3. Offer to commit using the **commit** skill

---

## Audit Workflow

### Step 1: Read the existing AGENTS.md

### Step 2: Check against each rule

Run through the Audit Checklist below. For each issue found, note:
- **Line(s)** affected
- **Issue** — what's wrong
- **Fix** — specific suggestion

### Step 3: Present findings

Group by severity:
- **Remove** — content that actively hurts (auto-generated fluff, code style rules, stale snippets)
- **Move** — content that belongs in `docs/patterns/` instead (task-specific instructions)
- **Revise** — content that should stay but needs tightening
- **Missing** — required sections (Tech Stack & Architecture, Project Purpose, Development Workflow, Dos and Don'ts) that are absent

### Step 4: Offer to apply fixes

After user approves, edit the file and offer to commit.

---

## Content Rules

These rules govern what goes into AGENTS.md. For the research behind them, see [references/best-practices.md](references/best-practices.md).

### Target: Under 300 lines, ideally under 100

Every line goes into every session. Ruthlessly cut anything that isn't universally applicable.

### Five Required Sections

**WHAT** — Stack, structure, key components:
```markdown
## Tech Stack & Architecture

- Python 3.12 / FastAPI / PostgreSQL / Redis
- Monorepo: `services/api`, `services/worker`, `packages/shared`
- `services/api` — REST API serving the frontend
- `services/worker` — Background job processor
- `packages/shared` — Shared types and utilities
```

**WHY** — Purpose and domain context:
```markdown
## Project Purpose

Invoice processing platform. Extracts line items from uploaded PDFs,
matches them against purchase orders, flags discrepancies for review.

Key domain terms: invoice, line item, purchase order, discrepancy, review queue.
```

**HOW** — Build, test, verify:
```markdown
## Development Workflow

- Build: `uv sync` (NOT pip install)
- Run: `docker compose up`
- Test: `pytest` from repo root
- Lint: `ruff check . --fix && ruff format .`
- Type check: `pyright`
```

**DOS AND DON'TS** — Human-curated project rules and constraints:

These are known project rules written by the team — things agents should always do or never do. Unlike Agent Memory (which is auto-maintained by hooks), this section is manually curated.

When scaffolding, seed it with a placeholder:
```markdown
## Dos and Don'ts

<!-- Add project-specific rules here. Each entry should be a short, direct instruction. -->

(none yet — add rules as you establish project conventions)
```

When populated, it looks like:
```markdown
## Dos and Don'ts

- Use `uv`, not pip — all dependency management goes through uv
- Run all commands from `backend/`, not the repo root
- Use `BaseServiceException` subclasses for service errors, not raw HTTPException
- Put new API routes in the router file, not in `main.py`
- Name migration files descriptively (`add_user_email_column`), not auto-generated
- Never modify migrations directly after they've been applied
```

**AGENT MEMORY** — Living section for learned preferences and workspace facts:

This is a living section maintained both by humans and by automated hooks (like the continual-learning hook). It has two subsections:

- `### Learned User Preferences` — Short "do X, not Y" corrections from actual usage. Grows as the human observes agent behavior that doesn't match their preferences.
- `### Learned Workspace Facts` — Durable facts about the workspace that agents need to know (key files, team names, project relationships).

When scaffolding, seed it with a placeholder:
```markdown
## Agent Memory

### Learned User Preferences

<!-- Add rules here as you notice agents doing things the wrong way.
     Each rule should be a short, direct correction: "do X, not Y."
     This section is also auto-maintained by the continual-learning hook. -->

(none yet — update this section as you work with agents on this codebase)

### Learned Workspace Facts

<!-- Durable facts about the workspace. Auto-maintained by the continual-learning hook. -->

(none yet — facts are added as agents learn about the codebase)
```

When populated, it looks like:
```markdown
## Agent Memory

### Learned User Preferences

- When creating Linear issues, put status, priority, assignee, and labels in Linear MCP fields; do not add a Metadata section in the issue body.
- Use `raise HTTPException` with `detail=`, not custom exception classes
- Put new API routes in the router file, not in `main.py`

### Learned Workspace Facts

- `docs/issues-rd.md` defines the backend PRD and issue requirements for the Cursor Fleet Dashboard.
- Internal Utilities is the Linear team for agent-fleet backend work.
```

These entries are short, authoritative, and universally applicable — exactly the kind of instruction agents follow well. They stay in AGENTS.md (not in `docs/patterns/`) because they apply to every session.

### Do Include

- Non-obvious tooling choices (tools mentioned get used **160x** more)
- Critical constraints and gotchas ("never modify migrations directly")
- Dos and Don'ts — human-curated project rules and constraints
- Agent Memory — learned preferences ("do X, not Y") and durable workspace facts
- Pointer to `docs/patterns/` for task-specific docs
- Environment setup steps if non-trivial

### Do NOT Include

- **Codebase overviews or directory trees** — agents discover structure themselves
- **Code style guidelines** — use linters/formatters instead (faster, cheaper, deterministic)
- **Task-specific instructions** — move to `docs/patterns/`
- **Code snippets** — they go stale; use `file:line` pointers instead
- **Auto-generated content** — reduces success rate ~3%, increases cost 20%+

### Use Progressive Disclosure

Reference deeper docs rather than embedding them:

```markdown
## Reference Docs

Task-specific guidance lives in `docs/patterns/`:

| Doc | When to read |
|-----|-------------|
| `docs/patterns/testing.md` | Before writing or modifying tests |
| `docs/patterns/migrations.md` | Before creating database migrations |
```

### Use Pointers Over Copies

```markdown
# Good — points to the source of truth
See auth middleware implementation: `src/middleware/auth.ts:15-45`

# Bad — will go stale
Here's how auth works:
\`\`\`typescript
// 50 lines of code that will drift from reality
\`\`\`
```

---

## Audit Checklist

| # | Check | Pass criteria |
|---|-------|---------------|
| 1 | Line count | < 300 lines (ideally < 100) |
| 2 | Has Tech Stack & Architecture section | Stack + structure + component purposes |
| 3 | Has Project Purpose section | Project purpose + domain terms |
| 4 | Has Development Workflow section | Build + test + lint commands |
| 5 | Has Dos and Don'ts section | Present (even if empty placeholder) for human-curated rules |
| 6 | Has Agent Memory section | Present (even if empty placeholder) with Learned User Preferences and Learned Workspace Facts subsections |
| 7 | No code style rules | Style enforcement belongs in linters |
| 8 | No directory trees | Agents discover structure themselves |
| 9 | No embedded code | Uses `file:line` pointers instead |
| 10 | No task-specific instructions | Moved to `docs/patterns/` |
| 11 | No auto-generated fluff | Every line is deliberate and useful |
| 12 | Agent Memory entries are concise | Each preference is "do X, not Y" — short and direct; each fact is a single sentence |
| 13 | Non-obvious tools mentioned | e.g., `uv`, `bun`, `just` — these get used 160x more |
| 14 | Progressive disclosure | Points to deeper docs, doesn't embed them |
| 15 | Critical gotchas present | Things that would waste an agent's time if unknown |

---

## Anti-Patterns

- **"Kitchen sink" files** — stuffing everything in AGENTS.md degrades instruction-following uniformly across all instructions
- **Auto-generating the file** — LLM-generated files are redundant with existing docs and hurt performance
- **Detailed codebase tours** — agents navigate fine without them; these just consume tokens
- **Embedded code** — drifts from reality; use pointers
- **Style guides** — use `pyright`, `ruff`, `eslint`, `prettier`, `biome` instead
