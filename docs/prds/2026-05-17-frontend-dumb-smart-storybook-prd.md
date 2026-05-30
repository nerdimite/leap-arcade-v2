# PRD: LEAP Frontend — Dumb/Smart Component Split + Storybook Setup

**Date:** 2026-05-17  
**Status:** Ready for implementation  
**Related ADR:** [ADR-0005 — Frontend dumb/smart split and Storybook setup](../adr/0005-frontend-dumb-smart-split-and-storybook.md)

---

## Problem Statement

The frontend `*Client` components today mix five concerns in a single file: React Query
mutations, navigation-guard side effects, timer intervals, reducer wiring, and all JSX
rendering. `RapidFireClient` is 289 lines and `WikiClient` is 440 lines. As a result:

- Designers and developers cannot iterate on UI states (feedback overlay, result card, error
  state, puzzle-complete card) without a running backend, a logged-in player, and a session in
  the right phase.
- Reproducing a specific game state visually — "show me the Wiki puzzle result screen with a
  perfect score" or "show me Rapid Fire feedback for a wrong answer with 8/15 progress" —
  requires playing the game by hand to that point.
- There is no Storybook in the project, so visual regression and component-level review have
  no surface to live on.
- Future games (Picture Illustration, Four Pics One Lie, Crossword — currently stubs) will
  inherit the same monolithic pattern unless we set the precedent now.

---

## Solution

Refactor every implemented screen into a smart/dumb split mirroring the cap-web-app reference
pattern, and add a Storybook setup on `@storybook/nextjs-vite` so any screen and any leaf
component can be rendered in isolation against static prop fixtures.

The smart layer (`*Client`) keeps all hooks, mutations, timers, and navigation-guard wiring.
It collapses the reducer's internal status union into a UI-facing `viewState` discriminated
union and passes that plus plain callbacks to the dumb assembled view (`*View`). The view
switches on `viewState.status` and renders leaf components (`QuestionCard`, `TimerBar`,
`ResultCard`, `WikiArticlePane`, etc.). Stories live co-located with every dumb component:
leaf stories show variants in isolation; assembled `*View` stories show the full page in each
status with frozen data.

Shared game chrome (`TimerBar` first, more as games are built) is promoted to
`src/components/game/`. Route-local components stay in `_components/`.

No functional behaviour changes for players. No backend changes. The existing Vitest + MSW
test suite continues to pass and is extended to cover any new pure helpers introduced by the
split.

---

## User Stories

### Designer / developer iteration

1. As a frontend developer, I want to render the Rapid Fire question UI in Storybook without
   a backend, so that I can adjust spacing and colours without playing the game.
2. As a frontend developer, I want to see the Rapid Fire feedback overlay in both "correct"
   and "wrong" states side by side, so that I can compare visual treatments.
3. As a frontend developer, I want to render the Rapid Fire result card with arbitrary
   `score`, `correct_count`, `wrong_count`, `skipped_count`, and `time_taken_seconds`, so
   that I can verify the layout with edge values (e.g. very high score, all-skipped run).
4. As a frontend developer, I want to render the Wiki active gameplay screen with a fixed
   timer value, so that I can iterate on the article-pane layout without the timer ticking
   down.
5. As a frontend developer, I want to render the Wiki final-results screen for both
   `completed` and `abandoned` Wikipedia Speed Run sessions, so that I can verify the
   subtitle and ordering of puzzle cards in each terminal state.
6. As a frontend developer, I want to render the Wiki puzzle-result interstitial in both
   "has next puzzle" and "view final results" variants, so that the CTA copy and pending
   state can be checked without playing four puzzles.
7. As a frontend developer, I want to render the Lobby tile grid with every combination of
   game statuses (`not_started`, `in_progress`, `completed`, `abandoned`), so that locked
   states are visually verifiable in one view.
8. As a frontend developer, I want to render the Mini Leaderboard with the current player
   both inside and outside the top 10, so that the pinned-row pattern is testable in
   Storybook.
9. As a frontend developer, I want to render the Login form in its idle, pending, and
   invalid-credentials states, so that error-message styling is iteratable without making
   real login attempts.
