---
target: rapid fire screens
total_score: 28
p0_count: 0
p1_count: 2
timestamp: 2026-05-30T14-43-36Z
slug: app-games-rapid-fire-components-rapidfireview-tsx
---
# Rapid Fire screens — critique

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Timer/score/progress solid; feedback verdict weak and easy to miss |
| 2 | Match System / Real World | 3 | Quiz metaphor + "QUICK DRAW" read clearly |
| 3 | User Control and Freedom | 3 | No mid-game exit; acceptable for a timed one-shot |
| 4 | Consistency and Standards | 3 | `text-muted-foreground` shadcn token drift; two redundant feedback channels |
| 5 | Error Prevention | 3 | Disabled-while-locked prevents double-submit |
| 6 | Recognition Rather Than Recall | 3 | Options + correct/wrong reveal are clear |
| 7 | Flexibility and Efficiency | 2 | Shows "1.–4." numerals but no number-key shortcuts on a speed quiz |
| 8 | Aesthetic and Minimalist Design | 2 | Narrow 512px column + dim scrim fighting option colors + tiny bottom pill |
| 9 | Error Recovery | 3 | Wrong answer reveals the correct option |
| 10 | Help and Documentation | 3 | Instructions view planned separately |
| **Total** | | **28/40** | **Good, with clear upside** |

## Anti-Patterns Verdict
- LLM: not obviously AI-generated; arcade identity is committed. The feedback pattern (full-card dim scrim + small centered-ish pill) is the weakest, most generic moment.
- Deterministic scan: `detect.mjs` on the rapid-fire components returned `[]` (clean).
- Browser overlay: not available (no automation in env); source-based visual review only.

## Priority Issues

- **[P1] Narrow play stage.** `RapidFireView` is `max-w-lg` (512px). On a VM browser in a loud room this reads as a timid centered column with dead side gutters, not a game-show stage. Question text is only 16px.
  - Fix: widen to ~`max-w-2xl` and lift question type (20–24px). Give the stage presence.

- **[P1] Feedback is bottom-anchored and muddy.** `FeedbackOverlay` uses `items-end ... pb-6`, so the verdict pill sits at the card bottom (the "not centered" you saw). The `bg-bg/50` scrim dims the whole card, including the options the QuestionCard just recolored green/red, so the two feedback channels fight each other.
  - Fix: drop the dimming scrim; keep the recolored options fully legible (that IS the answer reveal). Replace the floating pill with a bold full-width verdict band in the timer's slot at the top of the card. Full-width text is inherently centered and reads instantly.

- **[P2] Feedback shows total score, not the points earned.** The pill says "Score {total}". The dopamine of a rapid quiz is the `+delta`. The earned points are the satisfying number and they're missing.
  - Fix: show "CORRECT +120" with the delta; let the header ScoreReadout absorb the new total.

- **[P2] No number-key shortcuts.** Options are enumerated "1.–4." implying keys, but there's no `1–4` handler. A speed quiz that can't be played by keyboard loses competitive players seconds per question.
  - Fix: bind 1–4 to option select during the question phase.

- **[P3] Minor drift.** `QuestionCard` uses `text-muted-foreground` (shadcn) instead of `text-ink-faint`; `currentScore` is passed to QuestionCard then `void`-ed (dead prop).

## Delight opportunity (feedback)
There is currently zero motion on feedback; it just appears. DESIGN sanctions score-reveal drama, win-only confetti, blink, ease-out-quint, all with reduced-motion fallbacks. Earn it here: verdict band punches in (scale 1.06→1 + opacity, ~180ms ease-out-quint), points delta counts up, a small lime confetti burst on correct, a coral shake on wrong. This is the peak-end moment of every question; it should feel like a hit.

## Persona Red Flags

**Sam (competitive speed-runner):** sees "1. 2. 3. 4." but must mouse or Tab to answer, no number keys; bleeds seconds. The small bottom pill is easy to miss at a glance between questions.

**Jordan (first-timer, high-energy room):** the verdict is a small pixel pill over a dimmed card; correct/wrong may not register instantly under time pressure and social noise.

## Minor Observations
- Option enumerator uses `font-mono` + shadcn muted token; align to arcade ink tokens.
- Feedback `aria-live="polite"` is good; keep the verdict text ("CORRECT"/"WRONG") so it's not color-only.

## Questions to Consider
- What if the verdict owned the top band of the card instead of floating at the bottom?
- What would the most satisfying half-second of a correct answer look like?
- Should the stage width match the game-show ambition the rest of the system sets?
