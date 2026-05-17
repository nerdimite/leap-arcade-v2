# Sub-4: Wikipedia Speed Run refactor

**Status:** done  
**Blocked by:** Sub-3 (Rapid Fire reference slice — mirror its conventions)  
**Blocks:** Sub-5, Sub-6, Sub-7 (so all of Batch D can mirror a settled two-example pattern)

## Parent

`docs/issues/frontend-dumb-smart-storybook/parent.md`

## ⚠️ Mirror Sub-3's conventions

This slice applies the pattern established in Sub-3 (`app/(games)/rapid-fire/_components/`) to the most complex client in the codebase. Before writing code, read every file produced by Sub-3 and mirror: file naming, file header style, comment style, story file shape, callback prop naming, helper-extraction approach, and the `*Client` → `to*ViewState` → `*View` → leaves composition. Deviate only where a Wiki-specific concern genuinely requires it; document deviations in the PR description.

## What to build

Refactor `WikiClient` from a 440-line monolith into a thin smart wiring layer + assembled dumb `WikiView` + leaf components. Behaviour for players is unchanged.

### Smart layer (`WikiClient.tsx`)

Retain all hooks, mutations, refs, effects, and navigation-guard wiring it currently owns:
- `useWikiReducer` (untouched)
- `useNavigationGuard`, `postWikiPlay`, `postWikiNavigate`, `postWikiBack`, `postWikiTimeout`, `postWikiAbandon`
- The 250ms `setInterval` `TICK` dispatch
- All `useEffect` blocks: server-timeout sync, abandon registration, dirty-flag, interval lifecycle, `pathRoot` reset on `attempt_id` change
- `useCallback` wrappers for `navigateToTitle`, `continueViaPlay`, `wikiBack`
- Local state: `navPending`, `continuePending`, `pathRoot`
- Refs: `tickRef`, `attemptIdRef`, `serverTimeoutSyncRef`

The client now computes `viewState = toWikiViewState(state, { pathRoot, navPending, continuePending })` and renders `<WikiView viewState={viewState} onNavigate={navigateToTitle} onBack={wikiBack} onContinue={continueViaPlay} />`. No JSX in the client beyond this.

### Pure helper: `toWikiViewState`

Extract into `_components/wiki-view-state.ts`. Signature:

```ts
function toWikiViewState(
  state: WikiReducerState,
  ui: { pathRoot: string; navPending: boolean; continuePending: boolean },
): WikiViewState
```

Collapses reducer phases per ADR-0005:
- `terminal` + `play.state === 'completed'` → `{ status: 'finalCompleted', totalScore, results }`
- `terminal` + `play.state === 'abandoned'` → `{ status: 'finalAbandoned', totalScore, results }`
- `error` → `{ status: 'error', message }`
- `puzzleResult` with `puzzleResult != null` → `{ status: 'puzzleResult', result, totalScore, hasNext, continuePending }`
- `play.state === 'active'` → `{ status: 'active', current, pathRoot, timerRemainingMs, completedCount, totalScore, navPending }`
- Any other combination → no-render (treat as `loading` or null; Wiki currently returns `null` in that case — preserve this)

Unit-tested in `wiki-view-state.test.ts`: one test per phase × play-state combination including the two terminal variants, the `null`-puzzleResult guard, and the fallback case.

### Dumb assembled view: `WikiView.tsx`

Props: `{ viewState: WikiViewState; onNavigate: (title: string) => void; onBack: () => void; onContinue: () => void }`. Switches on `viewState.status` and renders the corresponding leaf. Returns `null` for the fallback case.

### Leaf components (co-located in `_components/`)

- **`WikiActiveView.tsx`** — the full in-game layout: sticky header, progress bar, clue, breadcrumb, timer, stats, article pane. Props: `{ current, pathRoot, timerRemainingMs, completedCount, totalScore, navPending, onNavigate, onBack }`. Uses `formatMs` from `src/lib/utils.ts` (Sub-2). Composes `WikiProgressBar`, `WikiClickBreadcrumb`, `WikiArticlePane`.
- **`WikiProgressBar.tsx`** — promoted from inline; props: `{ puzzleIndex, puzzleCount, completedCount }`.
- **`WikiClickBreadcrumb.tsx`** — promoted from inline; props: `{ pathRoot, clickPath }`.
- **`WikiArticlePane.tsx`** — promoted from inline `memo`. **Retains its `useEffect` for DOM click delegation on the server-rendered Wikipedia HTML.** This is the only sanctioned hook-in-leaf exception (see ADR-0005). Props: `{ currentTitle, articleHtml, navPending, onNavigate }`. The effect intercepts anchor clicks (`data-wiki-title` attribute) and calls `onNavigate(title)`; it does not touch services, hooks, or stores.
- **`WikiPuzzleResultCard.tsx`** — between-puzzles result screen. Props: `{ targetTitle, steps, score, timeMs, totalScore, hasNext, onContinue, continuePending }`.
- **`WikiFinalResults.tsx`** — promoted from inline; props: `{ totalScore, results, title?, subtitle? }`. Variant subtitles for completed vs abandoned are passed in by `WikiView`.

