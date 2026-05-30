# Sub-2: Crossword Keyboard UX Polish

**Type:** AFK
**Status:** done
**Depends on:** Sub-1
**Blocks:** Sub-5 (e2e tests assume polished UX is present)

## Parent

`docs/issues/crossword/parent.md`

## What to build

Frontend-only slice that takes the barebones grid/clue UI from Sub-1 and brings it up to the PRD's "full standard crossword" UX bar. Backend is unchanged — this slice consumes the same `play` / `check` contract.

End-to-end behaviour delivered:

1. **Cursor + type-and-advance** — clicking an open cell selects it and sets a cursor. Typing a letter fills the selected cell and auto-advances the cursor to the next open cell along the **active direction** (skipping nothing — the next cell in the entry; at the end of an entry the cursor stops). Letters are uppercased on entry.
2. **Direction toggle** — clicking the already-selected cell, or pressing Tab/Space, toggles the active direction (across ↔ down) **only when the cell belongs to both** an Across and a Down entry. On a cell that belongs to only one entry, the direction is forced to that entry.
3. **Arrow-key navigation** — `←→↑↓` move the cursor to the nearest open cell in that direction (blocked cells are skipped/blocked). Horizontal arrows imply across context, vertical arrows imply down context for the active-entry highlight.
4. **Backspace semantics** — Backspace clears the current cell's letter if non-empty; if the current cell is already empty, it retreats to the previous open cell along the active direction and clears that. Locked (solved) cells are never cleared by Backspace — the cursor retreats past them.
5. **Active-entry highlight** — selecting a cell highlights every cell of its active entry in the grid and highlights the matching clue in the Across/Down panel. Clicking a clue jumps the cursor to that entry's first open (non-locked) cell and sets the direction. The highlight is derived purely from cursor + direction, not from server state.
6. **Auto-check trigger (shared-cell aware)** — a `/check` fires the moment the active entry's cells are all non-empty. **Critically:** when a single keystroke fills a shared cell that completes BOTH the across and the down entry through it, the client must fire one `/check` per completed entry (up to two). De-dupe in-flight checks per `entry_id` (a second check for the same entry while one is pending is suppressed).
7. **Hit feedback** — on `correct=true`, the entry's cells lock into a persistent green highlight and become read-only; the corresponding clue is marked solved with `✓` and de-emphasised; a `+100` chip animates near the score. Solved cells loaded from `play` on refresh come back locked green.
8. **Wrong-entry feedback (keep letters)** — on `correct=false` for a fully-filled entry, the entry's cells flash red briefly (~250 ms) but the typed letters are **kept** (NOT cleared). Locked-correct letters borrowed from solved crossing entries are never touched by the flash or any edit. The entry re-checks automatically the next time it becomes fully filled after the player edits a cell.
9. **Locked-cell read-only** — cells belonging to a solved entry are read-only: typing into them is a no-op (cursor advances past), and they render green even when they sit inside an as-yet-unsolved crossing entry.
10. **Storybook coverage** — `CrosswordGrid` and `ClueListPanel` get Storybook entries: empty, in-progress with some solves, all-solved, mid-entry with active highlight, and a wrong-flash state.
11. **Reducer / hook tests** — the cursor/selection/direction state machine is unit-tested via a pure reducer: cell select, type-and-advance, direction toggle (only on shared cells), arrow nav, Backspace clear/retreat, entry-completion detection (which entries became full from a given fill), hit vs miss handling.

This slice does NOT touch backend code, scoring, the stopwatch, the navigation guard, or the result-screen polish — those are Sub-3 and Sub-4.

## Technical nuances (must get right)

- **Keep letters on wrong** — the single biggest divergence from Word Hunt's clear-on-miss. A wrong entry must NEVER wipe the player's letters, and must never disturb green locked crossing letters. The player fixes one cell and the entry re-checks.
- **Shared-cell double-check** — one keystroke can complete two entries. Both must be checked; both can score. Detect "which entries just became full" from the edited cell's across+down membership, not just the active entry.
- **In-flight check de-dupe** — without per-`entry_id` de-dupe, a fast typist (or the shared-cell case) can fire duplicate `/check` calls; the server is idempotent (duplicate-solve is a no-op) but the client must not double-count the `+100` chip.
- **Direction toggle only on intersections** — toggling on a single-membership cell is meaningless; force the cell's only direction.
- **Locked cells are read-only and green even inside unsolved entries** — a solved CACHING down-entry pre-fills one cell of an unsolved across entry; that cell stays green and uneditable while the rest of the across entry is still blank.
- **Highlight is client-derived** — never round-trip to the server to compute the active-entry highlight; it's pure cursor + direction + the static skeleton.

## Acceptance criteria

- [ ] Typing fills the selected cell and advances the cursor along the active direction; letters are uppercased
- [ ] Clicking the selected cell / Tab / Space toggles across↔down only on cells that belong to both directions; single-membership cells force their direction
- [ ] Arrow keys move the cursor to the nearest open cell, skipping blocked cells
- [ ] Backspace clears the current cell, or retreats-and-clears the previous open cell when current is empty; never clears a locked cell
- [ ] Selecting a cell highlights its active entry in the grid and the matching clue; clicking a clue jumps to its first open non-locked cell and sets direction
- [ ] A `/check` fires when the active entry is fully filled; a shared-cell fill that completes both entries fires one check per entry; in-flight checks are de-duped per `entry_id`
- [ ] On `correct=true`: cells lock green + read-only, clue gets `✓` and de-emphasis, a single `+100` chip animates; solved state survives refresh via `play`
- [ ] On `correct=false`: cells flash red ~250 ms, typed letters are KEPT, locked crossing letters untouched, and the entry re-checks after the next edit completes it
- [ ] Cells of a solved entry are read-only and render green even inside an unsolved crossing entry
- [ ] Storybook entries render for `CrosswordGrid` (empty / in-progress / all-solved / mid-entry-highlight / wrong-flash) and `ClueListPanel` (all-unsolved / partial / all-solved)
- [ ] Reducer / hook tests for the cursor/direction/entry-completion state machine pass
- [ ] Existing Sub-1 happy-path behaviour still works (full playthrough, refresh-resume, submit)

## Blocked by

Sub-1 (the grid component, clue panel, and `/check` wiring must exist).
