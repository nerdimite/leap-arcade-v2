# PRD: Wikipedia Speed Run

**Date:** 2026-05-17  
**Status:** Ready for implementation

---

## Problem Statement

The LEAP platform needs a second playable mini-game after Rapid Fire: Wikipedia Speed Run. The game is trickier than Rapid Fire because it combines normal game-session lifecycle rules with external Wikipedia content, server-side HTML rewriting, route-safe navigation, timing, scoring, and deterministic tests that still exercise realistic Wikipedia markup.

Players must be able to solve 5 fixed Wiki Puzzles, each starting from a Wikipedia page and asking them to infer the hidden target from a Puzzle Clue. The app must let them navigate only through rewritten internal Wikipedia links, record each Navigation Step server-side, score each puzzle by click efficiency and speed, and aggregate the result into the shared leaderboard.

## Solution

Build Wikipedia Speed Run as a first-class backend + frontend game using the same overall layering as Rapid Fire:

1. Store seed content in `wiki_rounds`.
2. Track one `game_sessions` row per player for the overall game.
3. Track one `wiki_puzzle_attempts` row per player per Wiki Round.
4. Fetch Wikipedia article HTML through the Wikimedia REST API.
5. Rewrite article links so each internal article click posts back to the backend before rendering the next article.
6. Keep timers server-authoritative for wiki puzzle attempts, per ADR-0004.
7. Render the frontend as a split-panel game screen with fixed game UI and scrollable Wikipedia content.
8. Test the happy path with realistic captured Wikimedia HTML fixtures served by `respx`.

## User Stories

1. As a player, I want to start Wikipedia Speed Run from the Lobby, so that I can play the next mini-game after Rapid Fire.
2. As a player, I want to play all 5 Wiki Puzzles in a fixed order, so that my score is comparable with everyone else's score.
3. As a player, I want each puzzle to show a riddle-like Puzzle Clue instead of the target page title, so that I must infer what page I am trying to reach.
4. As a player, I want the start page to load as a familiar Wikipedia-style article, so that the game feels like a real Wikipedia speedrun.
5. As a player, I want the clue, timer, current puzzle number, step count, and back button to remain visible while I scroll the article, so that I always know the game context.
6. As a player, I want the game to show "Puzzle N of 5", so that I can pace myself through the run.
7. As a player, I want to see a breadcrumb of my click path, so that I can remember where I have been and avoid loops.
8. As a player, I want each internal Wikipedia article link click to navigate to the next page, so that normal Wikipedia exploration is the core interaction.
9. As a player, I want external links, file links, edit links, citation links, and search/navigation chrome to be unavailable, so that the game stays inside the intended Wikipedia article graph.
10. As a player, I want browser Ctrl+F / Cmd+F to work inside the rendered article, so that I can use normal browser find behaviour if I choose.
11. As a player, I want redirect pages to count as only one click, so that I am not penalized for Wikipedia implementation details.
12. As a player, I want the optional in-game back button to take me to the previous page and count as a step, so that I can recover from a bad click without using browser history.
13. As a player, I want the browser back button to be intercepted by the existing Navigation Guard, so that I do not accidentally abandon or desynchronize the game.
14. As a player, I want each puzzle timer to start immediately when the clue and article load, so that the speedrun starts as soon as the puzzle appears.
15. As a player, I want each puzzle to have a configurable time limit, initially 3 minutes, so that the game remains fast enough for a one-day event.
16. As a player, I want a timeout to score 0 for that puzzle and advance me to the next puzzle, so that one failed puzzle does not end my whole game.
17. As a player, I want a short result screen after each puzzle, so that I can see my steps, time, score, and then deliberately continue.
18. As a player, I want the timer for the next puzzle to start only when the next puzzle screen loads, so that the between-puzzle result screen does not consume puzzle time.
19. As a player, I want the final result screen to show total score and all 5 per-puzzle results, so that I can understand how I performed.
20. As a player, I want the final result screen to reveal each target title after the game ends, so that I get closure on the riddles.
21. As a player, I want completed or abandoned Wikipedia Speed Run sessions to lock the Lobby tile, so that the one-session-per-game rule is consistent with Rapid Fire.
22. As a player, I want an active session to resume after refresh with the correct current page and remaining time, so that I can recover from accidental refresh without gaining extra time.
23. As an event organiser, I want all 5 Wiki Rounds to come from seed data, so that event content can be reviewed and changed before the event.
24. As an event organiser, I want each Wiki Round to store one reference solution path and an optimal click count, so that scoring and post-game review have a baseline.
25. As an event organiser, I want the score to reward near-optimal paths gently and inefficient paths more harshly, so that players are rewarded for getting close without a brutal first-step penalty.
26. As an event organiser, I want speed to add bonus points without overpowering click efficiency, so that both quick thinking and good navigation matter.
27. As a developer, I want Wikipedia content fetching isolated behind a client module, so that external API handling is testable and replaceable.
28. As a developer, I want HTML rewriting isolated behind a pure transformation module, so that link policy and sanitization can be tested without a database.
29. As a developer, I want API e2e tests to use captured real Wikimedia fixtures, so that the happy path exercises realistic markup without relying on live network access.
30. As a developer, I want the wiki backend to follow the route → service → DAO → model pattern already used by Rapid Fire, so that implementation agents can move predictably through the call graph.

