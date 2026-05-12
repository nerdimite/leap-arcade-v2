# Spec Authoring Guide

How to author a `*.meridian.yaml` spec that compiles cleanly via `meridian compile` into an interactive HTML design map. This guide is the **authoring** counterpart — it is concerned with *what* to put in the spec, not *how* the renderer draws it. The renderer is owned by [meridian-cli](../..).

The canonical, full-fidelity reference is [sample_spec.yaml](sample_spec.yaml) (Rapid Fire). When in doubt, copy its shape.

---

## File layout

One feature = one YAML file, named `<feature>.meridian.yaml`. Place it next to the design conversation transcript, typically `docs/design/<feature>.meridian.yaml`.

Top-level keys:

```yaml
meta:      # required
groups:    # optional
nodes:     # required (at least one)
edges:     # optional but normally heavily used
journeys:  # optional
```

`meridian validate <file>` enforces this and the rules below.

---

## `meta`

```yaml
meta:
  feature: "Rapid Fire"               # required, used in the artifact header
  intent: "One-line problem framing." # optional, surfaces in the header subline
  generated_at: "2026-05-12"          # optional
  version: "0.2"                      # optional
  title: "Rapid Fire · Design Map"    # optional, overrides the <title> tag
```

`feature` is the only required field. Keep it short — it's the page title.

---

## Layers

The artifact uses a **layer** taxonomy to colour nodes/groups and drive filter pills. The CLI ships with sensible defaults for these layer keys (you can use any subset; unknown keys fall back to a neutral grey):

| Layer key | Use it for |
|-----------|-----------|
| `route`   | HTTP endpoints / event handlers / lifespan hooks |
| `schema`  | API request/response Pydantic schemas |
| `service` | Service-class methods |
| `utility` | Pure helpers and domain calculators |
| `dao`     | Data-access methods |
| `types`   | Internal DTOs |
| `model`   | ORM models / DB schemas |

Pick at most 7 distinct layers. Too many and the filter pills become noise.

---

## `groups`

Groups are **compound containers** (file or class scoped). Use one whenever 2+ nodes share the same file or class — without a group, the children float free in the canvas.

```yaml
groups:
  - id: g_service          # snake_case; must be globally unique across groups + nodes
    label: "RapidFireService"
    sub_label: "class"      # rendered as a tiny secondary label, e.g. "class" / "routes"
    layer: service          # drives the dashed border colour
    parent: null            # groups can nest (e.g. file -> class), usually leave null
```

Rules of thumb:

- **One container per real-world boundary**, not per layer. A `service.py` file with one class becomes one group whose children are its methods.
- **Don't create groups for single-child files.** A standalone utility node sits at the top level — adding a group around it just clutters the canvas.
- **Don't mix layers inside one group** unless the file actually does (e.g. routes file with one schema class — keep them in one group, that's accurate).

---

## `nodes`

The unit of design capture. Each node is a function, method, schema, DTO, ORM model, or external dependency.

```yaml
nodes:
  - id: rf_service_play              # snake_case; globally unique
    label: "play()"                  # what shows in the canvas card
    kind: method                     # endpoint | function | method | schema | model | dto | dao | external | utility
    layer: service                   # drives card accent colour
    parent: g_service                # group id (omit for floating top-level nodes)

    file: "leap/games/rapid_fire/service.py"
    sig: "play(player_id: str) -> PlayResponse"

    behaviour:
      - "Opens session via self.ctx.session()"
      - "Calls game_session_dao.get_by_player_and_game(...)"
      - "Branch — None (new): create session, _pick_next_question([]), return active PlayResponse"
      # 4–10 bullets typical; ordered, notes-tone

    failures:
      - "NoQuestionsAvailableException(503) if pool empty"

    tests:
      - { type: acc,  label: "active + first question for first-time player" }
      - { type: edge, label: "503 when question cache empty at startup" }
      - { type: todo, label: "concurrent /play calls" }

    flag: "Concurrent submit race — UNIQUE(...) constraint would help."
    contract: |
      Optional free-form markdown block. Rendered in the side drawer below
      the structured sections. Use it for prose context that doesn't fit the
      bullets — usually you don't need this.

    tags: ["http", "critical-path"]   # free-form; reserved for future filtering
    depth: 1                          # reserved for future depth slider
```

### What goes where

- **`label`**: short and human-readable; this is the card's primary text. Include the parens for callables (`play()`), drop them for types (`PlayResponse`).
- **`kind`** vs **`layer`**: `kind` is *what it is* (endpoint, schema, …); `layer` is *what visual lane it lives in* (route, service, …). They're often the same word but conceptually different. `kind` is informational; `layer` drives colour.
- **`file`**: full repo-relative path. Don't include line numbers — they go stale.
- **`sig`**: a one-line signature for the drawer. Strip type imports; use simple Python notation.
- **`behaviour`**: *ordered* bullets describing what the function actually does. Detailed enough that a reviewer could write the implementation from this list alone, but written like notes — no prose padding.
- **`failures`**: every error this can raise/return, with the resulting status code or behaviour. `"N/A — pure data shape"` is a fine entry for DTOs.
- **`tests`**: the test plan, not actual test code. Three types:
  - **`acc`** — acceptance criterion: the behavior is fully decided and could be written as a test today. Use this for the primary happy paths and the must-have negative cases.
  - **`edge`** — edge/boundary case: the behavior is decided but it's a non-obvious boundary. Examples: off-by-one, nil/empty input, concurrent call, timeout boundary.
  - **`todo`** — obligation parking lot: we know a test is needed here but the *behavior itself* hasn't been nailed down yet. Use sparingly — if you can write the assertion, use `acc` or `edge` instead. `todo` is for genuine unknowns like "behaviour when DB is unavailable at startup" where the recovery strategy is still open. Do not use `todo` just because the test hasn't been written; that's what `acc` and `edge` are for.