10. As a frontend developer, I want to render the full Leaderboard table with empty and
    populated states, so that the empty-state design is not forgotten.
11. As a designer, I want a Storybook URL I can open in a browser to see every screen and
    component in every state, so that I can review the UI without setting up the backend.

### Component reuse and consistency

12. As a frontend developer, I want a single shared `TimerBar` component that any timed game
    can use, so that the timer affordance is visually consistent across Rapid Fire, Wiki,
    and future games.
13. As a frontend developer, I want a single shared `formatMs` utility, so that timer
    formatting is consistent everywhere it appears.
14. As a frontend developer adding a new game in future, I want a clear `*Client` / `*View`
    pattern to follow, so that I don't reinvent the orchestration boundary.

### Continuity / no regressions

15. As a player, I want the Login, Lobby, Rapid Fire, Wikipedia Speed Run, and Leaderboard
    screens to behave identically to today after the refactor, so that the refactor is
    invisible to me.
16. As a player, I want the navigation guard to continue arming and disarming at the same
    points (game start / completion / abandon), so that I cannot accidentally lose progress.
17. As a player, I want the per-question timer in Rapid Fire and the puzzle timer in Wiki
    to continue running and expiring at the same moments as before, so that scoring is
    unchanged.
18. As a player, I want the lobby tiles to continue reflecting my per-game status from
    `GET /players/me/sessions`, so that completed games stay locked.
19. As a player, I want the leaderboard sidebar and full page to continue polling every 5
    seconds, so that live updates are unchanged.

### Test coverage

20. As a frontend developer, I want every existing unit test (reducer, schema, API wrapper,
    navigation guard, login form) to continue passing after the refactor, so that I know
    I haven't broken behaviour.
21. As a frontend developer, I want the `viewState` mapping function in each `*Client` to
    be a pure helper that can be unit-tested in isolation, so that reducer-to-view
    translation is covered by tests without rendering React.
22. As a frontend developer, I want `formatMs` to have its own unit tests, so that the
    promoted helper has explicit coverage independent of any consumer.

---

## Implementation Decisions

### Module inventory

#### Smart layer (`*Client.tsx`) — kept, slimmed down

Each `*Client` retains the same filename and is the only `"use client"` boundary for its
route. Its responsibilities shrink to: own the reducer + local UI state, own all hooks
(React Query, navigation guard, router), own all `useEffect` side effects (timers, mutation
calls, dirty-flag wiring), and compute a `viewState` value (and any pre-derived values such
as `timerBarPct`) that it passes to its `*View` counterpart along with plain callback props.

Modified clients: `LoginClient` (new — `login/page.tsx` becomes a server component),
`LobbyClient`, `LobbyLeaderboardSidebar`, `LeaderboardClient`, `RapidFireClient`,
`WikiClient`.

#### Assembled dumb views (`*View.tsx`) — new

Each route gets one assembled dumb view that owns the status switch and renders leaf
components. Views accept exactly two prop shapes:

- A `viewState` discriminated union (one variant per visual state)
- Callback props (`onSelectOption`, `onBackToLobby`, `onNavigate`, etc.)

Views have zero hooks beyond local UI state like popover-open or focus management. They are
pure renderers. New files: `LoginView`, `LobbyView`, `RapidFireView`, `WikiView`.

#### `RapidFireView` `viewState` shape (collapsed from reducer)

The Rapid Fire reducer's 6 internal statuses (`loading`, `question`, `submitting`,
`feedback`, `result`, `error`) collapse into a 5-variant view union. `submitting` collapses
into `{ status: 'question', locked: true, ... }`. The reducer is unchanged; the
collapsing happens in `RapidFireClient` via a pure `toViewState(state, timerBarPct)` helper:

```ts
type RapidFireViewState =
  | { status: 'loading' }
  | { status: 'question'; question: Question; timerBarPct: number;
      currentScore: number; questionsAnswered: number; questionsTotal: number;
      locked: boolean }
  | { status: 'feedback'; question: Question; lastCorrect: boolean;
      lastCorrectOption: number | null; submittedOption: number | null;
      currentScore: number; questionsAnswered: number; questionsTotal: number }
  | { status: 'result'; result: ResultData }
  | { status: 'error'; message: string }
```

