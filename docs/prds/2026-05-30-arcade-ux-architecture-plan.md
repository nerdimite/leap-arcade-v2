# Arcade UX & Component Architecture Plan

Date: 2026-05-30
Status: Draft (foundational decisions confirmed; per-game detail iterating)
Register: product (see `PRODUCT.md`, `DESIGN.md`)

This plan consolidates the information-architecture, layout, and component-decomposition
decisions for the Glitch & Giggle frontend as it moves to a unified arcade system. It
covers the global chrome, the lobby, the game-entry flow (incl. a new instructions view),
the shared game shell, and a per-game IA pass.

---

## 1. Confirmed cross-cutting decisions

| # | Decision | Choice |
|---|----------|--------|
| 1 | Global top bar | Persistent bar on **lobby + leaderboard only**; games stay full-focus with just their own `GameHeader`. |
| 2 | Bar contents | Wordmark (`◤ GLITCH & GIGGLE`, links to lobby) · corp ID · logout · `Leaderboard →` link. **No tournament clock.** |
| 3 | Game-entry flow | **Dedicated instructions route.** `/<game>` = instructions (no `postPlay`); `/<game>/play` = the session. Fresh tile → `/<game>`; resume tile → `/<game>/play`. |
| 4 | Instructions content | **Objective + how-to bullets only**, no scoring/points. Start CTA + back-to-lobby. Copy distilled from PRDs into a `GAME_INSTRUCTIONS` registry. |
| 5 | GameShell scope | Shell owns `--accent` (from `gameId`) + page container + the **state switch via named slots**. View becomes mostly slot content + `GameHeader`. |

---

## 2. Global chrome (new)

New `components/chrome/AppBar.tsx` (name TBD), rendered by the `/lobby` and `/leaderboard`
layouts only.

- **Left:** `◤ GLITCH & GIGGLE` wordmark (Press Start 2P, layered accent text-shadow per
  DESIGN §3), links to `/lobby`.
