# Sub-4: Navigation Guard and Polished Result Screen

**Type:** AFK
**Status:** ready-for-agent
**Depends on:** Sub-1
**Blocks:** Sub-5 (e2e tests cover both the guard-submit path and the polished result)

## Parent

`docs/issues/word-hunt/parent.md`

## What to build

Wires the existing platform navigation guard to the Word Hunt session and replaces Sub-1's barebones result block with the PRD's full result screen. Crucially, this slice establishes the platform invariant that **for Word Hunt, leaving the page is functionally a deliberate submit** — there is no abandon endpoint and no `abandoned` status for Word Hunt sessions. Runs in parallel with Sub-2 and Sub-3.

End-to-end behaviour delivered:

1. **Navigation guard wiring** — on entering the Word Hunt route while a session is `active`, the existing platform navigation guard arms (`setIsDirty(true)`). On confirmed exit (back button, route change, tab close attempt) the guard handler calls `POST /games/word-hunt/submit`, awaits the response, then disarms (`setIsDirty(false)`) and allows the navigation to proceed. On `completed` the guard does not arm. There is no confirm modal asking "Are you sure?" — the action is a clean submit (the player has already received the visible "Submit" button as the explicit exit; the guard handles accidental exits identically).
2. **No abandon endpoint** — `POST /games/word-hunt/abandon` is **not** added. The `game_sessions.status` for Word Hunt only ever transitions `active → completed`. The Lobby tile reflects this: there is no `abandoned` state for Word Hunt.
3. **Polished `ResultView` component** — replaces the inline minimal result block from Sub-1. Layout:
   - Big total score at the top.
   - Breakdown line: `base_score (= found_count × 100) + time_bonus = total`.
   - `found_count / total_words` and `time_elapsed_ms` formatted as `mm:ss`.
   - A list of the found words: each row shows the clue and the answer word. Unfound words are deliberately omitted (no "missed" section).
   - "Back to Lobby" button that routes back to `/lobby`.
4. **Re-entry from lobby tile on `completed` session** — clicking the Word Hunt tile when the session is `completed` calls `play`, receives `puzzle: null` + `result` populated, and renders the polished `ResultView` directly (no detour through gameplay). The grid is not shown.
5. **Result-screen confidentiality** — verified by a frontend test: when rendering `ResultView` from a `result` payload that contains only found words, no DOM element ever displays the text of an unfound Hidden Word (because it is never present in the payload to begin with).
6. **Submit button on the game screen** — wired in Sub-1, but this slice ensures: the submit button uses the same `/submit` call as the navigation guard; after the response, the UI transitions to `ResultView` without a hard reload; double-clicks are de-duped (a second click while the request is in-flight is a no-op).

This slice does NOT touch backend `submit` logic (Sub-1 already returns the final result), the time-bonus computation (Sub-3 adds the relevant fields), or the drag UX polish (Sub-2). It does consume the `base_score` / `time_bonus` / `time_elapsed_ms` fields that Sub-3 adds — if Sub-3 lands first the result screen will display real numbers, if it lands after the result screen will fall back gracefully to showing just `score` (the merge order is small).

## Acceptance criteria

- [ ] On entering the Word Hunt route with an `active` session, the navigation guard arms; on entering with a `completed` session, it does not
- [ ] Confirmed back-navigation while `active` calls `POST /games/word-hunt/submit`, waits for the response, then completes the navigation; the player lands on the Lobby with the tile reflecting `completed`
- [ ] No `POST /games/word-hunt/abandon` route exists; no `WordHuntService.abandon` method exists; `game_sessions.status` for Word Hunt never becomes `abandoned`
- [ ] Polished `ResultView` renders total score, the `base + time_bonus = total` breakdown (or just `score` if Sub-3 has not landed), `found_count / total_words`, `time_elapsed_ms` formatted `mm:ss`, the found-words list (clue + word), and a "Back to Lobby" button
- [ ] Unfound Hidden Words never appear on the result screen (verified by a render test against a payload with `found_count < total_words`)
- [ ] Re-entering the Word Hunt route after completion shows the `ResultView` directly with no detour through gameplay
- [ ] Double-clicking the submit button while a `/submit` request is in flight does not fire a second request
- [ ] Existing Sub-1 happy-path behaviour still works end-to-end

## Blocked by

Sub-1 (the `/submit` endpoint, the session lifecycle, and the route shell must exist).
