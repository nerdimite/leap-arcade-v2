# Wikipedia Rendering Hardening

**Status:** done

## Parent

`docs/issues/wikipedia-speed-run/parent.md`

## What to build

Polish and harden the rendered Wikipedia article experience after the core navigation path works. The article should feel familiar, remain game-safe, support browser find, show responsive loading states, and be covered by broader real-captured Wikimedia fixtures across the optimal paths.

## Acceptance criteria

- [x] Article container uses Wikipedia-like typography, spacing, tables/images handling, and scoped styles without leaking into the game UI
- [x] Game header remains fixed with clue, puzzle progress, timer, steps, score so far, and optional back button
- [x] Click-path breadcrumb is compact, scrollable, and useful for longer paths
- [x] Article navigation shows an overlay spinner/dim state while keeping the header visible and timer active
- [x] Ctrl+F / Cmd+F works because article HTML is rendered into the DOM
- [x] Rewriter disables external links, red/edit links, special pages, talk pages, category pages, file links, and citation jumps according to the PRD
- [x] Trusted Wikimedia images render; unsafe scripts and event handler attributes are removed
- [x] Captured Wikimedia fixtures cover all seeded start pages and optimal-path pages needed for happy-path testing
- [x] Tests assert policy-relevant HTML markers rather than brittle exact HTML snapshots
- [x] Frontend rendering tests cover loading overlay, breadcrumb, article click interception, and result screen transitions

## Blocked by

- `docs/issues/wikipedia-speed-run/sub-2-complete-one-puzzle-by-navigation.md`