#### `WikiView` `viewState` shape (collapsed from reducer)

Wiki's reducer phases (`active`, `puzzleResult`, `terminal`, `error`) collapse into a view
union that hides the inner `state.play.state` discrimination from the view:

```ts
type WikiViewState =
  | { status: 'active'; current: WikiCurrent; pathRoot: string;
      timerRemainingMs: number; completedCount: number; totalScore: number;
      navPending: boolean }
  | { status: 'puzzleResult'; result: WikiPuzzleResult; totalScore: number;
      hasNext: boolean; continuePending: boolean }
  | { status: 'finalCompleted'; totalScore: number; results: WikiPuzzleResult[] }
  | { status: 'finalAbandoned'; totalScore: number; results: WikiPuzzleResult[] }
  | { status: 'error'; message: string }
```

The `attemptId`-driven `pathRoot` resetting stays in `WikiClient`; the view receives
`pathRoot` as a plain string.

#### Leaf components — new

Route-local leaves co-located in `_components/`:

- **Lobby:** `GameTile`
- **Rapid Fire:** `QuestionCard`, `FeedbackOverlay`, `ResultCard`, `RapidFireErrorState`
- **Wiki:** `WikiActiveView`, `WikiProgressBar`, `WikiClickBreadcrumb`,
  `WikiArticlePane`, `WikiPuzzleResultCard`, `WikiFinalResults`
- **Leaderboard:** `LeaderboardTable`
- **Mini leaderboard:** `MiniLeaderboard` (extracted from `LobbyLeaderboardSidebar`)

Shared leaves promoted to `src/components/game/`:

- **`TimerBar`** — props: `percentage: number`. Used by Rapid Fire today; a Wiki-specific
  visualisation may use it later.

#### Leaf-component hook policy

Leaf components hold no hooks. **One exception:** `WikiArticlePane` keeps its
`useEffect`-based click delegation on the server-rendered Wikipedia HTML
(`dangerouslySetInnerHTML`). The effect intercepts anchor clicks and calls the
parent-supplied `onNavigate` callback — it never touches services, hooks, or stores. This
exception is recorded in ADR-0005.

#### Utility promotion

- `formatMs(ms: number): string` (currently inline in `WikiClient`) → `src/lib/utils.ts`.
- `optionButtonClass(...)` (currently inline in `RapidFireClient`) → stays co-located with
  `QuestionCard` as it is purely a view helper for that component.
- `sessionsByGameId(...)` and `statusLabel(...)` (currently inline in `LobbyClient`) →
  move into `LobbyClient` as private functions that build `GameTile` props; they are
  reducer-style mapping helpers, not view concerns.

#### Storybook setup

- **Framework:** `@storybook/nextjs-vite` (matches cap-web-app; Vite is already used by
  Vitest in this repo).
- **Addons:** `@storybook/addon-a11y`, `@storybook/addon-docs`, `@chromatic-com/storybook`,
  `@storybook/addon-vitest`.
- **Stories glob:** `../src/**/*.stories.@(ts|tsx)`.
- **Static dir:** `../public`.
- **`preview.tsx` decorators:** wraps every story in `ThemeProvider` (from
  `src/components/theme-provider.tsx`) plus a fresh `QueryClientProvider`. The
  `QueryClientProvider` is defensive — dumb views don't call hooks, but it removes a class
  of footguns if a story accidentally composes a smart child.
- **Story conventions:** no `title` field on `meta` (path-derived sidebar, same rule as
  cap-web-app); one `Default` story per leaf unless variants warrant more; one story per
  status for each `*View`.
- **Scripts:** `bun run storybook` (dev), `bun run build-storybook` (static export).

#### Story coverage targets