## Implementation Decisions

### Domain terminology

- Use **Puzzle Clue**, not hint. The current `docs/wiki.json` field named `hint` should become `clue` in backend seed data and API responses.
- Use **Wiki Round** for the seeded puzzle definition.
- Use **Wiki Puzzle Attempt** for one player's attempt at one Wiki Round.
- Use **Navigation Step** for a deliberate forward link click or in-game back action. The start page is not a step.

### Gameplay rules

- Every player plays all 5 Wiki Rounds in fixed seed order.
- Each Wiki Round has a configurable `time_limit_ms`; initial value is `180000`.
- The puzzle timer starts immediately when the clue and start article are returned to the player.
- Timeout scores 0 for the current puzzle and advances to the next puzzle.
- Redirects count as 1 Navigation Step.
- Browser back is intercepted by the Navigation Guard.
- The optional in-game back button is controlled by a configurable feature flag and counts as 1 Navigation Step.
- Between puzzles, show a per-puzzle result screen with a deliberate "Next Puzzle" action.
- The final result screen reveals target titles and per-puzzle breakdowns, but not necessarily the full solution paths.

### Scoring

Maximum score is 200 per puzzle and 1000 total.

```text
if timed_out:
    puzzle_score = 0
elif clicks_taken <= optimal_click_count:
    steps_score = 125
else:
    steps_score = max(125 - 2 * (clicks_taken - optimal_click_count)^2, 12)

time_bonus = floor(75 * (1 - time_ms / time_limit_ms))
puzzle_score = steps_score + time_bonus
```

- `clicks_taken` excludes the start page.
- `time_ms` is computed server-side from `wiki_puzzle_attempts.started_at`.
- The client does not send `time_ms` for scoring.
- Time bonus is clamped to the range `0..75`.
- Timeout always scores 0, even if the player had navigated close to the target.

### Database model

The existing `game_sessions` table remains the score ledger for the overall game. It already supports `game_id = 'wiki'`.

Add `wiki_rounds` as the seeded content table:

```sql
CREATE TABLE wiki_rounds (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    sequence_index INTEGER NOT NULL,
    start_title TEXT NOT NULL,
    start_url TEXT NOT NULL,
    target_title TEXT NOT NULL,
    target_url TEXT NOT NULL,
    clue TEXT NOT NULL,
    optimal_click_count INTEGER NOT NULL,
    solution_path TEXT[] NOT NULL DEFAULT '{}',
    time_limit_ms INTEGER NOT NULL DEFAULT 180000,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE (sequence_index),
    CHECK (sequence_index >= 1),
    CHECK (optimal_click_count >= 1),
    CHECK (time_limit_ms > 0)
);
```

Add `wiki_puzzle_attempts` as the per-player, per-round gameplay table:

