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

### Picture Illustration
A rebus-puzzle game where the player decodes tech/corporate concepts from visual images. All seeded Picture Puzzles are played in a single session under one global Session Timer. Max score: 1300 pts (5 puzzles × 200 pts + 300 pts time bonus).

### Picture Puzzle
A seed-data record encoding one concept as a visual image. Consists of an image (stored as a static frontend asset) and a list of accepted answers. The player types a free-text answer; the service normalises both sides (lowercase, punctuation removed, whitespace collapsed) before matching against the accepted answer list. All word variations that should be accepted (e.g. "nlp", "natural language processing") must be listed explicitly in the seed.

### Picture Puzzle Attempt
A server-side record of one answer submission within a Picture Illustration Game Session. One row is written per submit — including wrong attempts. Tracks `submitted_answer` (null = skip), `correct`, and `skipped`. Multiple attempts can exist per puzzle per session; the attempt count at the moment of a correct answer or skip determines the per-puzzle score.

### Session Timer
The global countdown that runs for the entire Picture Illustration Game Session, starting at `session.started_at`. Configured via `PICTURE_TIME_LIMIT_MS` (default: 300 000 ms). When the timer reaches zero, the client calls `POST /games/picture/abandon`, which ends the session immediately — remaining unsolved puzzles score 0. Time remaining at game end contributes a time bonus (1 pt per second remaining) to the final score.

### Picture Session Score
The final score for a Picture Illustration session. Computed as: sum of per-puzzle scores (200 pts for 1st-attempt correct, 150 for 2nd, 100 for 3rd, 50 for 4th+, 0 for skipped or not-reached) plus a time bonus of 1 pt per second remaining on the Session Timer at game end.

### Word Hunt
A riddle-driven word-search game. The player sees a single Letter Grid and a panel of Riddle Cards. Each riddle's answer is a Hidden Word lying along a straight line in the grid in any of the eight directions (horizontal, vertical, both diagonals, forwards or reverse). The player drags across cells to perform a Word Trace; the server derives the traced letters from the cells and credits a Find if the string matches an unsolved Hidden Word. Scoring: 100 pts per word found + a session-wide time bonus (max 500, decays to 0 over 10 minutes). The game ends when all words are found, when the player presses Submit, or when the navigation guard fires — all three paths score identically. Internal `game_id`: `word_hunt`.

### Letter Grid
The seeded rectangular board of single uppercase letters that hosts the Hidden Words. Dimensions (`rows`, `cols`) come from the seed; the same grid is shown to every player.

### Hidden Word
A seeded word placed in the Letter Grid along one of eight straight directions. Each Hidden Word has an associated Riddle Card whose clue text points to it. The server stores the seeded start/end cell coordinates and validates them against the grid at startup.

### Riddle Card
A card in the Word Hunt clue panel. Shows the riddle while the corresponding Hidden Word is unfound. On a successful Find it flips to reveal the answer word with a checkmark. The card never reveals the answer of an unfound word — neither on-screen nor in the API response.

### Word Trace
A player drag across grid cells, reported to the server as a `{start_row, start_col, end_row, end_col}` quad. The server validates the trace is a straight line in one of the eight directions, walks the cells, and compares the resulting string to the unsolved Hidden Words.

### Find
A server-side record of one player successfully tracing a Hidden Word. Stores the actual traced coordinates (which may differ from the seeded coordinates when the answer string appears in multiple grid locations). At most one Find per `(session, Hidden Word)`.

### Word Hunt Result
The end-of-game screen for Word Hunt. Shows total score broken into `base_score` (100 × found_count) and `time_bonus`, the found-count over total, and a list of the Hidden Words the player found with their clues. Unfound words are deliberately omitted to prevent answer leaks during the event.

### Crossword
A classic intersecting-word puzzle. The player fills a blank grid of open cells with letters typed from the keyboard; each open cell belongs to one Across and/or one Down Crossword Entry. An entry auto-checks the moment all its cells are filled: a correct entry locks green and scores, a wrong one flashes red and stays editable (typed letters are kept, locked crossing letters untouched). Scoring: 100 pts per solved entry + a session-wide time bonus (max 500, decaying linearly to 0 over 10 minutes). The grid starts fully blank — no letters are pre-revealed — and answers never leave the server. The game ends when all entries are solved, when the player presses Submit, or when the Navigation Guard fires — all three paths score identically. Internal `game_id`: `crossword`.

