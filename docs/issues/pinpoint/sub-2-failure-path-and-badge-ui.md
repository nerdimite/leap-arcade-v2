# Sub-2: Failure Path + 5-Card Badge UI

**Type:** AFK
**Status:** ready-for-agent
**Depends on:** Sub-1
**Blocks:** Sub-5

## Parent

`docs/issues/pinpoint/parent.md`

## What to build

Polish the in-game UX to match the LinkedIn Pinpoint feel and round out the failure-path UX. Sub-1 already implements the server-side `failed` state and zero scoring — this slice is focused on what the player sees.

End-to-end behaviour delivered:

1. **Clue badge row component** — five horizontal badge cards rendered for every puzzle. All five slots are always visible. Initial render: clue 1 revealed (text shown), clues 2–5 in a "locked" empty state (greyed/blurred). On each wrong guess, the next badge slides+fades into the revealed state from left to right, mirroring LinkedIn Pinpoint. Driven entirely by `puzzle.clues_revealed` and `puzzle.clues` from the server response — no client-only state.
2. **Wrong-guess feedback** — on `correct: false`, the just-unlocked badge gets a brief shake animation and a red flash; the input clears; focus stays on the input. No toast, no error banner — the badge animation is the feedback.
3. **Result-flash overlay** — on `puzzle.status` transitioning to `solved`, a 2s green overlay appears centred over the play area showing "Correct! +<base>" (the time-bonus breakdown is added in Sub-3). On transition to `failed`, a 2s red overlay shows "Out of clues — +0". The canonical answer is **never** displayed in either state. After the 2s flash, the client auto-calls `play` to advance to the next puzzle (or the result screen if the session is complete).
4. **Frontend state machine** — handle three local UI phases per puzzle: `playing` (input enabled), `flashing` (input disabled, overlay visible), `advancing` (between `play` calls). Keep this logic colocated with the Pinpoint route so it can be tested in isolation.
5. **Component-level tests** — the badge row renders the correct number of revealed vs locked slots given a `PuzzleState`; the result overlay renders the right copy for `solved` vs `failed`; the canonical answer is provably never rendered (assert on the component tree given a state with `status: failed`).

This slice does not change any backend contract — `puzzle.status: failed` already exists from Sub-1.

## Acceptance criteria

- [ ] Five badge slots are always visible; revealed slots show the clue text, locked slots show a placeholder/locked treatment
- [ ] On a wrong guess, the next badge transitions from locked to revealed via a slide+fade animation; the input clears; focus stays on the input
- [ ] On a wrong guess, the just-unlocked badge briefly shakes and flashes red
- [ ] On `solved`, a 2s green overlay shows "Correct! +<base>" (no answer text) and then the client advances by calling `play`
- [ ] On `failed`, a 2s red overlay shows "Out of clues — +0" (no answer text) and then the client advances by calling `play`
- [ ] During the 2s flash window, the input is disabled and clicking "Guess" is a no-op
- [ ] No code path in the frontend renders `answer` or `answer_aliases` from any response — verified by component tests
- [ ] Reducer / hook tests covering the three UI phases (`playing` / `flashing` / `advancing`) pass; tests follow the prior-art pattern in `frontend/src/__tests__/` for Rapid Fire

## Blocked by

Sub-1 — the API contract, the route shell, and the basic guess loop must exist before this UX layer can be built.