### Consumer migration: `formatMs`

Remove the inline `formatMs` from `WikiClient` (now in `WikiActiveView` — but the actual consumer is `WikiActiveView`, not the client). Import `formatMs` from `src/lib/utils.ts` (Sub-2).

### Stories

- `WikiProgressBar.stories.tsx` — `Default` (e.g. 5 puzzles, on puzzle 3, 2 completed).
- `WikiClickBreadcrumb.stories.tsx` — `Default` with a 4-step path.
- `WikiArticlePane.stories.tsx` — `Default` (with a static HTML snippet containing a `data-wiki-title` anchor for visual clarity) + `NavPending` (overlay shown).
- `WikiPuzzleResultCard.stories.tsx` — `HasNext`, `ViewFinalResults`.
- `WikiFinalResults.stories.tsx` — `Completed`, `Abandoned` (different subtitle).
- `WikiActiveView.stories.tsx` — `Default` (timer at e.g. 45s, mid-game stats).
- `WikiView.stories.tsx` — `Active`, `PuzzleResult`, `FinalCompleted`, `FinalAbandoned`, `Error`.

All callbacks: `fn()` from `@storybook/test`.

### What does not change

- `useWikiReducer` and its action/state types — zero edits.
- `services/wiki/*` and `lib/api/wiki.ts` — zero edits.
- `wiki-article.css` — unchanged; imported by `WikiArticlePane` after move.
- 250ms tick cadence, all reducer dispatches, all mutation calls — preserved in `WikiClient`.
- `WikiClient.test.tsx` — must continue passing. If any assertion targets removed inline JSX structure, retarget to accessible names or test IDs that survive the refactor; do not change behavioural intent.

## Deviation notes (Sub-4)

- **Reducer type name:** Sub-3 aliases `WikiReducerState`; implementation imports `WikiState` from `useWikiReducer.ts` for parity with Rapid Fire (`RapidFireState`).
- **Fallback sentinel:** explicit `{ status: "none" }` in `WikiViewState`; `WikiView` returns `null` for `"none"` and has a trailing `return null` for exhaustiveness safety.
- **Async callbacks:** `WikiViewProps` declares `onBack` / `onContinue` as `Promise<void> | void`; `WikiView` wraps callers with `void` at puzzle continue and passes `() => void onBack()` into `WikiActiveView`, which exposes `onBack` as `() => void` (thin thunk boundary).
- **`WikiPuzzleResultCard` prop name:** intermediate card uses **`steps`** (maps from `WikiPuzzleResult.steps_taken`) per this sub-issue draft.

## Acceptance criteria

- [x] `WikiClient.tsx` contains zero JSX beyond `<WikiView ... />` (and provider wrapping)
- [x] All 6 leaf component files plus `WikiView.tsx` exist with props shapes above
- [x] `toWikiViewState` is a pure exported function with unit-test coverage for every phase × play-state combination
- [x] `formatMs` is imported from `src/lib/utils.ts`; the inline definition is removed
- [x] `wiki-article.css` import path updated to live with `WikiArticlePane.tsx`
- [x] `WikiArticlePane`'s click-delegation `useEffect` is preserved with identical semantics (intercepts anchors with `data-wiki-title`, calls `onNavigate`, respects `navPending`)
- [x] All `WikiView` status stories render correctly in Storybook
- [x] Every leaf component has at least one story
- [x] No service or hook imports in `WikiView` or any leaf except the sanctioned `WikiArticlePane` `useEffect`
- [x] `WikiClient.test.tsx` and all other existing tests pass; only assertion retargeting is allowed
- [ ] Manual smoke test (`bun dev`): full Wikipedia Speed Run playthrough — navigate through a puzzle by clicking links, complete a puzzle, continue to next, complete all 5, see final results. Back button works when enabled. Timer expiry calls `/timeout`. Mid-game back navigation triggers the abandon dialog.
- [x] `bun run lint`, `bun run typecheck`, `bun run test` all pass
