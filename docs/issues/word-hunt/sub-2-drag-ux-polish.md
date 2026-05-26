# Sub-2: Drag UX Polish

**Type:** AFK
**Status:** done
**Depends on:** Sub-1
**Blocks:** Sub-5 (e2e tests assume polished UX is present)

## Parent

`docs/issues/word-hunt/parent.md`

## What to build

Frontend-only slice that takes the barebones drag/clue/grid UI from Sub-1 and brings it up to the PRD's UX bar. Backend is unchanged.

End-to-end behaviour delivered:

1. **Drag-direction snapping in `LetterGrid`** — pointer-down begins a trace from a cell; pointer-move snaps the selection to the nearest valid straight line from the start cell (one of: horizontal, vertical, both diagonals). Off-axis movement projects onto the nearest of the 8 allowed axes. Pointer-up commits the trace. The user can never select an L-shape or an off-axis path — the visual selection always reflects exactly what the server would accept.
2. **Persistent found-cell highlight** — every cell that is part of a found word gets a persistent highlight (distinct background colour). Finds from previous sessions of the same puzzle (loaded from `play` response on refresh) come back with the same highlight applied.
3. **Miss flash** — when `/find` returns `matched=false`, the cells that were just selected flash red briefly (~250 ms) then clear. No score change, no toast, no modal — just the flash.
4. **Hit feedback** — on a successful find, the just-traced cells lock into the persistent found-highlight colour with a brief "land" animation, and a `+100` score chip animates near the score display.
5. **Clue card flip-on-found** — `ClueListPanel` cards show the riddle text only while unfound. On a successful find, the corresponding card flips (CSS 3D transform or equivalent) to reveal `word ✓` and visually de-emphasises (struck or faded). The flip is driven purely by the `clues[*].found` flag in the latest `play` / `find` response — no client-only state.
6. **Storybook coverage** — `LetterGrid` and `ClueListPanel` get Storybook entries that exercise: empty state, in-progress with some finds, all-found state, mid-drag preview (for `LetterGrid`).
7. **Reducer / hook tests** — direction-snapping logic is unit-tested via a pure reducer or pure helper: pointer paths that wander off-axis snap to the nearest of the 8 lines from the drag origin; length-1 commits are rejected; commits with valid coordinates surface to the parent.

This slice does NOT touch backend code, scoring, the stopwatch, the navigation guard, or the result-screen polish — those are Sub-3 and Sub-4.

## Acceptance criteria

- [ ] Pointer-driven drag in `LetterGrid` constrains the visual selection to one of 8 cardinal/diagonal lines from the drag origin at all times during the drag
- [ ] Pointer paths that wander off-axis snap to the nearest of the 8 allowed lines (e.g. a path that drifts 1 cell off horizontal still selects the pure horizontal line until it drifts closer to a diagonal)
- [ ] Single-cell taps (no drag) do not fire a `/find` call
- [ ] On a successful find, the traced cells lock into a persistent highlight that survives page refresh (via `play` response)
- [ ] On a miss, the selected cells flash red briefly (~250 ms) then clear; no other state changes
- [ ] On a successful find, a `+100` increment animates near the score; no `+100` is shown on a miss
- [ ] `ClueListPanel` cards show clue-only text while `found=false`; flip to `word + ✓` when `found=true`; flipped cards are visually de-emphasised
- [ ] Grid remains visually neutral — no highlights on hover, no highlight when a clue card is clicked, no hints about word locations
- [ ] Storybook entries render for `LetterGrid` (empty / in-progress / all-found / mid-drag) and `ClueListPanel` (all-unfound / partial / all-found)
- [ ] Reducer / hook tests for direction snapping pass
- [ ] Existing Sub-1 happy-path behaviour still works (full playthrough, refresh-resume, submit)

## Blocked by

Sub-1 (the grid component, clue panel, and `/find` wiring must exist).
