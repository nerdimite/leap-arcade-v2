# LEAP Tournament Platform — Project Brief

---

## 1. Brief

The LEAP Tournament Platform is a self-hosted, multiplayer mini-game tournament system built for a structured 1-hour group activity. Players compete across a set of intellectual and puzzle-based games, earn points, and rank on a shared live leaderboard. The platform is designed to be lightweight, self-contained, and deployable with a single command — no cloud dependencies, no external services, no setup burden on the day of the event.

The goal is a polished, energetic experience that feels like a game show — not an internal tool.

---

## 2. Context

### The LEAP Programme

LEAP is Fidelity's graduate onboarding programme for new joiners. Interns go through a structured 5-month stint covering technical exposure, cross-functional learning, and community-building activities organised by the LEAP Alumni L&D squad.

### The Activity

At the end of the internship cohort, LEAP alumni organise a closing group activity — roughly 1 hour — where interns compete in a tournament of mini-games. The intent is to end the programme on a high note: something fun, competitive, and memorable. This platform is built specifically for that activity.

### Hosting Context

The platform runs entirely within the training VMs provisioned to interns during the programme. These VMs sit outside the Fidelity intranet but have full internet access, so there are no network restrictions to contend with. The platform is packaged as a Docker Compose application — a single `docker compose up` starts all services. The vendor managing the VMs only needs Docker installed and one port exposed. No cloud deployment, no external database, no managed infrastructure.

### Auth

Player accounts are pre-configured before the event based on corp IDs. Players receive a shared event code or per-person credentials ahead of time. There is no self-registration flow — accounts exist at startup, seeded into the database alongside all game content.

---

## 3. Games

Five games are in scope for the initial build. Players can attempt them in any order (free-roam arcade model) but must complete every game they start — no mid-game exits, no replays.

### 3.1 Wikipedia Speed Run

Players start on a given Wikipedia page and must navigate to a target page using only internal Wikipedia links. Search is disabled, browser back is blocked, and the timer runs from the moment the game starts. The backend proxies Wikipedia content, rewrites internal links to route through the platform, and tracks every click. Scoring penalises time taken and steps taken, with bonuses for optimal pathing and hint avoidance.

### 3.2 Picture Illustration

Players are shown a set of images that together hint toward a concept, person, or topic — revealed progressively. They type a text answer which is validated server-side. Earlier correct answers yield higher scores; hints and wrong attempts carry penalties.

### 3.3 Rapid Fire Quiz

A timed quiz round — 30 to 60 seconds — where MCQ and typed questions auto-advance. Designed for fast, instinctive play. Scoring rewards correct answers, penalises wrong ones, and applies streak bonuses and speed multipliers.

### 3.4 Four Pics, One Lie

Four images are displayed — three belong to the same category, one is the odd one out. Players identify the outlier. Difficulty modes range from obvious to expert. Fast correct answers earn a speed bonus.

### 3.5 Crossword Puzzle

A classic crossword with across/down clues, keyboard navigation, and auto-focus movement. Multiple difficulty levels. Scoring rewards correct words and full puzzle completion, penalises wrong submissions and hint usage, and applies a time bonus for remaining time.

---

## 4. High Level User Journey

```
1. Player opens the platform URL in their VM browser

2. Login screen
   → Enter corp ID + event code
   → Server validates credentials, issues a JWT session

3. Arcade lobby
   → Five game tiles displayed
   → Each tile shows: game name, description, points available, status (not started / completed)
   → Global leaderboard visible in sidebar, updates periodically
   → Player picks any game to start

4. Game session starts
   → Server creates a session row with a server-side timestamp (source of truth for timer)
   → Client renders the game, reconstructs timer from server timestamp
   → Player cannot navigate away without a browser warning
   → On accidental refresh, session is rehydrated from server state

5. Player completes the game
   → Final answer / submission sent to server
   → Server validates, calculates score, marks session as completed
   → Score summary shown — points earned, time taken, breakdown
   → Player returned to lobby, completed game tile now locked

6. Player completes all five games
   → Final total score visible on leaderboard
   → Lobby shows a completion state
```

---

## 5. Technical Overview

### Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16 (App Router), React, TypeScript, TailwindCSS, shadcn/ui |
| Backend | FastAPI (Python), async, SQLAlchemy 2.0 (async style) |
| Database | PostgreSQL |
| Deployment | Docker Compose |

