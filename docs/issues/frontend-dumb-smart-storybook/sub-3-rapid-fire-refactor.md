# Sub-3: Rapid Fire refactor — reference slice for the pattern

**Status:** done  
**Blocked by:** Sub-1 (Storybook), Sub-2 (`TimerBar`)  
**Blocks:** Sub-4 (Wiki — applies this pattern to a more complex client)

## Parent

`docs/issues/frontend-dumb-smart-storybook/parent.md`

## ⚠️ Reference-slice instructions

**This slice establishes the in-code conventions that every subsequent refactor slice (Sub-4, Sub-5, Sub-6, Sub-7) must mirror.** Be deliberate about file naming, file header style, comment style, story file shape, callback prop naming, helper-extraction approach, and how `viewState` is computed. Subsequent slices will be reviewed against the files produced here. If a convention isn't already locked down in ADR-0005 or the PRD, pick something reasonable and document the choice briefly in the PR description so later slices can mirror it.

## Conventions established (mirror in Sub-4..Sub-7)

- **File headers:** one-line `/** … */` purpose comment at top of new modules (no banner blocks).
- **Pure view-state module:** kebab-case `rapid-fire-view-state.ts` exports `RapidFireViewState` + `toRapidFireViewState`; tests as sibling `rapid-fire-view-state.test.ts`.
- **Reducer input type:** `RapidFireState` from `useRapidFireReducer.ts` (not the name `RapidFireReducerState` from the sketch).
- **`loading` view variant:** includes `currentScore`, `questionsAnswered`, `questionsTotal` so the dumb header matches reducer state during `loading` / `idle` (ADR snippet showed only `status`; extended here for parity).
- **`RapidFireView` props:** `viewState`, `onSelectOption`, `onBackToLobby`, plus **`questionEnteredAtRef`** — shared `MutableRefObject<number>` from the smart layer so answer `timeMs` matches the same anchor as the 50ms timer (single source of truth).
- **Timer bar parity:** render shared `TimerBar` in `!viewState.locked` question states only (matches previous `state.status === "question"` gate so `submitting` stays with no visible bar).
- **Storybook CSF:** `satisfies Meta<typeof Component>`; omit `title` in meta; `import type { Meta, StoryObj } from "@storybook/nextjs-vite"`; **`fn` from `storybook/test`** (Storybook 10 ships this entry; use `@storybook/test` only if the project adds it as a direct dep). Alias schema imports in stories when export names collide (`Question as RapidFireQuestion`, etc.). Avoid exporting a story named `Error` (Biome `noShadowRestrictedNames`): use **`ErrorStory`** (optional `name: "Error"` if your Storybook types allow it for sidebar label).
- **Leaf `Default` story:** re-export primary variant (e.g. `export { Question as Default }`, `export { Correct as Default }`).

## What to build

Refactor `RapidFireClient` from a 289-line monolith into a thin smart wiring layer that produces a `viewState` and hands it to a dumb assembled `RapidFireView`, which switches on status and renders leaf components. Behaviour for players is unchanged.

### Smart layer (`RapidFireClient.tsx`)

Retain all hooks, mutations, effects, refs, and the navigation-guard wiring it currently owns:
- `useRapidFireReducer` (untouched)
- `useNavigationGuard`, `useSubmitAnswer`, `useAbandon`
- The 50ms `setInterval` for the per-question timer
- All `useEffect` blocks (timer, mutation dispatch, dirty-flag wiring, result-shown, feedback-complete, abandon registration)
- `questionEnteredAtRef`, `resultDirtyClearedRef`, `timerPulse` local state

The client now does two new things:
1. Pre-computes `timerBarPct` from the interval tick (already in code, just retained).
2. Computes `viewState = toRapidFireViewState(state, timerBarPct)` and renders `<RapidFireView viewState={viewState} onSelectOption={...} onBackToLobby={...} />`.

The client owns zero JSX beyond the single `<RapidFireView ... />` element (and any provider wrapping). All visual concerns move to `RapidFireView` and leaves.

### Pure helper: `toRapidFireViewState`

Extract into a co-located file (e.g. `_components/rapid-fire-view-state.ts`) as a named export. Signature:

```ts
function toRapidFireViewState(
  state: RapidFireReducerState,
  timerBarPct: number | null,
): RapidFireViewState
```

Collapses the reducer's 6 statuses into the 5-variant view union per ADR-0005:
- `loading` → `{ status: 'loading' }`
- `question` → `{ status: 'question', ..., locked: false, timerBarPct: timerBarPct ?? 100 }`
- `submitting` → `{ status: 'question', ..., locked: true, timerBarPct: timerBarPct ?? 0 }`
- `feedback` → `{ status: 'feedback', ... }`
- `result` → `{ status: 'result', result }`
- `error` → `{ status: 'error', message }`

