# LEAP Tournament Platform — To Dos

---

## Backend

- [x] Repo structure + Docker Compose setup (fastapi, postgres)
- [ ] Postgres schema — players, game_sessions, scores tables with constraints
- [ ] SQLAlchemy async models
- [ ] Seed script — player accounts (corp IDs) + all game content
- [ ] Auth — login endpoint, JWT generation, auth middleware
- [ ] Game session endpoints — start session, rehydrate on refresh, complete session (shared logic across all games)
- [ ] Rapid Fire service — fetch questions, submit answer, scoring logic
- [ ] Wikipedia Speed Run service — proxy + HTML transform, click tracking, path validation, completion detection
- [ ] Leaderboard endpoint — global scores, per-game scores
- [ ] Admin endpoint — leaderboard poll for facilitator view

---

## Frontend

- [ ] Next.js 16 project setup, Tailwind + shadcn config, design tokens
- [ ] Auth page — login form, JWT storage
- [ ] Arcade lobby — 5 game tiles, game status, leaderboard sidebar
- [ ] Game session shell — refresh rehydration, beforeunload guard, timer sync
- [ ] Rapid Fire UI
- [ ] Wikipedia Speed Run UI
- [ ] Score summary modal (shared, used by all games on completion)
- [ ] Admin / facilitator leaderboard view

---

## Content

- [ ] Author Rapid Fire questions (JSON)
- [ ] Author Wikipedia start/target pairs

---

## Polish + Testing

- [ ] End to end run through all 5 games
- [ ] Concurrent load sanity check at ~200 users
- [ ] Mobile responsiveness pass
- [ ] Docker Compose production build test — clean `docker compose up` from scratch