```sql
CREATE TABLE wiki_puzzle_attempts (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    game_session_id TEXT NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,
    round_id TEXT NOT NULL REFERENCES wiki_rounds(id),
    status TEXT NOT NULL DEFAULT 'active',
    current_title TEXT NOT NULL,
    click_path TEXT[] NOT NULL DEFAULT '{}',
    steps_taken INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    time_ms INTEGER,
    score INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE (game_session_id, round_id),
    CHECK (status IN ('active', 'completed', 'timed_out')),
    CHECK (steps_taken >= 0),
    CHECK (score IS NULL OR score >= 0),
    CHECK (time_ms IS NULL OR time_ms >= 0)
);
```

Do not implement the older `wiki_sessions` design from the backend technical design. The single-puzzle `wiki_sessions` table no longer fits the resolved 5-puzzle game model.

### Seed data

- Move the resolved puzzle content into backend seed data alongside `players.json` and `rapid_fire.json`.
- Rename `hint` to `clue` during this move.
- Add or derive `time_limit_ms = 180000` for every seeded round unless overridden.
- Preserve `solution_path` for post-game reference, fixture generation, and organiser review.
- Seed loader must be idempotent and safe to re-run on startup.
- Seed order is the `sequence_index`; do not randomize per player.

Reference seed shape:

```json
{
  "sequenceIndex": 1,
  "start": "Biology",
  "startLink": "https://en.wikipedia.org/wiki/Biology",
  "clue": "I let the model peek around, to find which words truly count — what am I?",
  "end": "Attention",
  "endLink": "https://en.wikipedia.org/wiki/Attention_(machine_learning)",
  "optimalClickCount": 3,
  "timeLimitMs": 180000,
  "solutionPath": [
    "Biology",
    "Biology in fiction",
    "Intelligent machine (redirects to Artificial intelligence)",
    "Attention (machine learning)"
  ]
}
```

### Backend call stack

Follow the same layering rules as Rapid Fire:

```text
FastAPI route
  -> API schema
  -> WikiSpeedRunService
  -> DAOs for game_sessions, wiki_rounds, wiki_puzzle_attempts
  -> WikipediaClient for external article HTML
  -> WikiHtmlRewriter for pure HTML transformation
  -> internal DTOs in leap/types
```

Services own sessions:

```text
async with self.ctx.session() as session:
    ...
```

DAOs take `AsyncSession` as their first argument and return typed Pydantic DTOs, not plain dicts.

### Deep modules

Build these as deep modules with small stable interfaces:

- **WikipediaClient** — fetches article HTML from the Wikimedia REST API, follows redirects, and returns canonicalized article data.
- **WikiHtmlRewriter** — transforms raw Wikimedia REST HTML into game-safe article HTML and link metadata. This is pure and should be heavily unit-tested.
- **WikiScoring** — computes step score, time bonus, puzzle score, timeout score, and aggregate score.
- **WikiSpeedRunService** — owns game lifecycle orchestration, attempts, completion, timeout, abandon, and resume.

### Internal DTO shapes

Use internal Pydantic DTOs under `leap/types/`, shared between DAOs and services.

```python
class WikiRoundDTO(BaseLeapModel):
    id: str
    sequence_index: int
    start_title: str
    start_url: str
    target_title: str
    target_url: str
    clue: str
    optimal_click_count: int
    solution_path: List[str]
    time_limit_ms: int


class WikiPuzzleAttemptStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    TIMED_OUT = "timed_out"


class WikiPuzzleAttemptDTO(BaseLeapModel):
    id: str
    game_session_id: str
    round_id: str
    status: WikiPuzzleAttemptStatus
    current_title: str
    click_path: List[str]
    steps_taken: int
    started_at: datetime
    completed_at: Optional[datetime]
    time_ms: Optional[int]
    score: Optional[int]


class WikiArticleDTO(BaseLeapModel):
    requested_title: str
    canonical_title: str
    html: str


class WikiPuzzleResultDTO(BaseLeapModel):
    round_id: str
    puzzle_index: int
    clue: str
    target_title: str
    optimal_click_count: int
    steps_taken: int
    time_ms: Optional[int]
    score: int
    status: WikiPuzzleAttemptStatus


class WikiActivePuzzleDTO(BaseLeapModel):
    game_session_id: str
    attempt_id: str
    round_id: str
    puzzle_index: int
    puzzle_count: int
    clue: str
    current_title: str
    time_limit_ms: int
    time_remaining_ms: int
    steps_taken: int
    click_path: List[str]
    article_html: str
    back_enabled: bool
```

