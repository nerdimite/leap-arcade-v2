# Sub-7: Leaderboard page refactor

**Status:** done  
**Blocked by:** — (completed)  
**Blocks:** None

## Parent

`docs/issues/frontend-dumb-smart-storybook/parent.md`

## ⚠️ Mirror Sub-3 and Sub-4 conventions

Read `app/(games)/rapid-fire/_components/` and `app/(games)/wiki/_components/` first. Mirror file naming, leaf-component patterns, story file shape.

## What to build

The smallest refactor in the set. `LeaderboardClient` today is a single component that owns the React Query hook and renders a table. Split into smart wiring + a `LeaderboardTable` leaf.

### Smart layer (`LeaderboardClient.tsx`)

Owns `useLeaderboard` and passes `entries` into the leaf. Renders the page layout wrapper, heading, and subheading (these are page-level concerns and stay with the client) — then renders `<LeaderboardTable entries={entries} />`.

Alternative considered: put the page wrapper in a `LeaderboardView` and pass `entries` through. Decision: skip the assembled `*View` for this slice because the only thing in the wrapper is heading text — no status switching, no leaf composition beyond the single table. A `LeaderboardView` would be pure noise. (If future polish adds page-level states like loading skeleton or empty-state CTA, promote to `LeaderboardView` then.)

### Leaf (`LeaderboardTable.tsx`)

Props: `{ entries: LeaderboardEntry[] }`. Pure render — the table wrapper, headers, and rows. All Tailwind classes move verbatim. When `entries.length === 0` it should render a friendly empty state inside the bordered card (e.g. "No scores yet — be the first." — pick something neutral; this is the one micro-copy decision allowed in this slice since the empty state has no existing copy).

### Stories

`LeaderboardTable.stories.tsx`:
- `Default` — 8 mock entries with varied scores
- `Empty` — `entries: []`

### What does not change

- `services/leaderboard/*` and `lib/api/leaderboard.ts` — zero edits.
- `leaderboard/page.tsx` — zero edits.
- All Tailwind class strings — move verbatim.

## Acceptance criteria

- [x] `LeaderboardClient.tsx` owns `useLeaderboard` and renders `<LeaderboardTable entries={entries} />` inside the page wrapper
- [x] `LeaderboardTable.tsx` is a pure render with the props shape above
- [x] `LeaderboardTable.stories.tsx` ships `Default` and `Empty` stories
- [x] Empty state is visible in Storybook and in the real app when no entries are returned
- [x] No service or hook imports in `LeaderboardTable`
- [ ] Manual smoke test (`bun dev`): leaderboard page renders correctly with populated data and refreshes every 5s
- [x] `bun run lint`, `bun run typecheck`, `bun run test` all pass
