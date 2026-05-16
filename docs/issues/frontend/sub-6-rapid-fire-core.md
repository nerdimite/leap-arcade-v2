# Sub-6: Rapid Fire — core play loop

**Status:** Done  
**Blocked by:** Sub-2 (Frontend infra), Sub-3 (Login auth flow)  
**Blocks:** Sub-7 (Abandon + navigation guard)

## Parent

`docs/issues/frontend/parent.md`

## What to build

The complete Rapid Fire happy path: start a session, answer all 15 questions, see the result screen. Covers the service layer, the game reducer, and the game UI. Abandon and timer-expiry are handled in Sub-7.

**Service layer**  
- `src/lib/api/rapid_fire.ts` — typed fetch wrappers for `POST /play`, `POST /answer`
- `src/services/rapid_fire/schema.ts` — Zod schemas for `PlayResponse`, `QuestionSchema`, `AnswerRequest`, `AnswerResponse`, `ResultSchema` (see backend API shapes in `rapid-fire.meridian.yaml`)
- `src/services/rapid_fire/hooks.ts` — `usePlay`, `useSubmitAnswer` (React Query mutations)

**Game reducer (`app/(games)/rapid-fire/_hooks/useRapidFireReducer.ts`)**  
Pure `useReducer`-based state machine. All state lives here; no logic in the component. State shape and transitions (from the grill session):

```
States:
  idle        — before /play is called
  loading     — /play in flight
  question    — question displayed, timer running
  submitting  — /answer in flight, options locked
  feedback    — showing correct/wrong for FEEDBACK_DURATION_MS
  result      — game complete, result card displayed
  error       — unrecoverable error

Actions:
  START               — idle → loading
  PLAY_SUCCESS        — loading → question (with first question + session data)
  PLAY_ERROR          — loading → error
  SELECT_OPTION       — question → submitting (fires useSubmitAnswer mutation)
  ANSWER_SUCCESS      — submitting → feedback (stores correct/wrong + next_question)
  ANSWER_ERROR        — submitting → error
  FEEDBACK_COMPLETE   — feedback → question (if next_question exists) | result (if null)
  RESULT_SHOWN        — result (no-op; disarms dirty flag)
```

`time_ms` for each answer is measured by the component (via `Date.now()` at question display vs submission). The reducer does not own timers — timing side-effects are managed by hooks watching derived state.

**Rapid Fire page**  
- `app/(games)/rapid-fire/page.tsx` — server component; calls `POST /play` to rehydrate an existing session or start a new one; wraps result in `HydrationBoundary`
- `app/(games)/rapid-fire/_components/RapidFireClient.tsx` — client component; uses `useRapidFireReducer`; renders the current state

**In-game UI elements (all client components):**
- Question card: question text + 4 option buttons
- Options lock immediately on selection (during `submitting` state)
- Feedback overlay: highlights correct option green, selected wrong option red; shows `current_score`
- Countdown timer: per-question bar draining from `time_limit_ms`, starts after `QUESTION_START_DELAY_MS`
- Progress indicator: "Question N of 15"
- Running score display
- Result card (in `result` state): score, correct/wrong/skipped counts, time taken, "Back to Lobby" button

`setIsDirty(true)` is called on `PLAY_SUCCESS`; `setIsDirty(false)` is called on `RESULT_SHOWN`.

## Acceptance criteria

- [x] Player can start Rapid Fire and see the first question with all four options
- [x] Selecting an option immediately locks all buttons and submits the answer
- [x] Correct answer shows green feedback; wrong answer shows green (correct) + red (selected)
- [x] Running score updates after each feedback phase
- [x] Game auto-advances to the next question after `FEEDBACK_DURATION_MS`
- [x] Next question timer starts after `QUESTION_START_DELAY_MS` get-ready pause
- [x] After the 15th question, the result card is shown inline with score breakdown
- [x] "Back to Lobby" button on result card navigates to `/lobby`
- [x] Page refresh mid-game resumes on the next unanswered question (server rehydration)
- [x] Timer resets to full `time_limit_ms` on resume after refresh (ADR-0003)
- [x] Reducer test: `idle → loading → question` on `START` + `PLAY_SUCCESS`
- [x] Reducer test: `question → submitting → feedback → question` on happy-path answer cycle
- [x] Reducer test: `feedback → result` when `next_question` is `null` after `FEEDBACK_COMPLETE`
- [x] Reducer test: `submitting` state — `SELECT_OPTION` action is ignored (no double-submit)
- [x] Zod: `PlayResponse` active branch parses `{ status, game_session_id, question, questions_answered, questions_total }`
- [x] Zod: `AnswerResponse` parses `{ correct, correct_option, current_score, next_question: null, result }`
- [x] API test (msw): `POST /play` sends correct headers and returns parsed `PlayResponse`
- [x] API test (msw): `POST /answer` sends `{ question_id, selected_option, time_ms }` and returns `AnswerResponse`
