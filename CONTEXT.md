# CONTEXT.md — LEAP Tournament Platform

Domain glossary for the LEAP platform. This file contains **only** canonical term definitions.
No implementation details, no specs, no scratch-pad notes.

---

## Terms

### Player
A pre-seeded participant in the LEAP tournament. Identified by `corp_id`. Players cannot self-register — accounts exist at startup.

### Event Code
A shared secret distributed to all players before the event. Combined with `corp_id` to authenticate.

### Session Token
A JWT issued by the backend on successful login. Stored as an `httpOnly` cookie on the browser by the Next.js login Route Handler. Never stored in `localStorage` or `sessionStorage`. FastAPI reads it via `Authorization: Bearer`; the proxy injects this header from the cookie on every forwarded request.

### Lobby
The main screen after login. Displays five Game Tiles and a Mini Leaderboard sidebar. The player's per-game completion state is fetched server-side via `GET /players/me/sessions`.

### Game Tile
A card on the Lobby representing one mini-game. Shows the game name, description, points available, and status: `not_started`, `in_progress`, or `completed`/`abandoned`. A completed or abandoned tile is locked — no re-entry.

### Game Session
A server-side record created when a player starts a game. Keyed on `(player_id, game_id)` — one session per player per game. Statuses: `active`, `completed`, `abandoned`. The `started_at` timestamp is the server-side source of truth for elapsed time.

### Rapid Fire
A 15-question MCQ quiz. Questions are served one at a time; each has its own `time_limit_ms`. The player selects one of four options or their timer expires (treated as a skip). Scoring: 50–100 pts per correct answer based on speed; 0 pts for wrong or skipped.

### Wikipedia Speed Run
A navigation game where the player works through all 5 Wiki Puzzles in a fixed order. Max score: 1000 pts (200 per puzzle).

### Wiki Puzzle
One start-to-target Wikipedia navigation challenge. The player is shown a Puzzle Clue (a riddle describing the target page) and the start page. They navigate by clicking internal Wikipedia links to reach the target. Each puzzle has a configurable `time_limit_ms`; the timer starts immediately when the clue is shown. Scoring: steps score (max 125) + time bonus (max 75) = max 200 per puzzle. Timeout scores 0.

### Puzzle Clue
The riddle shown to the player at the start of each Wiki Puzzle. Describes the target page without revealing its title. The player must deduce the target and navigate to it. Stored as the `clue` field on a Wiki Round.

### Wiki Round
A seed-data record defining one Wiki Puzzle: start page, target page, clue text, `optimal_click_count`, and `time_limit_ms`. All 5 rounds are played by every player in a fixed seed order.

### Wiki Puzzle Attempt
A server-side record of one player's attempt at one Wiki Round within their Wikipedia Speed Run Game Session. Tracks the full `click_path` (all page titles visited, including the start page and any backtracking), `steps_taken` (total clicks, where back counts as a step), `started_at`, `time_ms` on completion, and per-puzzle `score`. Statuses: `active`, `completed`, `timed_out`.

### Navigation Step
A single deliberate page visit within a Wiki Puzzle Attempt. Recorded server-side. Includes forward link clicks and back-button presses (when the back button is enabled). Redirect pages count as 1 step. The step count equals `len(click_path) − 1` (start page is not a step).

### Wiki Back Button
An optional in-game "← Back" button that navigates the player to the previous page in their click path. Counts as one Navigation Step. Controlled by a configurable feature flag; browser back is intercepted by the Navigation Guard regardless.

### Question Timer
A per-question countdown rendered by the client, starting from the question's `time_limit_ms`. Starts after a configurable get-ready delay. Resets to full `time_limit_ms` on page refresh (server has no per-question start timestamp). When it reaches zero, the client auto-submits with `selected_option: null`.

### Feedback Phase
The ~1.5s window after an answer is submitted. The client shows whether the answer was correct, highlights the correct option, and displays the running score. Auto-advances to the next question. Duration and get-ready delay are configurable constants.

### Answer Submission
A `POST /games/rapid-fire/answer` call with `{ question_id, selected_option, time_ms }`. `selected_option` is `null` when the timer expired (treated as skipped server-side). `time_ms` is client-measured and clamped by the server.

### Abandon
The act of forfeiting a game mid-session. Triggered only by the navigation guard — there is no explicit "abandon" button. Calls `POST /games/rapid-fire/abandon`, records a partial score, and redirects to the Lobby. Players cannot re-enter an abandoned game.

### Navigation Guard
A browser-level trap that intercepts back navigation and page unload while a game is in progress. Implemented via `pushState` + `popstate` + `beforeunload`. Arms when the game session starts (`setIsDirty(true)`), disarms on completion or confirmed abandon (`setIsDirty(false)`).

### Result Screen
The inline view shown after a game completes (or is abandoned). Replaces the question UI on the same page. Shows `score`, `correct_count`, `wrong_count`, `skipped_count`, `time_taken_seconds`. Includes a "Back to Lobby" button.

### Mini Leaderboard
A sidebar on the Lobby showing the top 10 players by total score, plus the current player pinned at the bottom if outside the top 10. Polls every 5 seconds via React Query `refetchInterval`.

### Full Leaderboard
A dedicated `/leaderboard` page showing all players ranked by total score with a tiebreaker of earliest completion time. Same 5s polling interval.

### Proxy Route Handler
The Next.js catch-all Route Handler at `app/api/[...path]/route.ts`. Reads the `token` httpOnly cookie, injects `Authorization: Bearer <token>`, and forwards the request to FastAPI. Owns the entire auth seam on the frontend — FastAPI is unchanged.

### Auth Guard (proxy.ts)
Next.js 16 `proxy.ts` at the project root. Reads the `token` cookie; redirects unauthenticated requests to `/login`. Protected routes: all routes except `/(auth)/login` and static assets.
