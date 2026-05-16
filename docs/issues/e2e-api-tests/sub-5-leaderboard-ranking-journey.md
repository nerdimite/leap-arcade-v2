# Sub-5: Multi-Player Leaderboard Ranking Journey

**Status:** done  
**Blocked by:** Sub-2  
**Blocks:** nothing

## Parent

`docs/issues/e2e-api-tests/parent.md`

## What to build

Write one e2e journey test that exercises the leaderboard ranking with multiple players. This verifies the ranking SQL is correct end-to-end, not just in isolation.

**Journey — Multi-player ranking:**
Two players complete rapid fire with different scores. `GET /leaderboard` returns both players in descending score order.

To guarantee different scores the test must engineer the outcome deliberately. The simplest approach: Player A answers all questions correctly (pick an option and rely on the real scoring), Player B answers zero questions then abandons (score stays 0). The leaderboard must then show Player A above Player B.

Since the test cannot know which option is "correct" without querying the DB directly, the recommended approach is:
- Player B: start a session and immediately abandon → score 0
- Player A: complete the full question loop (same pattern as Sub-3 Journey 1) → score > 0
- Assert leaderboard: exactly 2 entries, Player A first, Player B second, `player_a.score > player_b.score`

Each player uses a distinct `corp_id` (e.g. `"emp_rank_a"`, `"emp_rank_b"`).

## Acceptance criteria

- [x] Leaderboard returns exactly 2 entries after both players have finished
- [x] Player A (completed game) appears above Player B (abandoned with 0 answers) in the response
- [x] `player_a.score > player_b.score` is asserted explicitly
- [x] Journey passes under `make e2e`
- [x] `clean_db` fixture ensures this journey is independent of Sub-3 and Sub-4 journeys

**Implementation:** `backend/tests/e2e/test_leaderboard_ranking_journey.py` — truncates transactional tables at journey start (only `emp_rank_a` / `emp_rank_b`), then Player B play+abandon, Player A full answer loop (correct options resolved via `rapid_fire_questions` by id from API), leaderboard assertions.

## Blocked by

Sub-2 (`docs/issues/e2e-api-tests/sub-2-e2e-infra.md`)