### Crossword Grid
The seeded rectangular board hosting the Crossword Entries. The seed stores the full solution as a matrix of uppercase letters with `null` for blocked cells; this matrix is the server-side source of truth and is validated at startup against every entry. The client receives only a blank skeleton — which cells are open and the corner number of each entry start — never the solution letters.

### Crossword Entry
One Across or Down word in the Crossword Grid. Defined in the seed by its number, direction (`across` / `down`), start cell, answer, and clue. Open cells are shared between a crossing Across and Down entry; a shared cell's letter must agree across both, validated at startup. The answer text of an unsolved entry is never sent to the client.

### Crossword Solve
A server-side record of one player correctly completing one Crossword Entry within their Crossword Game Session. At most one per `(session, entry)`. On a mid-game refresh, solved entries are re-hydrated with their answer letters and lock green; all unsolved cells return blank (in-progress tentative letters are not persisted).

### Crossword Result
The end-of-game screen for Crossword. Shows total score split into `base_score` (100 × solved_count) and `time_bonus`, the solved-count over total, and the list of entries the player solved with their clues and answers. Unsolved entries are deliberately omitted to prevent answer leaks during the event.

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

### Pinpoint
A word-association game where the player guesses the hidden category that links a set of clue words. The player sees one clue at a time; each wrong guess reveals the next clue. Maximum 5 clues per puzzle. The player works through every seeded puzzle in a random order per session. Score per puzzle: base score (500 / 400 / 300 / 200 / 100 for 1–5 clues used) plus a time bonus that decays linearly from 100 to 0 over 90 seconds. No negative points. Answer is never revealed to the player, even on failure.

### Pinpoint Puzzle
A single seed-data record defining one Pinpoint round: an `answer`, a list of `answer_aliases` (all acceptable phrasings, normalised to lowercase and trimmed on comparison), and exactly 5 ordered clue words (`clue1`–`clue5`). All seeded puzzles are played by every player in every session.

### Pinpoint Puzzle Attempt
A server-side record of one player's attempt at one Pinpoint Puzzle within their Pinpoint Game Session. Tracks `clues_revealed` (1–5, incremented on each wrong guess), `guesses` (JSONB array of all wrong guess texts), `status` (`active` / `solved` / `failed`), `score` (null until terminal), `started_at` (set when the puzzle is first served), and `completed_at`. Statuses transition: `active` → `solved` on a correct guess; `active` → `failed` when the 5th guess is wrong.

### Clue Reveal
The mechanic by which a wrong guess advances the puzzle state: one wrong guess unconditionally increments `clues_revealed` by 1 and exposes the next clue word. A player can never make two guesses while still on the same clue — wrong guess and clue reveal are a single atomic step. The player has at most 5 total guesses per puzzle.

### Pinpoint Time Bonus
A per-puzzle bonus computed from the elapsed time between `puzzle_started_at` and the correct guess: `max(0, floor(100 × (1 − elapsed_ms / 90_000)))`. Reaches 0 at 90 seconds. The stopwatch runs indefinitely with no hard timeout; a player who takes longer than 90 seconds still earns their base clue score.

### Proxy Route Handler
The Next.js catch-all Route Handler at `app/api/[...path]/route.ts`. Reads the `token` httpOnly cookie, injects `Authorization: Bearer <token>`, and forwards the request to FastAPI. Owns the entire auth seam on the frontend — FastAPI is unchanged.

### Four Pics Question
A single seed-data record defining one Four Pics round: exactly four static image paths in a JSONB array and one server-side `odd_one_out_index` (0–3). The odd image is never sent to the client.

### Four Pics Question Attempt
A server-side record of one question served within a Four Pics game session. Created when the question is first shown with `status = active` and a server-authoritative `started_at`. Transitions to `correct` or `wrong` on the player's single tap; both are terminal.

### Auth Guard (proxy.ts)
Next.js 16 `proxy.ts` at the project root. Reads the `token` cookie; redirects unauthenticated requests to `/login`. Protected routes: all routes except `/(auth)/login` and static assets.
