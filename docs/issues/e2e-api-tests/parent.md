# E2E API Test Infrastructure

**Status:** in progress

## What to build

Lift the Docker Compose setup to the repo root, add a dedicated test database service, and build an e2e test suite that exercises the full API stack (real PostgreSQL, real migrations, real seed data) through user journey tests. Provide a Makefile so developers can run the full stack and e2e suite with single commands.

**PRD:** `docs/plans/2026-05-16-e2e-api-tests-prd.md`

**Slice 1 (compose + Makefile):** done — `docs/issues/e2e-api-tests/sub-1-compose-restructure.md`

**Slice 2 (e2e infra):** done — `docs/issues/e2e-api-tests/sub-2-e2e-infra.md`

**Slice 5 (multi-player leaderboard):** done — `docs/issues/e2e-api-tests/sub-5-leaderboard-ranking-journey.md`

## Execution plan

```
Slice 1 (no blockers):   Sub-1 — Compose restructure + Makefile
Slice 2 (after Sub-1):   Sub-2 — E2e test infrastructure
Slice 3 (after Sub-2):   Sub-3 — Happy path + auth edge case journeys (done)  ┐
Slice 4 (after Sub-2):   Sub-4 — Session lifecycle journeys (done)            ├─ parallel
Slice 5 (after Sub-2):   Sub-5 — Multi-player leaderboard ranking       ┘
```

## Overall acceptance criteria

- [ ] `make dev` starts `postgres + api` from the repo root
- [ ] `make e2e` spins up `postgres_test`, migrates, seeds, runs all e2e journeys, tears down
- [ ] `make e2e-reset` nukes the `postgres_test` volume and re-runs from scratch
- [ ] All 6 user journeys pass against a real PostgreSQL database
- [ ] Dev workflow (`backend/.env`, existing unit tests) is completely unchanged