Unit-tested in `rapid-fire-view-state.test.ts`: one test per reducer status, plus an assertion that `submitting` collapses to `question` with `locked: true`, plus null-`timerBarPct` handling.

### Dumb assembled view: `RapidFireView.tsx`

Props: `{ viewState: RapidFireViewState; onSelectOption: (optionIndex1: number, timeMs: number) => void; onBackToLobby: () => void }`. Zero hooks. Switches on `viewState.status` and renders the appropriate leaf component composition. Owns the page-level layout wrapper (`<div className="mx-auto max-w-lg space-y-4 p-6">`).

### Leaf components (co-located in `_components/`)

- **`QuestionCard.tsx`** — props: `{ question, options, phase: 'question' | 'feedback', selected: number | null, correctOption: number | null, lastCorrect: boolean | null, locked: boolean, currentScore: number, timerBar?: React.ReactNode, feedbackOverlay?: React.ReactNode, onSelectOption: (optionIndex1: number, timeMs: number) => void }`. Renders the question text, four `Button` options with the correct/wrong/locked classes (move `optionButtonClass` into this file as a private helper), and renders the `timerBar` and `feedbackOverlay` slots if provided. Captures the click → elapsed-time computation that today lives in `RapidFireClient`.
- **`FeedbackOverlay.tsx`** — props: `{ lastCorrect: boolean | null; currentScore: number }`.
- **`ResultCard.tsx`** — props: `{ score, correctCount, wrongCount, skippedCount, timeTakenSeconds, onBackToLobby }`.
- **`RapidFireErrorState.tsx`** — props: `{ message?: string; onBackToLobby: () => void }`.

The shared `TimerBar` from Sub-2 is rendered inside `RapidFireView` (when `viewState.status === 'question'`) and passed into `QuestionCard` via its `timerBar` slot prop. Same for `FeedbackOverlay` via `feedbackOverlay` slot. Slot props keep `QuestionCard` reusable without hard-wiring timer/feedback knowledge into it.

### Stories

- `TimerBar.stories.tsx` — already exists from Sub-2.
- `QuestionCard.stories.tsx` — `Question`, `FeedbackCorrect`, `FeedbackWrong`.
- `FeedbackOverlay.stories.tsx` — `Correct`, `Wrong`.
- `ResultCard.stories.tsx` — `Default` (mid-range), optionally `PerfectScore` and `AllSkipped` if useful.
- `RapidFireErrorState.stories.tsx` — `Default`.
- `RapidFireView.stories.tsx` — one story per `viewState.status`: `Loading`, `Question` (locked: false, ~70% timer), `QuestionLocked` (locked: true), `Feedback` (one correct variant), `Result`, `ErrorStory` (sidebar label `Error` when supported).

All story files: meta omits `title`; callbacks use `fn()` from `storybook/test` (see Conventions).

### What does not change

- `useRapidFireReducer` and its action/state types — zero edits.
- `services/rapid_fire/*` — zero edits.
- `lib/api/rapid_fire.ts` — zero edits.
- All Tailwind class strings — move verbatim.
- React Query keys, hydration, `page.tsx` — zero edits.
- Timer interval cadence (50ms) and constants (`FEEDBACK_DURATION_MS`, `QUESTION_START_DELAY_MS`) — unchanged.

## Acceptance criteria

- [x] `RapidFireClient.tsx` contains zero JSX beyond `<RapidFireView ... />` (and any provider wrapping)
- [x] `RapidFireView.tsx`, `QuestionCard.tsx`, `FeedbackOverlay.tsx`, `ResultCard.tsx`, `RapidFireErrorState.tsx` exist with the props shapes above (plus `questionEnteredAtRef` on `QuestionCard` / `RapidFireView` per Conventions)
- [x] `toRapidFireViewState` is exported from `_components/rapid-fire-view-state.ts` as a pure function
- [x] `rapid-fire-view-state.test.ts` covers all 6 reducer statuses; `submitting` collapses to `question` with `locked: true`; null `timerBarPct` handled
- [x] `useRapidFireReducer.test.ts` and all other existing tests pass with no behavioural assertion edits
- [x] All six `RapidFireView` status stories defined (`ErrorStory` for error state; verify in Storybook locally)
- [x] Every leaf component has at least a `Default` story
- [x] No service or hook imports in `RapidFireView` or any Rapid Fire leaf component
- [ ] Manual smoke test (`bun dev`): full Rapid Fire playthrough works end-to-end — login → start → answer 15 questions (mix correct/wrong/skip via timer) → see result → back to lobby. Navigation guard still fires on mid-game back. Refresh mid-question resumes correctly.
- [x] `bun run lint`, `bun run typecheck`, `bun run test` all pass

**Note:** `bun run build-storybook` requires **Node 20.19+** (or 22.12+). This environment reported Node v20.18.2; upgrade locally to verify the Storybook build.