- **Right:** player corp ID (Inter meta) · logout control · `Leaderboard →` link.
- No clock (decision #2). Leave horizontal room so one could be added later without reflow.
- Styling: panel surface, 2px `--line` bottom border, cabinet-sm shadow. Default accent
  = Wiki Cyan (no game in context).
- A11y: keyboard-traversable, visible focus rings, logout is a real `<button>`.

Open: exact logout mechanism (clears the httponly cookie via existing auth proxy, see
`docs/adr/0001`). Wire to whatever the auth service already exposes.

---

## 3. Lobby IA

Structure stays: head (kicker + H1 + intro) → 2-col tile grid → sticky mini-leaderboard
sidebar. Changes:

- Identity/logout/leaderboard move **up into the global bar** (§2); remove any duplication
  from the lobby body.
- **Mini-leaderboard** gains a `View full board →` footer link to `/leaderboard` (second
  path alongside the bar link).
- **Tile action becomes status-aware** (`LobbyClient` already derives status):
  - not started → href `/<game>` (instructions)
  - active → href `/<game>/play` (resume, skips instructions)
  - completed/abandoned → locked, no nav (unchanged)
- `GameTile` keeps current visual (marquee, sprite, pill); only the resolved `href` and
  pill label depend on status.

---

## 4. Game-entry flow + Instructions view

### Routing change (all 7 games)
- `/<game>/page.tsx` → renders `InstructionsView` (no `postPlay`).
- `/<game>/play/page.tsx` → does the server-side `postPlay` + hydration + renders the
  existing `*Client` (this is today's `/<game>/page.tsx` logic, moved down a segment).
- Resume path links straight to `/play`, so instructions only appear on a fresh start.

### `InstructionsView` (new shared view)
Accent-themed single briefing card:
- `▸ {label}` kicker + `{tagline}` `<h1>` (reuses the `GAME_VISUALS` registry).
- One-line **objective**.
- **HOW TO PLAY**: 2–4 short bullets (controls hint where relevant, e.g. Crossword keys).
- Primary **START** button (accent fill) → navigates to `/<game>/play`.
- Secondary `← back to lobby`.
- No scoring/points (decision #4).

### `GAME_INSTRUCTIONS` registry (new)
`Record<LobbyGameId, { objective: string; howTo: string[] }>`, distilled from
`docs/game-req.md` + per-game PRDs + `docs/final_game_content/`. Lives alongside
`GAME_VISUALS` in `lib/` (or a dedicated `lib/game-instructions.ts`).

---

## 5. GameShell (the promoted header → full shell)

New `components/game/GameShell.tsx`. Owns the three things duplicated across every View.

```tsx
type GameShellProps = {
  gameId: LobbyGameId;          // derives --accent via GAME_VISUALS
  state: string;                // current viewState.status
  slots: Partial<Record<string, ReactNode>>; // keyed by status
  size?: "sm" | "md" | "lg" | "xl" | "wide"; // container max-width
  bleedStates?: string[];       // states that skip the container (own their layout)
  className?: string;           // flex-row etc. for grid games
};
```

- Sets `style={{ "--accent": GAME_VISUALS[gameId].accent }}` on the root (removes every
  `const <GAME>_ACCENT` constant and the per-branch re-wrap).
- Renders `slots[state]`; wraps in `mx-auto {maxWidth} p-*` unless `state ∈ bleedStates`.
- View shrinks to: compute view-state union (unchanged) → return `<GameShell ... slots={{…}} />`,
  composing `GameHeader` inside the `playing` slot where it belongs.

Per-game container sizing (current widths to preserve):

| Game | size | className | notes |
|------|------|-----------|-------|
| Rapid Fire | `md` (max-w-lg) | — | error/result/playing all same width |
| Pinpoint | `md` | — | |
| Picture | `lg` (max-w-xl) | — | result = `ResultScreen` (own layout) |
| Four Pics | `md` | — | result own layout |
| Word Hunt | `wide` (max-w-5xl) | `lg:flex-row` | result own layout |
| Crossword | `wide` (max-w-6xl) | `lg:flex-row`, `p-4` | result own layout |
| Wikipedia | custom | bespoke sticky header | shell provides accent only; header stays custom |

Implementation note: result/empty branches that own their width go in `bleedStates` (or
shed their inner container) so width ownership stays consistent.

---

## 6. Component inventory: shared vs game-specific

### Shared / global (`components/game/`, `components/chrome/`)
- `GameHeader` ✅ (built) — marquee plate + progress + right-cluster slot.
- `ScoreReadout` ✅ (built) — score plate, optional accessory.
- `TimerBar` ✅ (exists).
- `GameShell` — planned (§5).
- `InstructionsView` — planned (§4).
- `AppBar` (global chrome) — planned (§2).

### Consolidation candidates (currently duplicated per game)
- **`ScoreIncrementChip`** — duplicated in `crossword/` and `word-hunt/` (identical but for
  the constant). Merge into one shared chip taking an `amount` prop.
- **Timers** — `pinpoint/Stopwatch`, `four-pics/Stopwatch` (elapsed) and `picture/SessionTimer`
  (countdown). Extract a shared `Stopwatch` (count-up) + `SessionTimer` (count-down) into
  `components/game/`.
- **Result screens** — `ResultView` (crossword, word-hunt, four-pics), `ResultScreen`
  (picture), `ResultCard` (rapid-fire), `WikiFinalResults`, `PinpointResultOverlay`. They
  share a pattern (accent top bar + big score plate + per-item list + Back-to-Lobby).
  Candidate: a `GameResultLayout` shell with game-specific innards. **Lower priority**;
  evaluate after the shell lands.

### Game-specific (stay local)
Play surfaces and overlays: `CrosswordGrid`, `LetterGrid`, `QuestionCard`,
`ClueBadgeRow`, `ClueListPanel` (crossword/word-hunt variants), `AnswerOverlay`,
`FeedbackOverlay`, `WikiArticlePane`, `WikiClickBreadcrumb`, `WikiProgressBar`,
`WikiActiveView` (bespoke header). These encode game rules/layout and stay local.

---

## 7. Per-game IA (target arrangement)

All non-wiki games: `GameShell(accent+container+slots)` → `GameHeader(identity + progress +
right-cluster)` in the `playing` slot → play surface → overlays → `result` slot.

| Game | Header right-cluster | Play surface | Result | Notes |
|------|----------------------|--------------|--------|-------|
| Rapid Fire | ScoreReadout | QuestionCard + TimerBar + FeedbackOverlay | ResultCard | states: loading/question/feedback/result/error |
| Pinpoint | ScoreReadout | ClueBadgeRow + guess form + Stopwatch | result overlay/list | |
| Picture | SessionTimer + ScoreReadout | clue image + answer form | ResultScreen | |
| Four Pics | Stopwatch + ScoreReadout | 2×2 image grid + AnswerOverlay | ResultView | |
| Word Hunt | ScoreReadout (+ increment chip) | LetterGrid + ClueListPanel + Submit (in panel) | ResultView | flex-row |
| Crossword | ScoreReadout (+ chip) + Submit | CrosswordGrid + ClueListPanel | ResultView | flex-row |
| Wikipedia | bespoke sticky header (Back + progress bar + clue + breadcrumb + timer/score pills) | WikiArticlePane (diegetic browser) | WikiFinalResults | shell = accent only |

---

## 8. Build sequence (proposed)

- **A. Foundation:** `GameShell`; merge `ScoreIncrementChip`; extract shared `Stopwatch` /
  `SessionTimer`. Stories for each.
- **B. Global chrome + lobby:** `AppBar`, lobby layout wiring, leaderboard links, status-aware
  tile hrefs.
- **C. Instructions:** `GAME_INSTRUCTIONS` registry, `InstructionsView` (+ story), route split
  `/<game>` vs `/<game>/play` for all 7.
- **D. Adopt `GameShell`** across all 7 Views (branches → slots).
- **E. (Optional) Result consistency** pass (`GameResultLayout`).

Each phase keeps the 180-test suite green and ships Storybook stories for new components.

---

## 9. Open questions
- Logout mechanism specifics (auth proxy endpoint / client action).
- Whether result screens should be consolidated now or after the shell (currently deferred to
  Phase E).
- Per-game instructions copy: draft from PRDs, then product review.
