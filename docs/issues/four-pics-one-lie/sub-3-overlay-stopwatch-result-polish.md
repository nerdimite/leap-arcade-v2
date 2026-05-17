# Sub-3: Answer Overlay + Stopwatch + Result Polish

**Type:** AFK
**Status:** ready-for-agent
**Depends on:** Sub-1
**Blocks:** nothing

## Parent

`docs/issues/four-pics-one-lie/parent.md`

## What to build

Replace the minimal correct/wrong feedback shipped in Sub-1 with the polished UX described in the PRD: a 2-second result overlay with score breakdown, a live per-question stopwatch driven by server time, and a full per-question result screen. Pure frontend work — no backend, no schema, no API contract changes.

End-to-end behaviour delivered:

1. **AnswerOverlay component** — appears immediately when `POST /answer` resolves; auto-dismisses after 2 seconds, then advances the UI to the next question (or to the result view if `result` was returned).
   - **Correct:** green overlay showing `+{base} base + {time_bonus} bonus = {score} pts`. Optional subtle highlight on the tapped image (no highlight on any other tile).
   - **Wrong:** red overlay showing `+0 pts`. The correct image is **not** indicated in any way — no border, no highlight, no animation — so the answer remains hidden from the player and from anyone watching their screen.
2. **Stopwatch component** — initialised from `question_started_at` returned by `POST /play` / `POST /answer`. Renders mm:ss live, updating every animation frame (or 100 ms tick). Visual decay cue (e.g. colour shift from neutral → warm → red) as elapsed approaches `FOUR_PICS_TIME_DECAY_MS = 30 000 ms` to communicate the bonus burn. After 30 s the cue settles into a "no bonus available" state but the stopwatch keeps running. Refreshing the page resumes the stopwatch from the server-provided start time — the client computes `elapsed = now − question_started_at` on mount.
3. **Result view polish** — replace the minimal "score + back" block from Sub-1 with a full per-question table:
   - Total score header
   - Counts: `questions_correct`, `questions_wrong`, `questions_not_reached` (will only be nonzero once Sub-2 ships)
   - Per-question rows showing question number, status badge (correct / wrong / not_reached), score earned, time bonus
   - **No images shown on the result screen** — the per-question identity is by number only, so the player cannot retroactively learn which image was the lie
   - "Back to Lobby" button
4. **Input lock during overlay** — once the player taps an image, all four tiles become non-interactive until the overlay dismisses. Subsequent taps during the 2-second window are no-ops. This prevents double-submission and accidental advance.
5. **Storybook coverage** — stories for `AnswerOverlay` (correct + wrong variants), `Stopwatch` (fresh / mid-game / past-decay states), and `ResultView` (mixed correct/wrong/not_reached fixture), following the existing dumb-smart-storybook patterns used by Rapid Fire / Wiki components.

## Acceptance criteria

- [ ] On a correct tap, a green overlay appears within ~50 ms and auto-dismisses after 2 s, displaying `+100 base + N bonus = X pts` with the actual returned values
- [ ] On a wrong tap, a red overlay appears within ~50 ms and auto-dismisses after 2 s, displaying `+0 pts`; no visual indication of which image was the correct answer
- [ ] After the overlay dismisses, the UI advances to the next question (using the `question` from the same `POST /answer` response — no extra round-trip) or to the result view (when `result` is populated)
- [ ] Image tiles are non-interactive during the overlay window; rapid-fire double taps do not trigger a second submission
- [ ] The stopwatch displays mm:ss, ticks live, and is initialised from `question_started_at`; refreshing the page resumes from the server time, not from zero
- [ ] The stopwatch has a visible decay cue that intensifies as the player approaches the 30 s bonus floor and settles into a stable "no bonus" state past 30 s
- [ ] The result view shows the total score, status counts, and a per-question table; no images appear on the result screen
- [ ] "Back to Lobby" button on the result view returns the player to the Lobby; lobby tile shows `completed` (or `abandoned` once Sub-2 ships)
- [ ] Storybook stories exist for `AnswerOverlay` (correct + wrong), `Stopwatch` (multiple states), and `ResultView` (mixed-status fixture) and render without runtime errors

## Blocked by

Sub-1 — the game shell, API client wrappers, and basic question/answer flow must exist before the polish layer can attach.
