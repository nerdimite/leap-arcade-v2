# Product

## Register

product

## Users

LEAP interns: graduates on Fidelity's 5-month onboarding programme, competing in a closing ~1-hour group tournament. They play on the training VM browsers (full internet, outside the intranet), pre-seeded with accounts (corp ID + shared event code, no self-registration).

Their context is high-energy and social: a roomful of peers playing at once, scores flowing onto a shared live leaderboard. The job to be done is simple and emotional: jump into any of the seven mini-games from a lobby, play fast, climb the leaderboard, and end the programme on a memorable high note. A facilitator watches an admin leaderboard view.

## Product Purpose

Glitch & Giggle is a self-hosted, single-`docker compose up` tournament platform that runs entirely on the interns' VMs with no cloud or external services (internally the LEAP Arcade platform). Players log in, free-roam between seven mini-games (Wikipedia Speed Run, Rapid Fire Quiz, Pinpoint, Picture Illustration, Four Pics One Lie, Word Hunt, Crossword), complete each game once, and rank on a live leaderboard.

Success is the *feeling*, not just the function: it should land like a game show, not an internal tool. The platform succeeds if interns forget they are using corporate software and instead feel like contestants. Functionally, it must stay fast, fair (server-side timing and scoring), and bulletproof for ~200 concurrent players in a one-shot live event with no second chances.

## Brand Personality

Three words: **playful, competitive, crafted.**

Voice is that of a confident game-show host: energetic, a little theatrical, never corporate. Copy is short, punchy, and celebratory on wins; clear and calm during play.

The product name, **Glitch & Giggle**, sets the tone: a little retro-digital mischief ("glitch") paired with genuine fun ("giggle"). It is competitive but never solemn.

The aesthetic register is **clean retro arcade**. We embrace the arcade brief (old-school cabinet, pixel characters, confetti, score-reveal drama) but execute it with restraint so it reads as a deliberate design choice, not cosplay. The guiding metaphor: a game-show stage and an arcade cabinet are both *dark rooms where the screen is the light source*, which is why the experience defaults to dark, the lobby is the darkened arcade, and each game tile is a lit marquee.

Emotional goals: anticipation walking up to a cabinet, the thrill of a fast correct answer, the drama of a score reveal, the pride of climbing the board.

## Anti-references

- **Neon-on-black gamer / RGB cyberpunk.** We are arcade, but we reject glow bloom, rainbow neon, and edgy-dark-mode cliche. Depth comes from hard offset shadows ("button press"), not light bleed.
- **Corporate intranet tool.** No gray enterprise tables, cramped forms, or SharePoint/Jira energy. The brief explicitly rejects this.
- **Childish / gimmicky.** Pixel-fun and confetti, yes; Comic Sans, cartoon mascots, and balloons, no. Playful, not juvenile.
- **Generic SaaS dashboard.** No card-grid template, no hero-metric blocks, no startup-cream AI-slop layout.

## Design Principles

- **The screen is the light source.** Default to a dark, tinted arcade environment; let lit elements (tiles, scores, active game) carry the energy. Dark is a deliberate metaphor here, not a fallback.
- **Pixel as accent, not as everything.** Reserve retro/pixel display type for the wordmark, score numerals, and game titles. Body, clues, quizzes, and leaderboards use a crisp modern sans so legibility always wins. Pixel everywhere reads juvenile; pixel as punctuation reads crafted.
- **Earn every effect.** Confetti, sprite motion, CRT/scanline texture, and score-reveal drama are deployed at moments that matter (wins, reveals), never as ambient decoration. Every effect has a calm reduced-motion fallback.
- **Diegetic framing where it delights.** Lean into in-world devices that make play feel like a game, not a form. Flagship example: Wikipedia Speed Run renders inside a retro-OS browser window (title bar, fake address bar, window chrome) with the article in light mode, a single glowing "browser" inside the dark arcade.
- **Per-game identity, one system.** Each mini-game gets its own accent color and character so the lobby feels varied and alive, while all games share one chrome, one type system, and one motion language.
- **Fair and fast under pressure.** This is a one-shot live event for ~200 players. Server-side timing and scoring are the source of truth; the UI must stay responsive, prevent double-submits, and rehydrate cleanly on refresh. Polish never compromises fairness or reliability.

## Accessibility & Inclusion

- **WCAG 2.1 AA contrast** for text and interactive elements. Saturated marquee accents on the dark base must still clear AA; this constrains palette choices deliberately.
- **Respect `prefers-reduced-motion`.** Confetti, sprite animation, and CRT/scanline texture all degrade to calm, static fallbacks. Score and state changes remain legible without motion.
- **Full keyboard navigation.** Keyboard-driven games (Crossword, Rapid Fire, Word Hunt, Pinpoint) are fully operable by keyboard with visible focus states; lobby and leaderboard are keyboard-traversable.