Redis is intentionally excluded — there is no problem in this system that requires it. Sessions are stateless JWTs, the leaderboard query is trivial at 200 concurrent users, and score deduplication is handled at the database layer.

### Services

```
docker-compose.yml
├── nextjs      :3000   — frontend, only externally exposed port
└── fastapi     :8000   — internal only, proxied via Next.js rewrites
└── postgres    :5432   — internal only
```

Next.js proxies all `/api/*` requests to FastAPI via `next.config.js` rewrites, so the browser talks to a single origin. No CORS configuration needed.

### Database Design Principles

**Preventing double writes**
A unique constraint on `(player_id, game_id)` in the `game_sessions` table ensures a player cannot create two sessions for the same game. Duplicate submission attempts return a clean error — no second row is created.

**Atomic score updates**
For incremental scoring games (Rapid Fire), scores are updated using atomic SQL:
```sql
UPDATE scores SET points = points + 50 WHERE player_id = $1 AND game_id = $2
```
This avoids read-modify-write races entirely. No application-level locking needed.

**Idempotent submissions**
Each game session is issued a server-generated session ID at start time. Final score submissions are keyed on this session ID. Repeated POSTs (network retries, double submits) are deduplicated — the server processes the first and ignores subsequent identical submissions.

**Server-side timer as source of truth**
`started_at` is written server-side when a session is created. The client derives the elapsed timer from this timestamp on every page load, including after a refresh. Client-side timer drift is irrelevant — scoring uses `completed_at - started_at` computed on the server.

### Game Services

Each game is a distinct service module within FastAPI with its own router, models, and scoring logic. They share the auth middleware and session infrastructure but are otherwise independent. This means a bug in the Crossword scoring logic cannot affect Rapid Fire, and individual games can be iterated on without touching others.

### Wikipedia Speed Run — Proxy Architecture

Wikipedia blocks iframe embedding and direct browser fetches via CORS. The platform handles this with a server-side proxy:

1. FastAPI fetches Wikipedia page HTML via the Wikipedia REST API
2. BeautifulSoup strips the response to the article body only — no navbars, infoboxes, or external links
3. Internal `/wiki/` links are rewritten to `/api/wiki/page?title=...`
4. The transformed HTML is returned to the client and rendered via `dangerouslySetInnerHTML`
5. Every link click hits FastAPI, which logs the step, checks for target completion, and returns the next page

All click path history is stored as a Postgres array column on the session row.

### Content Strategy

All game content — questions, image references, crossword grids, Wikipedia start/target pairs, category clues — is authored as JSON seed files and loaded into Postgres at container startup via a seed script. The platform has zero runtime dependency on external content APIs (except Wikipedia Speed Run which proxies Wikipedia live, and benefits from the VMs having full internet access). Images for Picture Illustration and Four Pics One Lie are bundled as static assets served directly by Next.js.

### Leaderboard

The leaderboard is a straightforward aggregation query:
```sql
SELECT player_id, SUM(score) as total, COUNT(*) as games_completed
FROM game_sessions
WHERE status = 'completed'
GROUP BY player_id
ORDER BY total DESC, MIN(completed_at) ASC
```

The tiebreaker is earliest completion time — fastest player across all games wins on a tie. The facilitator admin view polls this query every few seconds. No WebSockets, no Redis sorted sets — Postgres handles this comfortably at the expected concurrency.

### Frontend Architecture

Next.js 16 App Router is used with a clear boundary between server and client components:

- **Server components** — layout shell, auth checks, lobby page (initial data fetch), game page shell (session rehydration)
- **Client components** — all game UIs, timers, answer interactions, score feedback

Game state within each client component is managed via `useReducer` — a single reducer per game handling all state transitions (answer submitted, timer ticked, hint used, game completed). Side effects like API calls are triggered via `useEffect` watching derived state values.

### Concurrency

The platform is designed for approximately 200 concurrent players on a single VM. Given the read-heavy, bursty nature of the workload (most players are mid-game, submitting answers infrequently), Postgres with a standard connection pool handles this without issue. SQLAlchemy's async engine with a pool size of 20–30 connections is sufficient. No horizontal scaling, no queue, no cache layer needed.

---

*Document version: 0.1 — architecture jam, pre-build*