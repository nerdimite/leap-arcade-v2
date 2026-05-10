# Data Model – Running Notes

Informal capture; not a design spec. Started 2026-05-10.

Scoped to the two games we're building first: **Wikipedia Speed Run** and **Rapid Fire Quiz**.
The shape is designed to extend cleanly to the remaining three games later.

---

## Auth

- Players are pre-seeded by corp ID before the event. No self-registration.
- Login: `corp_id` (case-insensitive, normalised to lowercase) + shared event code.
- Event code hash lives in an **env var** (`EVENT_CODE_HASH`), not in the DB. No per-player credential row needed.
- JWT payload carries the normalised `corp_id`. All downstream queries use that.

---

## Table Design

### `players`
Pure profile table. No auth concerns.

| column | type | notes |
|---|---|---|
| `id` | text PK | normalised corp_id (lowercase) |
| `display_name` | text | |
| `created_at` | timestamptz | |

### `game_sessions`
Score ledger. One row per player per game. The leaderboard aggregates this.

| column | type | notes |
|---|---|---|
| `id` | text PK | uuid |
| `player_id` | text FK → players | |
| `game_id` | text | enum: `'wiki'`, `'rapid_fire'`, ... |
| `status` | text | `'active'` \| `'completed'` \| `'abandoned'` |
| `score` | int | nullable until completed |
| `started_at` | timestamptz | server-written |
| `completed_at` | timestamptz | nullable |

Constraint: `UNIQUE (player_id, game_id)` — one session per player per game, ever.

Leaderboard query:
```sql
SELECT player_id, SUM(score) AS total, COUNT(*) AS games_completed
FROM game_sessions
WHERE status = 'completed'
GROUP BY player_id
ORDER BY total DESC, MIN(completed_at) ASC
```

### `wiki_rounds`
Content table for the Wikipedia Speed Run game. Renamed from `wiki_content` — each row is a playable round (a start/target pair).

| column | type | notes |
|---|---|---|
| `id` | text PK | uuid |
| `start_page` | text | Wikipedia page title |
| `target_page` | text | Wikipedia page title |
| `optimal_steps` | int | nullable, used for bonus scoring |
| `difficulty` | text | `'easy'` \| `'medium'` \| `'hard'` |
| `hints` | text[] | ordered free-text hints; server returns `hints[hints_used]` on each request |
| `notes` | text | nullable, authoring notes |

### `wiki_sessions`
One row per player. Gameplay detail for a wiki session.

| column | type | notes |
|---|---|---|
| `id` | text PK | uuid |
| `game_session_id` | text FK → game_sessions | |
| `round_id` | text FK → wiki_rounds | which challenge was played |
| `click_path` | text[] | ordered visited page titles; initialise with `[start_page]` from the round; append on each valid forward click |
| `current_page` | text | page the player sees; initialise to `wiki_rounds.start_page`; update after each validated click |
| `hints_used` | int | default `0` |

Constraint: `UNIQUE (game_session_id)` — effectively 1:1 with game_sessions for wiki.

### `rapid_fire_questions`
Question pool. Renamed from `rapid_fire_content`.

| column | type | notes |
|---|---|---|
| `id` | text PK | uuid |
| `question_text` | text | |
| `question_type` | text | `'mcq'` \| `'typed'` |
| `options` | text[] | nullable, MCQ only |
| `correct_answer` | text | |
| `difficulty` | text | `'easy'` \| `'medium'` \| `'hard'` |
| `category` | text | topic grouping, for potential filtering |
| `time_limit_ms` | int | per-question time limit; question auto-skips when elapsed |

### `rapid_fire_answers`
One row per question answered. Insertion order = answer sequence. FKs directly to `game_sessions` — no intermediate session table needed.

| column | type | notes |
|---|---|---|
| `id` | text PK | uuid |
| `game_session_id` | text FK → game_sessions | |
| `question_id` | text FK → rapid_fire_questions | |
| `correct` | bool | |
| `time_ms` | int | time taken to answer this question |
| `answered_at` | timestamptz | server-written |

Already-asked question tracking: `SELECT question_id FROM rapid_fire_answers WHERE game_session_id = ?`.
Score derived at completion time from these rows. Streak is client-side.

---

## Hint Design

- Hints are free-text, authored per round, stored as `hints text[]` on `wiki_rounds`.
- No typed hint categories (`category`/`intermediate` dropped). Author writes as many as they want per round in order of increasing specificity.
- On each hint request: server returns `hints[hints_used]`, increments `hints_used`. If `hints_used >= len(hints)` → 400.
- Penalty is **flat per hint** (same cost regardless of how many taken). Simple to communicate to players.
- `WikiHintRequest` has no body — it's just "give me my next hint".

---

## Key Decisions & Rationale

- **Per-game session tables** (`wiki_sessions`, `rapid_fire_answers`) instead of one generic `game_sessions.session_data` blob — explicit schema per game, easier to reason about. Wiki state is typed columns; rapid fire uses child rows.
- **`game_sessions` as score ledger** — game-agnostic aggregate that makes the leaderboard query trivial and stays clean as more games are added.
- **Event code as env var** — shared code, no per-player credential row. Simple and sufficient.
- **`wiki_rounds.is_active`** — marks which challenge is live for the event. Game service picks `WHERE is_active = true LIMIT 1`. DB is the config, no env var needed for content selection.
- **Rapid fire: dynamic question serving** — server picks next question at each answer submission, excluding `asked_question_ids`. No upfront batch selection. Timer is `started_at + time_limit - now()` computed server-side on every response.
- **`rapid_fire_answers` child table, no intermediate session row** — FKs directly to `game_sessions`; `rapid_fire_sessions` dropped as a pointless passthrough. One INSERT per answer, asked-question tracking and score derivation from these rows. Streak client-side.
- **Rapid fire time limit is per-question** (`time_limit_ms` on `rapid_fire_questions`), seeded as content data. Question auto-skips on expiry. Final score is based on end-to-end time across all questions (i.e. `game_sessions.completed_at - started_at`), not per-question remaining time.
- **`abandoned` status** — player can voluntarily forfeit mid-game. Points accumulated up to that point are locked in and counted. No resume, no replay.

---

## Open Questions

- Scoring formula for wiki: deferred — will be resolved during game logic implementation.

---

## What's Not Decided Yet

Other three games (Picture Illustration, Four Pics One Lie, Crossword) — same pattern will apply but haven't designed their session/content tables yet.
