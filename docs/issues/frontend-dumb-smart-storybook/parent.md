# Frontend: dumb/smart component split + Storybook setup

**Status:** done

## What to build

Refactor every implemented frontend screen (Login, Lobby, Rapid Fire, Wikipedia Speed Run, Leaderboard) into a smart/dumb split mirroring the cap-web-app reference pattern. Add a Storybook setup so any screen and any leaf component can be rendered in isolation against static prop fixtures. No functional behaviour changes for players; no backend changes.

**PRD:** `docs/plans/2026-05-17-frontend-dumb-smart-storybook-prd.md`  
**ADR:** `docs/adr/0005-frontend-dumb-smart-split-and-storybook.md`

## Execution plan

```
Batch A — parallel, no blockers
  Sub-1: Storybook setup + AGENTS.md update + prettier fix
  Sub-2: Shared primitives (formatMs → src/lib/utils.ts; TimerBar → src/components/game/)

Batch B — needs Sub-1 + Sub-2; reference refactor (single slice)
  Sub-3: Rapid Fire refactor — establishes in-code conventions for *Client / *View / leaf naming, story shape, viewState helper extraction. Subsequent slices mirror this slice.

Batch C — needs Sub-3; second pattern-application (single slice)
  Sub-4: Wikipedia Speed Run refactor — applies the Sub-3 pattern to the most complex client, including the sanctioned WikiArticlePane useEffect exception.

Batch D — parallel, needs Sub-4
  Sub-5: Login refactor (page becomes server component; LoginClient + LoginView)
  Sub-6: Lobby refactor (LobbyView + GameTile + MiniLeaderboard extraction)
  Sub-7: Leaderboard page refactor (LeaderboardTable extraction)
```

## Overall acceptance criteria

- [x] Every existing Vitest unit test passes with no behavioural assertions edited (import paths may move) — 93/93 passing
- [ ] `bun run storybook` boots and shows the path-derived sidebar for all stories — script wired; local boot requires Node 20.19+ (manual)
- [x] Every `*View` component has stories covering every status variant in its `viewState` union
- [x] Every leaf component has at least a `Default` story
- [x] `RapidFireClient` and `WikiClient` retain all hooks, mutations, timers, and navigation-guard wiring; no hooks or services imports exist in any `*View` or leaf component (sole exception: `WikiArticlePane`'s DOM click delegation `useEffect`)
- [x] `toRapidFireViewState` and `toWikiViewState` are pure exported functions with their own unit tests
- [x] `formatMs` is exported from `src/lib/utils.ts` with unit tests
- [x] `TimerBar` lives in `src/components/game/` and is consumed by Rapid Fire
- [x] `frontend/AGENTS.md` documents the `*Client` / `*View` rule and Storybook conventions
- [x] `.prettierrc` `tailwindStylesheet` path points at `src/app/globals.css`
- [ ] No restyling, copy changes, or visual tweaks — DOM output of every refactored screen is unchanged — manual smoke test pending