- **`flag`**: when set, the node renders in amber and shows a "Flagged for review" callout. Use sparingly — flag is for genuine "needs a second look", not "I have a vague concern".
- **`contract`**: optional escape hatch. Prefer the structured fields.

### Naming ids

Use a stable prefix per layer/file so ids stay self-describing:

- `route_<verb>` for HTTP endpoints (`route_play`, `route_answer`)
- `schema_<name>` for API schemas (`schema_play_response`)
- `<service>_<method>` for service methods (`rf_service_play`, `rf_service_submit_answer`)
- `<dao>_<method>` for DAO methods (`game_session_dao_get`)
- `dto_<name>`, `orm_<name>` for types and ORM
- Free-form for utilities (`compute_rapid_fire_score`)

Ids are referenced by `parent`, edges, and journeys — keep them readable.

---

## `edges`

Flat list. Always populated. Every edge carries a descriptive label.

```yaml
edges:
  - { from: route_play,             to: rf_service_play,            label: "delegates" }
  - { from: rf_service_play,        to: game_session_dao_get,       label: "lookup" }
  - { from: rf_service_play,        to: pick_next_question,         label: "select question" }
  - { from: schema_play_response,   to: schema_question_schema,     label: "embeds" }
  - { from: dto_game_session,       to: orm_game_session,           label: "maps from" }
```

Rules:

- **Every edge has a label.** Empty labels make the diagram unreadable. Use action verbs (`delegates`, `calls`, `lookup`, `if new`, `if active`, `embeds`, `wraps`, `maps from`, `returns`, `set ABANDONED`, `load cache`).
- **Direction matters.** `from` is the caller / owner / wrapper; `to` is the callee / data / wrapped.
- **No self-loops** by default. If you need one, pass `--allow-self-loops` to the CLI (rare).
- **Endpoints must resolve** to a known node or group. Validation will reject dangling references.
- **You don't need to label every conditional branch** with a separate edge — one edge with an `"if new"` label is fine. But do split if both branches end at *different* targets.

### Optional `kind` and `id`

```yaml
- { from: rf_service_play, to: rf_answer_dao_get_all, label: "if completed", kind: calls }
```

`kind` is reserved for future colour-coding (calls / returns / reads / writes / raises / emits). `id` lets you give an edge a stable handle for journeys; usually unnecessary.

---

## `journeys`

Named, ordered flows through the call graph. They are how the artifact becomes *navigable* — without them it's just a static map.

```yaml
journeys:
  - id: first_play
    label: "First play (new game)"
    description: "Player clicks Play with no existing session."
    color: "#10b981"   # optional; auto-assigned if omitted
    steps:
      - { node: route_play,              note: "POST /play with JWT" }
      - { node: rf_service_play,         note: "Service.play(player_id)" }
      - { node: game_session_dao_get,    note: "returns None — no existing session" }
      - { node: game_session_dao_create, note: "insert new active session" }
      - { node: pick_next_question,      note: "random.choice from full cache" }
      - { node: schema_play_response,    note: 'status="active" + first question' }
```

Rules of thumb:

- **One journey per *user/system flow*.** "App startup", "First play", "Resume mid-game", "Submit (continue)", "Submit (final)", "Abandon" are six discrete journeys for one feature.
- **Steps are ordered** and traversed in sequence in the UI's bottom step-bar. The journey *highlights* edges that exist between consecutive steps — if your journey skips a node, the edge won't glow.
- **Notes are short**, written from the system's POV (`"returns None — no existing session"`), not narrative prose.
- **Keep journeys focused.** A 12-step journey usually means two journeys.
- **Don't try to journey the whole graph.** Static viewing covers that. Journeys are for the meaningful sequences.

---

## Validation checklist

Before handing the spec to `issue-planner`, run:

```bash
meridian validate docs/design/<feature>.meridian.yaml
```

The validator checks:

- All ids (groups + nodes) globally unique
- Every `parent` resolves to an existing group
- Every edge `from` / `to` resolves to a node or group
- Every journey step references a known node
- Journey ids unique
- No accidental self-loops

When it complains, **fix the spec** — don't suppress with flags. The errors usually surface real design gaps (a node mentioned in a journey but never defined, an edge to a forgotten DAO).

---

## Compile + iterate

```bash
meridian compile docs/design/<feature>.meridian.yaml \
  --out docs/design/<feature>-design-map.html
```

Open the HTML, walk it with the user, edit the YAML, recompile. The HTML is a build artifact — never hand-edit it.

`--watch` rebuilds on every save, useful while iterating.
`--open` opens the artifact in the default browser after compile.

---

## When to break the rules

This guide is opinionated because consistency makes the artifact pleasant. Break a rule when the design genuinely needs it — e.g. a node with 30 behaviour bullets is a sign the function should be split, but if it really is one cohesive block, leave it. Just don't break rules accidentally.