### API routes

Mount under `/games/wiki`.

#### `POST /games/wiki/play`

Starts or resumes the overall Wikipedia Speed Run game.

Responsibilities:

- Create `game_sessions(game_id='wiki')` if missing.
- Return completed/abandoned result if the session is terminal.
- Create the first active `wiki_puzzle_attempt` if this is a new session.
- On resume, compute server-authoritative remaining time from `started_at`.
- If an active attempt has expired, mark it `timed_out`, score 0, and advance until an active puzzle or final result exists.
- Fetch and rewrite the current article HTML.

Response shape:

```ts
type WikiPlayResponse =
  | {
      state: "active"
      totalScore: number
      completedCount: number
      current: WikiActivePuzzle
      completedAttempts: WikiPuzzleResult[]
    }
  | {
      state: "completed" | "abandoned"
      totalScore: number
      results: WikiPuzzleResult[]
    }
```

#### `POST /games/wiki/navigate`

Records a forward Navigation Step and returns the next article or per-puzzle result.

Request:

```ts
type WikiNavigateRequest = {
  title: string
}
```

Responsibilities:

- Reject terminal sessions and non-active attempts.
- Reject or ignore navigation when the server-side timer has expired; return timeout/advance state instead.
- Fetch the requested title from Wikimedia, following redirects.
- Count the click as exactly 1 step even if Wikimedia redirects.
- Append the canonical landed title to `click_path`.
- Set `current_title` to the canonical landed title.
- If the canonical landed title matches the target title, complete the attempt, compute score, and return a per-puzzle result.
- If this was the fifth puzzle, complete the overall `game_sessions` row with the total score.

Response shape:

```ts
type WikiNavigateResponse =
  | {
      state: "active"
      current: WikiActivePuzzle
    }
  | {
      state: "puzzle_completed"
      puzzleResult: WikiPuzzleResult
      nextPuzzleAvailable: boolean
      totalScore: number
    }
  | {
      state: "completed"
      totalScore: number
      results: WikiPuzzleResult[]
    }
```

#### `POST /games/wiki/back`

Records an in-game back action when the feature flag is enabled.

Responsibilities:

- Reject if back is disabled.
- Reject if the current attempt has fewer than 2 entries in `click_path`.
- Count the action as 1 step.
- Set `current_title` to the previous page in the path.
- Preserve the full path including backtracking rather than deleting history, so scoring reflects all deliberate moves.
- Return rewritten HTML for the new current page.

#### `POST /games/wiki/timeout`

Lets the client report that its visible countdown reached zero. The server remains authoritative.

Responsibilities:

- If the server timer has actually expired, mark the current attempt `timed_out`, score 0, and advance.
- If the server timer has not expired, return the current active puzzle state with corrected `time_remaining_ms`.
- Complete the overall game if the fifth puzzle timed out.

#### `POST /games/wiki/abandon`

Abandons the overall game via the Navigation Guard.

Responsibilities:

- Mark the active `game_sessions` row `abandoned`.
- Preserve completed puzzle scores.
- Score active and untouched puzzles as 0 for final display.
- Return a final result shape.
- Lobby tile is locked after abandon, consistent with existing Game Session rules.

### Wikipedia content fetching

Use Wikimedia REST API article HTML:

```text
GET https://en.wikipedia.org/api/rest_v1/page/html/{title}
```

Decisions:

- Use a descriptive User-Agent.
- Follow redirects.
- Treat redirects as a single Navigation Step.
- Cache fetched and rewritten article HTML in memory by canonical title for the event lifetime.
- Prewarm start pages from the seeded rounds if cheap.
- Do not persist HTML in the database for this build.
- Images may load from Wikimedia CDN directly.
- Do not proxy or allow external article navigation.

