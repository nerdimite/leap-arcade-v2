# ADR-0005 — Frontend dumb/smart component split and Storybook setup

**Status:** Accepted  
**Date:** 2026-05-17

---

## Context

The frontend `*Client` components (e.g. `RapidFireClient`, `LobbyClient`) mix API mutations,
React Query hooks, navigation-guard side effects, timer intervals, and all JSX rendering in a
single file. This makes the UI impossible to iterate on in isolation — every design change
requires a running backend and authenticated session.

The goal is to adopt the same dumb/smart separation used in the cap-web-app reference repo so
that:

- Any screen can be rendered in Storybook with static prop fixtures, no server required.
- Design iteration (layout, colour, typography, state variants) is decoupled from business logic.
- Smart containers shrink to pure wiring: reducer → viewState, hooks → callbacks.

---

## Decision

### 1. Naming convention

| Layer | Suffix | Owns |
|-------|--------|------|
| Smart shell | `*Client` (unchanged) | Hooks, mutations, effects, navigation guard, reducer |
| Assembled dumb page | `*View` | Receives `viewState` + callback props; renders sub-components |
| Leaf dumb component | no suffix | Props in, UI out; zero hooks, zero side effects |

`*Client` keeps its suffix because it is an established Next.js App Router convention ("this
requires `"use client"`"). Adding `*Container` would be churn with no semantic gain.

### 2. Component scope — full sweep

All implemented screens get the split:

- **Login** — `LoginView` extracted from `login/page.tsx`; `page.tsx` becomes a server
  component that renders `LoginClient` (new).
- **Lobby** — `LobbyView` (tile grid + layout); `GameTile` (leaf); `MiniLeaderboard` (leaf,
  extracted from `LobbyLeaderboardSidebar`).
- **Rapid Fire** — `RapidFireView` (owns status switch); `QuestionCard`, `TimerBar`,
  `FeedbackOverlay`, `ResultCard`, `RapidFireErrorState` (leaves).
- **Wikipedia Speed Run** — `WikiView` (owns status switch); `WikiActiveView`,
  `WikiProgressBar`, `WikiClickBreadcrumb`, `WikiArticlePane`, `WikiPuzzleResultCard`,
  `WikiFinalResults` (leaves promoted from inline definitions in current `WikiClient`).
- **Leaderboard** — `LeaderboardTable` (leaf).

**Exception:** `WikiArticlePane` keeps a `useEffect` for DOM click delegation on the
server-rendered Wikipedia HTML (`dangerouslySetInnerHTML`). This is a UI/DOM concern, not a
data-fetching one — it takes `onNavigate` as a callback and never touches services. Leaf
components otherwise have no hooks.

**Utility promotion:** the `formatMs(ms)` helper (currently inline in `WikiClient`) moves to
`src/lib/utils.ts` since it is a pure function reusable by any timed game.

### 3. Shared game chrome → `src/components/game/`

`TimerBar` (and any future shared game component, e.g. `ScoreDisplay`) lives in
`src/components/game/`. Route-specific components stay co-located in `_components/`.
Promotion rule: promote only when used by 2+ routes.

### 4. `RapidFireView` props: collapsed viewState discriminated union

The reducer has 6 internal statuses (`loading`, `question`, `submitting`, `feedback`, `result`,
`error`). `RapidFireClient` maps these to a 5-variant view union before passing to
`RapidFireView`:

```
type RapidFireViewState =
  | { status: 'loading' }
  | { status: 'question'; question: Question; timerBarPct: number; currentScore: number; questionsAnswered: number; questionsTotal: number; locked: boolean }
  | { status: 'feedback'; question: Question; lastCorrect: boolean; lastCorrectOption: number | null; submittedOption: number | null; currentScore: number; questionsAnswered: number; questionsTotal: number }
  | { status: 'result'; result: ResultData }
  | { status: 'error'; message: string }
```

`submitting` collapses into `question` with `locked: true`. `timerBarPct` is computed in
`RapidFireClient` (which owns the interval) and passed as a plain number. `RapidFireView` is
timer-free.

### 5. Storybook: static snapshot stories, `@storybook/nextjs-vite`

- Framework: `@storybook/nextjs-vite` (mirrors cap-web-app; Vite already used for Vitest).
- **Page-level stories** (`*View.stories.tsx`): one story per status variant, static `args`,
  `fn()` stubs for callbacks. Timer does not tick in stories — bars are held at a fixed
  percentage.
- **Leaf stories**: single `Default` story unless multiple visual variants warrant more.
- No MSW wiring in stories — that is integration-test territory (already covered by Vitest +
  MSW in `src/test/`).
- `preview.tsx` wraps every story with `ThemeProvider` (next-themes) and a fresh
  `QueryClientProvider` (defensive; dumb views don't call hooks but composed stories might).

### 6. Two independent leaderboard components

`MiniLeaderboard` (sidebar, compact, top-10, pinned "your rank") and `LeaderboardTable` (full
page, all players) are separate dumb components. A `compact` prop that also changes pinning
logic would be a hidden coupling; the two UIs are genuinely different enough to warrant
independent components sharing only the `LeaderboardEntry` type.

---

## Consequences

- `*Client` files shrink to wiring only; large JSX blocks move to `*View` counterparts.
- `login/page.tsx` stops being `"use client"` — it becomes a proper server component.
- `src/components/game/` gains real inhabitants (`TimerBar` first, others as games are built).
- Storybook stories are co-located with each component (same folder, `.stories.tsx` suffix).
- The existing Vitest + MSW test suite is unchanged; stories and unit tests are complementary,
  not duplicative.
- Any future game added to the platform must follow the same `*Client`/`*View` split from day
  one — the Storybook story for its `*View` is part of the definition of done.

---

## Alternatives considered

- **Interactive Storybook stories with MSW** — rejected; timer-driven state makes stories
  transient and hard to hold for design work. Static snapshots are better for design iteration.
- **Single shared `LeaderboardTable` with `compact` prop** — rejected; pinning logic belongs
  only to the sidebar and would bloat a shared component.
- **Mirror reducer statuses exactly in `viewState`** — rejected; `submitting` is an
  internal orchestration concept, not a view concept; the view cares only about whether
  buttons are locked.
