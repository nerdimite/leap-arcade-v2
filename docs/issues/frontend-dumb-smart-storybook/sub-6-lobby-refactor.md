# Sub-6: Lobby refactor

**Status:** done  
**Blocked by:** Sub-4 (mirror Rapid Fire + Wiki conventions)  
**Blocks:** None

## Parent

`docs/issues/frontend-dumb-smart-storybook/parent.md`

## ⚠️ Mirror Sub-3 and Sub-4 conventions

Read `app/(games)/rapid-fire/_components/` and `app/(games)/wiki/_components/` first. Mirror file naming, leaf-component patterns, story file shape, and callback prop naming.

## What to build

Two parallel sub-refactors on the same page:

1. `LobbyClient` → slim wiring; extract `LobbyView` + `GameTile` leaf.
2. `LobbyLeaderboardSidebar` → slim wiring; extract `MiniLeaderboard` leaf.

### 1. Lobby tile grid

**`LobbyClient.tsx` (smart)**

Owns:
- `usePlayerSessions` from `services/players/hooks`
- `currentCorpId` prop (passed by `page.tsx`, unchanged)
- The helper functions currently inline: `sessionsByGameId(rows)`, `statusLabel(session)`. Keep them as private functions in this file; they are reducer-style mappers turning the raw `PlayerSession[]` into the props shape needed by `GameTile`.

Computes an array of `GameTileProps` (one per `GAME_TILES` entry, with `badge`, `score`, `locked`, `href`) and passes it to `<LobbyView tiles={tiles} sidebar={<LobbyLeaderboardSidebar currentCorpId={currentCorpId} />} />`.

The `sidebar` prop is a `React.ReactNode` slot — the smart sidebar wrapper is rendered by `LobbyClient`, but `LobbyView` doesn't know what's in it. Stories can pass either a real `<MiniLeaderboard>` with mocked entries (composed leaf), or a placeholder div.

**`LobbyView.tsx` (dumb)**

Props: `{ tiles: GameTileProps[]; sidebar: React.ReactNode }`. Owns the page layout wrapper, heading/subheading, and the responsive grid + sidebar arrangement. Renders one `<GameTile>` per tile.

**`GameTile.tsx` (leaf)**

Props:
```ts
{
  name: string
  description: string
  maxPoints: number
  badge: string
  score?: number | null
  href?: string
  locked: boolean
}
```

Renders either a `<Link href={href}>` (when not locked) or a `<div aria-disabled="true">` (when locked). All Tailwind classes and the `Lock` icon usage move verbatim.

**Stories:**
- `GameTile.stories.tsx` — `NotStarted`, `InProgress`, `Completed` (locked).
- `LobbyView.stories.tsx` — `AllAvailable`, `MixedStatuses`, `AllLocked`. Each composes a real `<GameTile>` array and passes a `<MiniLeaderboard>` (or placeholder) into the `sidebar` slot.

### 2. Mini leaderboard sidebar

**`LobbyLeaderboardSidebar.tsx` (smart)**

Owns:
- `useLeaderboard`
- The computation: slice top 10, find current player, decide `showPinned`. Keep the `normalizeCorp` helper as a private function here.

Passes plain props to `<MiniLeaderboard entries={top10} currentCorpId={currentCorpId} pinnedEntry={showPinned ? selfRow : undefined} />`.

**`MiniLeaderboard.tsx` (leaf)**

Props:
```ts
{
  entries: LeaderboardEntry[]
  currentCorpId: string | null
  pinnedEntry?: LeaderboardEntry
}
```

Owns the section wrapper, heading, top-10 table, and the pinned-row separator + table. Moves the `MiniRow` helper component into this file. The `normalize`-based highlighting logic stays — but accepts the pre-resolved `currentCorpId` and checks against each `entries[i].corp_id` directly (the normalization is symmetric so this is safe; preserve the same case-insensitive behaviour).

**Stories:**
- `MiniLeaderboard.stories.tsx` — `Default` (current player in top 10), `WithPinnedRow` (current player pinned below the separator).

### What does not change

- `services/leaderboard/*`, `services/players/*`, `lib/api/*` — zero edits.
- `lobby/page.tsx` — zero edits.
- `GAME_TILES` and `lib/game-tiles.ts` — zero edits.
- All Tailwind class strings — move verbatim.

## Acceptance criteria

- [x] `LobbyClient.tsx` contains zero JSX beyond `<LobbyView tiles={...} sidebar={...} />`
- [x] `LobbyView.tsx`, `GameTile.tsx`, `MiniLeaderboard.tsx` exist with props shapes above
- [x] `LobbyLeaderboardSidebar.tsx` is reduced to data fetching + computation; renders `<MiniLeaderboard ... />`
- [x] All five stories (3 for `GameTile`, 3 for `LobbyView`, 2 for `MiniLeaderboard`) render correctly
- [x] No service or hook imports in `LobbyView`, `GameTile`, or `MiniLeaderboard`
- [ ] Manual smoke test (`bun dev`): lobby loads with correct per-tile badges; completed/abandoned tiles are locked; sidebar shows top 10; if your corp_id is outside top 10, your row is pinned below the separator; leaderboard refreshes every 5s
- [x] `bun run lint`, `bun run typecheck`, `bun run test` all pass