### HTML rewriting policy

The REST API already avoids the normal Wikipedia search box and chrome. The rewriter still owns link policy.

Policy:

- Internal article links (`/wiki/...`) become clickable game links with `data-wiki-title`.
- Internal article link clicks are intercepted by the frontend and sent through `POST /games/wiki/navigate`.
- Section anchors may remain scroll-only when they point within the same article; cross-page anchors are normalized to the destination page title and the anchor is ignored.
- External links become plain text.
- Red links, edit links, special pages, talk pages, category pages, citation jumps, and file links become plain text.
- Image `src` attributes may remain if they point to trusted Wikimedia hosts.
- Scripts and event handler attributes are removed.
- The frontend renders the result inside a scoped article container using Wikipedia-like styling.

The rewriter should return enough metadata to make tests easy:

```python
class RewrittenWikiHtmlDTO(BaseLeapModel):
    html: str
    internal_link_titles: List[str]
    removed_link_count: int
```

### Frontend UX

Use a split-panel page:

- Fixed game header at the top.
- Header contains Puzzle Clue, "Puzzle N of 5", countdown timer, steps taken, score so far, and optional back button.
- A compact 5-step progress indicator shows completed, active, and remaining puzzles.
- A scrollable click-path breadcrumb sits below the header.
- The article content scrolls below the game header.
- While navigation is loading, dim the article content and show an overlay spinner; header remains visible and timer keeps ticking.
- Ctrl+F / Cmd+F is allowed and should work because the rewritten HTML is rendered into the DOM.
- On puzzle completion, replace the article with a puzzle result card and a "Next Puzzle" button.
- On final completion, show total score and 5 puzzle breakdown cards with target-title reveal.

### Frontend response handling

The wiki page should model game state explicitly:

```ts
type WikiClientState =
  | { kind: "loading" }
  | { kind: "active"; data: WikiActivePuzzle; totalScore: number; completedAttempts: WikiPuzzleResult[] }
  | { kind: "puzzleResult"; result: WikiPuzzleResult; totalScore: number; nextPuzzleAvailable: boolean }
  | { kind: "complete"; totalScore: number; results: WikiPuzzleResult[] }
  | { kind: "error"; message: string }
```

This mirrors Rapid Fire's reducer-driven client style, but the wiki state machine should account for server-authoritative timeout correction and article loading.

### Leaderboard and lobby integration

- `game_sessions.score` stores the final total score for Wikipedia Speed Run.
- `game_sessions.status='completed'` counts toward leaderboard aggregation.
- `game_sessions.status='abandoned'` locks the Lobby tile and may show score according to the existing session-summary behaviour.
- `GET /players/me/sessions` should need no special case beyond the new `wiki` score/status.
- `GET /lobby` should display Wikipedia Speed Run using the existing `GAMES` registry data.

## Testing Decisions

### What makes a good test

- Test observable behaviour through stable interfaces.
- Unit-test pure scoring and HTML rewriting exhaustively.
- Service tests should use hand-written fakes, not `MagicMock`, for DAOs and the Wikipedia client.
- API e2e tests should assert user-journey outcomes through HTTP: statuses, response states, score, step count, timer behaviour, and DB-backed lifecycle transitions.
- Do not assert private helper calls, ORM internals, or exact HTML formatting beyond policy-relevant markers.

### Unit tests

Test `WikiScoring`:

- Optimal click count yields full steps score.
- A few extra clicks are only lightly penalized.
- Inefficient paths eventually hit the floor.
- Time bonus is max at 0 ms and 0 at/after `time_limit_ms`.
- Timeout always scores 0.
- Total score aggregates exactly 5 puzzle results.

Test `WikiHtmlRewriter` with real captured Wikimedia HTML fixtures:

- Internal article links become game-controlled links.
- External links are disabled.
- File, edit, special, category, citation, and red links are disabled.
- Scripts and unsafe attributes are removed.
- Images from trusted Wikimedia hosts remain renderable.
- Redirect/canonical title metadata is preserved outside the rewriter by the Wikipedia client.

Test `WikipediaClient`:

