# AI Tournament Platform – Product & Technical Requirements Document

**For Claude Agent Implementation**

---

# 1. Product Vision

Build a **web-based multiplayer tournament gaming platform** where users can:

* Register/Login
* Join tournaments
* Play multiple rounds of intellectual and puzzle-based games
* Earn points
* Compete on leaderboards
* Progress through tournament stages
* Win prizes/titles


The application should prioritize:

* Fast gameplay
* Clean UX
* Real-time scoring
* Anti-cheating mechanisms
* Tournament progression logic
* Mobile + Desktop responsiveness

---

# 2. Target Audience

* Corporate associates
* Students
* Tech communities

---

# 3. High-Level System Requirements

## Frontend

* React + TypeScript
* TailwindCSS
* Framer Motion for transitions
* Responsive UI
* Real-time timer updates
* WebSocket support

## Backend

* Node.js + Express OR NestJS
* PostgreSQL
* Redis (leaderboards/timers/session caching)
* WebSocket server (Socket.io)

## Authentication

* JWT Authentication
* Google OAuth optional
* Secure session handling

## Deployment

* Dockerized
* Cloud deployable

---

# 4. Core Platform Features

## 4.1 Authentication

Users should be able to:

* Login
* Reset password
* View profile
* Track stats

---

## 4.2 Tournament Engine

### Features

* Tournament creation
* Scheduled rounds
* Timed rounds
* Score aggregation

---

## 4.3 Leaderboard System

### Types
* Tournament leaderboard
* Game-specific leaderboard

### Ranking Logic

Sort by:

1. Total score
2. Completion time
3. Accuracy
4. Hint usage

---

# 5. Game Requirements

---

# GAME 1 – Wikipedia Speed Run

## Concept

Player starts from one Wikipedia page and must reach a target Wikipedia page using only internal wiki links.

Example:
Start: "Coffee"
Target: "Quantum Mechanics"

---

## Gameplay

* Only internal wiki navigation allowed
* Search disabled
* Browser back disabled
* Timer starts immediately

---

## UI Requirements

* Embedded wiki renderer
* Highlight clickable internal links
* Show:

  * Current page
  * Target page
  * Time elapsed
  * Steps taken

---

## Backend Requirements

* Wikipedia API integration
* Path tracking
* Click history storage
* Validation that only allowed links are used

---

## Scoring Logic

### Base Score

1000 points

### Formula

```text
Final Score =
1000
- (Time Taken * 2)
- (Steps Taken * 5)
- Hint Penalty
```

### Bonus

* Under optimal path → +200
* No hints → +100

### Hint System

* Reveal related category
* Reveal intermediate article

Penalty:
-50 per hint

---

# GAME 2 – Crossword Puzzle

## Concept

Classic crossword solving game.

---

## Requirements

* Dynamic crossword generator
* Across/Down clues
* Keyboard navigation
* Auto-focus movement
* Highlight active word

---

## Difficulty Levels

* Easy
* Medium
* Hard

---

## Backend

Store:

* Puzzle layout
* Clues
* Solutions
* User progress

---

## Scoring

```text
Correct Word = +20
Correct Puzzle Completion Bonus = +200
Wrong Submission = -2
Hint Usage = -10
Time Bonus = Remaining Time
```

---

# GAME 3 – Picture Illustration

## Concept

Users see multiple images that together hint toward a concept/topic.

Example:

* Apple
* Gravity
* Prism
* Telescope

Answer: Isaac Newton

---

## Requirements

* AI-generated or curated image sets
* Progressive reveal
* Text answer input

---

## Hint System

* Reveal category
* Reveal first letter
* Reveal era/domain

---

## Scoring

```text
Solve with 1 image = 500
2 images = 400
3 images = 300
4 images = 200
Hint used = -50
Wrong attempts = -10
```

---

# GAME 4 – Rapid Fire

## Concept

Timed quiz round.

---

## Gameplay

* 30–60 seconds
* MCQ + typed answers
* Questions auto-advance

---

## Features

* Difficulty scaling
* Topic categories
* Streak bonus

---

## Scoring

```text
Correct = +50
Wrong = -10
Streak of 5 = +100
Speed Bonus = Remaining milliseconds factor
```

---

# GAME 5 – Pinpoint (Inspired by LinkedIn Games)

## Concept

User identifies a hidden category using progressively revealed clues.

Example:
Clues:

* Java
* Python
* Rust
  Answer:
  Programming Languages

---

## Gameplay

* Start with minimal clues
* Reveal more clues gradually
* Earlier guesses yield more points

---

## Requirements

* Category engine
* Progressive clue reveal
* Guess validation

---

## Scoring

```text
Solved in 1 clue = 500
2 clues = 400
3 clues = 300
4 clues = 200
5 clues = 100
Wrong guess = -20
```

---

# GAME 6 – Cross Climb (Inspired by LinkedIn Games)

## Concept

Word ladder puzzle where one letter changes per row while clues connect words.

Example:
COLD
CORD
CARD
WARD
WARM

---

## Requirements

* Grid-based UI
* Clue support
* Validation engine
* Auto-check letter changes

---

## Rules

* Only one letter changes
* Every intermediate word must be valid

---

## Scoring

```text
Correct Ladder Step = +50
Puzzle Completion = +300
Hint = -30
Wrong word = -10
```

---

# GAME 7 – Four Pics, One Lie

## Concept

4 images displayed:

* 3 belong to same category
* 1 is the odd one out

---

## Requirements

* Image rendering
* Category metadata
* Selection validation

---

## Difficulty Modes

* Obvious
* Tricky
* Expert

---

## Scoring

```text
Correct = +100
Wrong = -30
Fast Answer Bonus = +50
```

---

# GAME 8 – Git Gone Wrong

## Concept

Simulated terminal where users solve git problems via commands.

Example:
Scenario:
"Undo the last commit but keep changes staged."

Expected:

```bash
git reset --soft HEAD~1
```

---

## Requirements

### Terminal Emulator

* Fake terminal UI
* Command parser
* Scenario engine
* Git state simulator

### Supported Git Concepts

* reset
* revert
* rebase
* stash
* merge conflicts
* cherry-pick
* detached HEAD
* branch recovery

---

## Validation Engine

Must:

* Track repo state
* Validate command correctness
* Allow alternate valid solutions

---

## Difficulty Levels

* Beginner
* Intermediate
* Advanced

---

## Scoring

```text
Correct Solution = +500
Optimal Command Bonus = +100
Each Wrong Command = -20
Hint = -50
Time Penalty applied
```

---

# GAME 9 – Squaredle

## Concept

Users connect letters in any direction to form words.

Letters disappear/fade when all associated words are found.

---

## Requirements

* Interactive letter grid
* Drag/swipe support
* Dictionary validation
* Word path tracking

---

## Rules

* Adjacent movement allowed
* Diagonal allowed
* Cannot reuse same tile in same word

---

## Backend

* Trie-based dictionary lookup
* Word generation engine
* Path validation

---

## Scoring

```text
3-letter word = 10
4-letter word = 20
5-letter word = 40
6+ letter word = 80
Complete Board Bonus = +500
```

---
