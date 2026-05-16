# Sub-7: Rapid Fire — abandon + navigation guard wiring + timer expiry

**Status:** Done  
**Blocks:** None

## Parent

`docs/issues/frontend/parent.md`

## What to build

The two remaining Rapid Fire edge cases: a player navigating away mid-game (abandon) and a question timer reaching zero (auto-skip). Both are defensive paths that must work correctly alongside the core loop from Sub-6.

**Timer expiry (auto-skip)**  
When the per-question countdown reaches zero, the client dispatches `TIMER_EXPIRE`. A side-effect hook watching this dispatches `SELECT_OPTION` with `selected_option: null`, which transitions to `submitting` and calls `POST /answer` with `{ question_id, selected_option: null, time_ms: time_limit_ms }`. The server treats `null` as a skip. The feedback phase shows the correct option with no highlighted selection.

**Abandon via navigation guard**  
The `GameNavigationGuardDialog` (already implemented in the `(games)` layout) intercepts back navigation and `beforeunload` when `isDirty` is true. When the player confirms "leave", the dialog must call `POST /api/games/rapid-fire/abandon` before releasing the navigation lock.

This requires wiring the abandon API call into the dialog's confirm handler. The `GameNavigationGuardDialog` currently calls a generic `onConfirm` callback — pass the abandon mutation as `onConfirm` from `RapidFireClient`. On a successful abandon response, call `setIsDirty(false)` and let the navigation proceed. Show the partial score from the `AbandonResponse` if possible (or navigate immediately — pick the simpler path).

**Service layer addition**  
- `src/lib/api/rapid_fire.ts` — add typed fetch wrapper for `POST /abandon`
- `src/services/rapid_fire/schema.ts` — add `AbandonResponse` Zod schema
- `src/services/rapid_fire/hooks.ts` — add `useAbandon` mutation

## Acceptance criteria

- [x] When the question timer reaches zero, the answer is auto-submitted with `selected_option: null`
- [x] Auto-skip feedback shows the correct option; no option is highlighted as "selected"
- [x] Timer expiry is ignored during `submitting` and `feedback` states (no double-fire)
- [x] Trying to navigate away mid-game (browser back) shows `GameNavigationGuardDialog`
- [x] Confirming the dialog calls `POST /abandon` before navigation proceeds
- [x] After confirmed abandon, `setIsDirty(false)` is called and the player is routed to `/lobby`
- [x] Cancelling the dialog dismisses it and returns the player to the active question
- [x] `AbandonResponse` Zod schema parses `{ result: { score, correct_count, wrong_count, skipped_count, time_taken_seconds } }`
- [x] Reducer test: `TIMER_EXPIRE` action in `question` state triggers `SELECT_OPTION` with `null`
- [x] Reducer test: `TIMER_EXPIRE` in `submitting` state is a no-op
- [x] API test (msw): `POST /abandon` returns `AbandonResponse` and is called exactly once on confirm