- Encodes titles safely.
- Follows redirects.
- Returns requested and canonical titles.
- Uses cache on repeated fetches.
- Surfaces upstream failures as service exceptions, not raw HTTP errors.

### Service tests

Test `WikiSpeedRunService` with hand-written fakes:

- `play` creates a `game_sessions` row and first attempt.
- `play` resumes the active attempt and returns server-authoritative remaining time.
- `play` auto-times-out stale attempts and advances.
- `navigate` increments steps and appends canonical titles.
- Redirect navigation counts as 1 step.
- Target detection completes the puzzle and computes score.
- Fifth puzzle completion marks the overall game session completed.
- `timeout` scores 0 and advances when server elapsed time has expired.
- `timeout` returns corrected active state when the client fires early.
- `back` counts as a step and changes current page only when enabled.
- `abandon` marks the game session abandoned and returns final display data.

### DAO tests

DAO methods that execute real SQL should be covered by the existing e2e/integration path, not mocked SQLAlchemy result objects. If DAO unit tests are added before integration scaffolding is complete, mark them with TODOs for integration test coverage.

### API e2e tests

Use `respx` to serve captured real Wikimedia REST HTML fixtures. Do not call live Wikipedia in normal test runs.

Fixtures should cover at least the optimal path for the first Wiki Round:

```text
Biology
Biology in fiction
Artificial intelligence
Attention (machine learning)
```

Additional fixtures should cover start pages and reference solution paths for all 5 rounds when the full happy path is implemented.

E2E journeys:

- Login → play → receive first puzzle and rewritten Biology HTML.
- Navigate along the first round's optimal path from `docs/wiki.json`.
- Assert each navigate call increments `steps_taken` by 1.
- Assert rewritten HTML contains game-controlled internal links and does not expose external navigation.
- Assert completing the target returns `state='puzzle_completed'`, `steps_taken=3`, and a valid score.
- Continue through all 5 fixture-backed optimal paths for a full-game happy path when fixtures exist.
- Assert final `game_sessions.status='completed'`, final score is written, and leaderboard includes the player.
- Resume mid-puzzle and assert remaining time is reduced according to server time, not reset.
- Timeout a puzzle and assert 0 score + next puzzle state.
- Abandon mid-game and assert the Lobby tile locks.

### Frontend tests

- Test the API client functions for `play`, `navigate`, `back`, `timeout`, and `abandon`.
- Test the wiki reducer/state machine if implemented.
- Test click interception on rewritten article links.
- Test loading overlay behaviour during navigation.
- Test timer initialization from `time_remaining_ms`.
- Test per-puzzle result and final result rendering.
- Test Navigation Guard integration for abandon.

## Out of Scope

- Randomizing Wiki Round order per player.
- Live calls to Wikipedia during CI or normal e2e runs.
- Persisting the Wikipedia HTML cache in PostgreSQL.
- Building a general-purpose web proxy.
- Allowing Wikipedia search, external links, file pages, talk pages, edit pages, or special pages.
- Blocking Ctrl+F / Cmd+F.
- Showing full solution paths during active gameplay.
- Implementing Picture Illustration, Four Pics One Lie, or Crossword.
- Browser-level Playwright tests for this PRD; the required e2e scope is API-level with realistic HTML fixtures.
- Load testing Wikimedia or the wiki proxy.

## Further Notes

- ADR-0004 explains why wiki puzzle timers are stricter than Rapid Fire timers on refresh.
- The older backend technical design described a single active `wiki_sessions` model. This PRD supersedes that shape with `wiki_puzzle_attempts` because every player now plays all 5 Wiki Rounds.
- `docs/wiki.json` is the current design artifact, but implementation should move this into backend seed data and rename `hint` to `clue`.
- In-memory article caching is acceptable for the one-day event. A restart loses the cache but not game state; pages are refetched on demand.
- The link rewriter is security-sensitive enough to be treated as a deep module with focused tests.
- The project does not currently define an external issue tracker configuration in-repo. If this PRD is later split into markdown issues, mirror the existing `docs/issues/<feature>/parent.md` convention and mark the parent as ready for agent work.