| Component | Stories |
|---|---|
| `TimerBar` | `Default`, `Low`, `Full` |
| `GameTile` | `NotStarted`, `InProgress`, `Completed` (locked) |
| `MiniLeaderboard` | `Default`, `WithPinnedRow` |
| `LeaderboardTable` | `Default`, `Empty` |
| `QuestionCard` | `Question`, `FeedbackCorrect`, `FeedbackWrong` |
| `ResultCard` | `Default` |
| `WikiProgressBar` | `Default` |
| `WikiClickBreadcrumb` | `Default` |
| `WikiArticlePane` | `Default`, `NavPending` |
| `WikiPuzzleResultCard` | `HasNext`, `ViewFinalResults` |
| `WikiFinalResults` | `Completed`, `Abandoned` |
| `LoginView` | `Idle`, `Pending`, `InvalidCredentials` |
| `LobbyView` | `AllAvailable`, `MixedStatuses`, `AllLocked` |
| `RapidFireView` | `Loading`, `Question`, `QuestionLocked`, `Feedback`, `Result`, `Error` |
| `WikiView` | `Active`, `PuzzleResult`, `FinalCompleted`, `FinalAbandoned`, `Error` |

### Behaviour-preservation invariants (no regressions)

The refactor is purely structural. The following must remain bit-identical:

- **Routing:** every URL renders the same final DOM (modulo refactored component
  composition). All `page.tsx` files keep their existing server/client boundary except
  `login/page.tsx`, which is promoted from a `"use client"` page to a server component that
  renders `<LoginClient />` (the form interaction logic moves verbatim into the new client
  component).
- **React Query keys, query options, and `staleTime`/`refetchInterval` values:** unchanged.
- **Hydration:** all `HydrationBoundary` placements and dehydrated query data keys are
  unchanged.
- **Reducers:** `useRapidFireReducer` and `useWikiReducer` are not edited. Their action and
  state shapes are stable.
- **Mutation calls:** the timing and order of `postPlay`, `postAnswer`, `postAbandon`,
  `postWikiPlay`, `postWikiNavigate`, `postWikiBack`, `postWikiTimeout`, `postWikiAbandon`
  are identical (same `useEffect` triggers, same `useCallback` definitions, just relocated
  into `*Client` only).
- **Navigation guard:** `setIsDirty` calls fire on the same state transitions; abandon
  registration still happens for in-progress game phases.
- **Timer intervals:** the 50ms Rapid Fire interval and 250ms Wiki interval stay where they
  are (inside `*Client`).
- **CSS classes:** all Tailwind class strings move verbatim. No restyling in this PRD —
  visual polish is a separate, follow-up effort that benefits from the new Storybook
  surface.

### Out-of-band: `tailwindStylesheet` config fix

`.prettierrc` currently points `tailwindStylesheet` at `app/globals.css`, but the file
lives at `src/app/globals.css`. This is unrelated to the refactor but was discovered in
exploration — fix in the same PR since it is a one-line change and tightens Tailwind class
sorting.

---

## Testing Decisions

### What makes a good test for this refactor

This PRD is a refactor. The dominant testing concern is **proving no regression** — every
existing unit test must continue to pass with no edits beyond import-path updates when files
move. New tests cover pure helpers introduced by the split, not React rendering of dumb
views (Storybook serves that purpose visually).

### Existing tests — must remain green

| Test | Why it matters |
|---|---|
| `useRapidFireReducer.test.ts` | Reducer is untouched; transitions must remain identical |
| `useWikiReducer.test.ts` | Same |
| `services/auth/schema.test.ts`, `services/leaderboard/*.test.ts`, `services/players/*.test.ts`, `services/rapid_fire/schema.test.ts` | Schemas are untouched |
| `lib/api/*.test.ts` (auth, players, rapid_fire, wiki) | API wrappers are untouched |
| `lib/constants.test.ts` | Constants are untouched |
| `proxy.test.ts`, `api-catch-all-proxy.test.ts` | Server-side surface untouched |
| `services/leaderboard/hooks.test.tsx`, `services/players/hooks.test.tsx` | React Query hooks untouched |
| `app/(games)/wiki/_components/WikiClient.test.tsx` | Existing client-level integration test must still pass against the slimmed `WikiClient` — assertions should be behavioural (clicks, navigation calls, dialog interactions), not DOM-structure-dependent. If existing assertions rely on JSX structure that the refactor changes, update them to target stable test IDs or accessible names, not the structural change |
| `components/layout/GameNavigationGuardDialog.*.test.tsx` | Dialog and abandon flow untouched |
| `app/api/auth/login/route.test.ts` | Server route untouched |
| `__tests__/login-page.test.tsx` | Existing login form integration test; assertions should target the new `LoginView` rendered inside `LoginClient`. Behavioural assertions (form submit, error message presence) survive; if any rely on the old `"use client"` page structure, update to address the same accessible behaviour |

