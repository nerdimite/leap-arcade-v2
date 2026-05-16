# Sub-2: Leaderboard Endpoint

**Status:** done  
**Blocked by:** none (Sub-1 completed)  
**Blocks:** nothing

## What to build

Implement `GET /leaderboard` end-to-end: DTO, DAO query, service, API schema, route, and subcutaneous tests. Replaces the `raise NotImplementedError` stub.

### Leaderboard behaviour

Every player in the system appears in the response, including those who have not started any game. Score contributions come from both `completed` and `abandoned` sessions — partial progress is visible. The `games_completed` count reflects only fully completed sessions, not abandoned ones. Entries are ordered by: total score descending → games completed descending → earliest completion time ascending (nulls last) → display name ascending. Each entry includes an explicit `rank` field (1-indexed position in the ordered list).

The response also includes `total_players` — the total count of all players in the leaderboard — so the frontend can display context like "you are #3 of 47".

### Data layer

A new `get_leaderboard()` method on `GameSessionDAO` executes a single SQL aggregation query. It LEFT JOINs from `players` to `game_sessions` (filtered to completed/abandoned) so players with no sessions appear with score 0. The method returns an ordered list of internal DTOs. Rank is not computed in SQL — it is added by the service as `enumerate(..., start=1)`.

The aggregation query (from the design session):

```sql
SELECT
    p.id AS player_id,
    p.display_name,
    COALESCE(SUM(gs.score), 0) AS total_score,
    COUNT(CASE WHEN gs.status = 'completed' THEN 1 END) AS games_completed,
    MIN(CASE WHEN gs.status = 'completed' THEN gs.completed_at END) AS first_completion
FROM players p
LEFT JOIN game_sessions gs
    ON gs.player_id = p.id AND gs.status IN ('completed', 'abandoned')
GROUP BY p.id, p.display_name
ORDER BY
    total_score DESC,
    games_completed DESC,
    first_completion ASC NULLS LAST,
    p.display_name ASC
```

`first_completion` is used for server-side ordering only — it is not included in the API response.

### Internal DTO

New `LeaderboardEntryDTO` with fields: `player_id: str`, `display_name: str`, `total_score: int`, `games_completed: int`, `first_completion: Optional[datetime]`. Subclasses `BaseLeapModel`.

### Service

New `LeaderboardService` with a single `get_leaderboard()` method. Opens `async with self.ctx.session()`, calls `game_session_dao.get_leaderboard(session)`, attaches `rank` (enumerate starting at 1), returns a structured response. Wired into `ServiceContainer` alongside `auth`, `lobby`, and `rapid_fire`.

### API schema

```
LeaderboardEntrySchema: rank, player_id, display_name, total_score, games_completed
LeaderboardResponse: entries: List[LeaderboardEntrySchema], total_players: int
```

### Route

`GET /leaderboard` — requires valid JWT (uses `get_current_player` for auth; player identity not used in the response body). Returns `LeaderboardResponse`.

## Acceptance criteria

- [x] `GET /leaderboard` returns 200 with all players in the `entries` list, including players with no sessions (score 0, games_completed 0)
- [x] `entries` are ordered: higher total score first; on tie, more games completed first; on tie, earliest first completion first; on tie, display name alphabetically
- [x] `rank` is 1-indexed and sequential (no gaps)
- [x] `total_players` equals the total number of players in the system
- [x] Abandoned session scores contribute to `total_score`; abandoned sessions do not increment `games_completed`
- [x] `GET /leaderboard` without a valid JWT returns 401
- [x] `first_completion` is absent from the API response (internal ordering only)
- [x] `LeaderboardService` is wired into `ServiceContainer` and accessible via `get_container`
- [x] Subcutaneous tests via `TestClient` verify all of the above through HTTP responses

## Blocked by

None — Sub-1 landed (`tests/conftest.py`, fakes, `TestClient` overrides).
