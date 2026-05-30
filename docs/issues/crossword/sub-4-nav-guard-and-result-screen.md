# Sub-4: Navigation Guard and Polished Result Screen

**Type:** AFK
**Status:** todo
**Depends on:** Sub-1
**Blocks:** Sub-5 (e2e tests cover both the guard-submit path and the polished result)

## Parent

`docs/issues/crossword/parent.md`

## What to build

Wires the existing platform navigation guard to the Crossword session and replaces Sub-1's barebones result block with the PRD's full result screen. Crucially, this slice establishes the invariant that **for Crossword, leaving the page is functionally a deliberate submit** — there is no abandon endpoint and no `abandoned` status for Crossword sessions. Runs in parallel with Sub-2 and Sub-3.

End-to-end behaviour delivered:

1. **Navigation guard wiring** — on entering the Crossword route while a session is `active`, the existing platform navigation guard arms (`setIsDirty(true)`). On confirmed exit (back button, route change, tab close attempt) the guard handler calls `POST /games/crossword/submit`, awaits the response, then disarms (`setIsDirty(false)`) and allows the navigation to proceed. On a `completed` session the guard does not arm. There is no "Are you sure?" confirm modal — the action is a clean submit (the player already has the visible Submit button as the explicit exit; the guard handles accidental exits identically).
2. **No abandon endpoint** — `POST /games/crossword/abandon` is **not** added. `game_sessions.status` for Crossword only ever transitions `active → completed`. The Lobby tile reflects this: there is no `abandoned` state for Crossword.
3. **Polished `ResultView` component** — replaces the inline minimal result block from Sub-1. Layout:
   - Big total score at the top.
   - Breakdown line: `base_score (= solved_count × 100) + time_bonus = total`.
   - `solved_count / total_entries` and `time_elapsed_ms` formatted `mm:ss`.
   - A list of solved entries: each row shows the clue and the answer word (and its number/direction, e.g. "7 Across — ATOMICITY"). Unsolved entries are deliberately omitted (no "missed" section).
   - "Back to Lobby" button that routes to `/lobby`.
4. **Re-entry from lobby tile on `completed` session** — clicking the Crossword tile when the session is `completed` calls `play`, receives `puzzle: null` + `result` populated, and renders `ResultView` directly (no detour through gameplay; the grid is not shown).
5. **Result-screen confidentiality** — verified by a frontend test: when rendering `ResultView` from a `result` payload containing only solved entries, no DOM element ever displays the answer text of an unsolved entry (because it is never present in the payload).
6. **Submit button de-dupe** — the submit button uses the same `/submit` call as the guard; after the response the UI transitions to `ResultView` without a hard reload; a second click while the request is in-flight is a no-op.

This slice does NOT touch backend `submit` logic (Sub-1 already returns the final result), the time-bonus computation (Sub-3 adds the relevant fields), or the keyboard UX polish (Sub-2). It consumes the `base_score` / `time_bonus` / `time_elapsed_ms` fields that Sub-3 adds — if Sub-3 lands first the result screen shows real numbers; if it lands after, the result screen falls back gracefully to showing just `score`.

## Technical nuances (must get right)

- **Leaving = submit, not abandon.** There is intentionally no abandon endpoint and no `abandoned` status. A guard exit and the Submit button hit the exact same `/submit` and produce identical results — assert this equivalence.
- **Guard arms only when `active`.** Re-entering a `completed` session must NOT arm the guard (otherwise navigating away from the result screen would fire a redundant `/submit` on an already-completed session, which the backend rejects).
- **Confidentiality is structural, not cosmetic.** Unsolved answers are never in the payload to begin with; the render test proves the UI can't leak what it never received.
- **In-flight submit de-dupe** — a double-click (or a guard exit racing the button) must not fire two `/submit` calls.
- **Completed re-entry shows result directly** — `play` on a completed session returns `puzzle: null`; the shell must branch to `ResultView` without mounting the grid.

## Acceptance criteria

- [ ] Entering the Crossword route with an `active` session arms the guard; entering with a `completed` session does not
- [ ] Confirmed back-navigation while `active` calls `POST /games/crossword/submit`, waits for the response, then completes navigation; the player lands on the Lobby with the tile reflecting `completed`
- [ ] No `POST /games/crossword/abandon` route exists; no `CrosswordService.abandon` method exists; `game_sessions.status` for Crossword never becomes `abandoned`
- [ ] `ResultView` renders total score, the `base + time_bonus = total` breakdown (or just `score` if Sub-3 has not landed), `solved_count / total_entries`, `time_elapsed_ms` as `mm:ss`, the solved-entries list (number/direction + clue + answer), and a "Back to Lobby" button
- [ ] Unsolved entries never appear on the result screen (verified by a render test against a payload with `solved_count < total_entries`)
- [ ] Re-entering the Crossword route after completion shows `ResultView` directly with no detour through gameplay
- [ ] Double-clicking submit (or a guard exit racing the button) while a `/submit` is in flight does not fire a second request
- [ ] Existing Sub-1 happy-path behaviour still works end-to-end

## Blocked by

Sub-1 (the `/submit` endpoint, the session lifecycle, and the route shell must exist).