### New tests (pure helpers only)

| Module | What to test |
|---|---|
| `toRapidFireViewState(state, timerBarPct)` — pure function in `RapidFireClient` (extract as a named export from a co-located helper file for testability) | Each reducer state produces the correct viewState variant; `submitting` collapses to `question` with `locked: true`; `pendingTimeMs == null` is handled |
| `toWikiViewState(state)` — pure function in `WikiClient` (extract similarly) | `state.phase === 'terminal'` with `play.state === 'completed'` → `finalCompleted`; with `'abandoned'` → `finalAbandoned`; `puzzleResult` requires `puzzleResult != null` |
| `formatMs(ms)` — promoted to `src/lib/utils.ts` | Negative input clamps to `0:00`; `61_000` → `1:01`; `3_599_000` → `59:59`; non-integer milliseconds floor correctly |

### Stories vs unit tests

Storybook stories are not a substitute for behavioural tests — they are visual fixtures. The
existing Vitest + MSW suite remains the source of truth for behaviour. Stories cover the
"can a designer see this state?" question.

### Prior art

- Reducer transition tests: `useRapidFireReducer.test.ts`, `useWikiReducer.test.ts`
- API wrapper + MSW tests: `lib/api/rapid_fire.test.ts`
- Component-level integration test: `WikiClient.test.tsx`, `GameNavigationGuardDialog.*.test.tsx`
- Form/component test: `__tests__/login-page.test.tsx`

---

## Out of Scope

- **Visual / design changes.** No restyling, no copy changes, no spacing tweaks. The point
  of this PRD is to make those changes *easy in a follow-up* via Storybook.
- **Reducer changes.** `useRapidFireReducer` and `useWikiReducer` are not edited.
- **Backend changes.** Zero backend files are touched.
- **Stub games.** Picture Illustration, Four Pics One Lie, Crossword pages remain stubs.
  The pattern this PRD establishes will be applied to them when they're built — not now.
- **New Playwright / browser e2e coverage.** Tracked separately.
- **Visual regression (Chromatic) integration.** The Chromatic addon is included to leave
  the door open, but no Chromatic project setup, baseline, or CI integration is in scope.
- **MSW-driven interactive stories.** Static snapshot stories only (per ADR-0005). If
  interactive stories become valuable later, they can be added without revisiting this
  refactor.
- **Promotion of additional shared game components.** Only `TimerBar` is shared today.
  `ScoreDisplay`, `GameShell`, etc. can be extracted as future games introduce duplication.

---

## Further Notes

- The `*Client` / `*View` naming is non-negotiable for any new game UI added later — recorded
  in ADR-0005 and the frontend `AGENTS.md` will be updated accordingly as part of this work.
- `WikiArticlePane`'s `useEffect` for click delegation is the only sanctioned exception to
  the "no hooks in leaf components" rule. New leaf components needing a hook should be
  questioned in review — most likely the hook belongs in `*Client` and a callback should be
  passed down instead.
- The `viewState` mapping helpers (`toRapidFireViewState`, `toWikiViewState`) should be
  exported from co-located files (e.g. `_components/rapid-fire-view-state.ts`) so that they
  are testable as plain functions without rendering React.
- After implementation, `frontend/AGENTS.md` must be updated with two new entries: the
  `*Client` / `*View` rule and the Storybook conventions (path-derived titles, decorators,
  one-story-per-status pattern).
- The `tailwindStylesheet` fix in `.prettierrc` should be in the same PR so that Tailwind
  class sorting works for the many touched files.
