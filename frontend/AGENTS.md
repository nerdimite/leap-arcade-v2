# AGENTS.md — LEAP Frontend

## Tech Stack & Architecture

- **Framework**: Next.js 16 (App Router) · React 19 · TypeScript
- **Styling**: Tailwind CSS v4 · shadcn/ui (`src/components/ui/`) · Radix UI · Lucide icons
- **Data fetching**: `@tanstack/react-query` · Zod (schemas in `src/services/`)
- **Linting**: Biome · **Formatting**: Prettier
- **Package manager**: `bun`

**Route structure:**
```
src/app/
  (auth)/login/         — login page (corp ID + event code)
  (games)/              — shared layout: NavigationGuardProvider + GameNavigationGuardDialog
    wiki/               — Wikipedia Speed Run
    picture/            — Picture Illustration
    rapid-fire/         — Rapid Fire Quiz
    four-pics/          — Four Pics, One Lie
    crossword/          — Crossword Puzzle
  lobby/                — game tile grid + mini leaderboard
  leaderboard/          — full leaderboard page
  admin/                — facilitator view (stub)
```

**Module layout:**
```
src/
  components/
    ui/           shadcn primitives — add via `bunx shadcn@latest add <component>`
    game/         shared game chrome: Timer, ScoreBar, HintButton, GameShell
    layout/       AppShell, Navbar, GameNavigationGuardDialog
  hooks/          useNavigationGuard, useUnsavedChanges, utility hooks only (no data fetching)
  lib/
    api/          typed fetch wrappers per domain (auth, games, leaderboard)
    auth/         JWT helpers, token read/write
  services/       React Query hooks + Zod schemas, one folder per domain
  types/          shared TypeScript types and enums
```

## Project Purpose

Game-show-style tournament platform for Fidelity's LEAP graduate programme. Players (pre-seeded, no self-registration) log in, play 5 mini-games in any order from the lobby, and rank on a live leaderboard.

Key domain terms: player, game_session, lobby, leaderboard, corp_id, event_code, score, hint.

All `/api/*` requests are proxied from Next.js to FastAPI via `next.config.mjs` rewrites — one origin, no CORS.

## Development Workflow

- **Install**: `bun install`
- **Dev server**: `bun dev`
- **Build**: `bun build`
- **Lint (Biome)**: `bun run lint` · auto-fix: `bun run lint:fix`
- **Format**: `bun run format`
- **Type check**: `bun run typecheck`
- **Add shadcn component**: `bunx shadcn@latest add <component>`

## Dos and Don'ts

- Use `bun`, not npm or yarn
- Co-locate route-specific components and hooks in `app/<route>/_components/` and `app/<route>/_hooks/` — promote to `src/components/` only when used across 2+ routes
- React Query hooks live in `src/services/<domain>/hooks.ts` — not in `src/hooks/`
- `src/hooks/` is for utility hooks only (e.g. `useNavigationGuard`, `useTimer`) — no data fetching, no domain logic
- API shapes use Zod — schemas co-located in `src/services/<domain>/`
- Add shadcn components via `bunx shadcn@latest add` — never create them manually in `src/components/ui/`
- Server components: layout shells, auth checks, lobby initial fetch, game page session rehydration
- Client components: all game UIs, timers, answer interactions, score feedback — use `useReducer` per game for all state transitions
- Server-side timer is the source of truth — never trust client-reported elapsed time; derive the display timer from `started_at` returned by the server
- Use `refetchInterval` on the leaderboard query (lobby mini-view + full page) — do not hand-roll `setInterval` + fetch for polling
- Use `useMutation` for answer submissions — it handles `isPending` guards and prevents double-submits
- Every game sets `setIsDirty(true)` via `useNavigationGuard` on session start and `setIsDirty(false)` on completion — this arms the history trap and `beforeunload` handler automatically

## Agent Memory

### Learned User Preferences

(none yet — update as you work with agents on this codebase)

### Learned Workspace Facts

- Navigation guard (`src/hooks/use-navigation-guard.tsx`) is adapted from the cap-web-app project — it traps both browser back (via `pushState` + `popstate`) and page unload (`beforeunload`); `isDirty` maps to "game in progress" in this context
- The `(games)` route group layout mounts `NavigationGuardProvider` and `GameNavigationGuardDialog` — individual game pages only need to call `setIsDirty`
- `@/*` alias resolves to `src/*` — set in `tsconfig.json`
- Next.js 16 renames `middleware.ts` → `proxy.ts`; export function renamed from `middleware` to `proxy`; edge runtime NOT supported in `proxy` (nodejs only) — see Next.js 16 upgrade guide
- Auth is httpOnly cookie — set by `app/api/auth/login/route.ts` (Next.js Route Handler), not FastAPI. See ADR-0001.
- All `/api/*` calls go through catch-all Route Handler `app/api/[...path]/route.ts` which injects `Authorization: Bearer <token>` from the cookie. FastAPI unchanged. See ADR-0002.
- Lobby fetches player session statuses server-side via `GET /players/me/sessions` (new backend endpoint to be added)
- Leaderboard: `refetchInterval: 5000` — top 10 + current player pinned if outside top 10 in lobby sidebar; all players on full leaderboard page
- Rapid Fire per-question timer resets to full `time_limit_ms` on page refresh — no sessionStorage tracking. See ADR-0003.
- Rapid Fire feedback phase: 1.5s auto-advance after answer, 0.5s get-ready delay before next question timer starts — both configurable in `src/lib/constants.ts`
- Abandon is navigation-guard-only — no explicit abandon button on game screens
- Game result is shown inline on the game page (reducer transitions to `result` state); no separate result route
- TypeScript types come from `z.infer<>` on Zod schemas in `src/services/<domain>/schema.ts` — no separate `types/` duplication
- Test stack: Vitest + React Testing Library + msw. Test targets: reducer state transitions, Zod schema parsing, API client fetch wrappers, login form mutation.

## Reference Docs

| Doc | When to read |
|-----|-------------|
| `docs/patterns/index.md` | Entry point — what pattern docs exist and when to use them |
| `docs/project_brief.md` | Game rules, scoring logic, and architecture decisions |
