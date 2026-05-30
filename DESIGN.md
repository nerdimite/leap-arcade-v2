---
name: Glitch & Giggle
description: Clean retro arcade tournament platform, dark by default; the screen is the light source.
colors:
  bg: "oklch(0.16 0.035 280)"
  bg-2: "oklch(0.19 0.04 282)"
  panel: "oklch(0.225 0.04 283)"
  panel-2: "oklch(0.265 0.045 284)"
  line: "oklch(0.34 0.05 285)"
  ink: "oklch(0.97 0.01 280)"
  ink-dim: "oklch(0.72 0.03 285)"
  ink-faint: "oklch(0.58 0.03 285)"
  accent-wiki: "oklch(0.78 0.16 220)"
  accent-rapid: "oklch(0.80 0.17 65)"
  accent-pin: "oklch(0.74 0.20 350)"
  accent-pic: "oklch(0.72 0.18 300)"
  accent-four: "oklch(0.82 0.19 135)"
  accent-word: "oklch(0.78 0.13 185)"
  accent-cross: "oklch(0.72 0.19 25)"
  article-surface: "#ffffff"
  article-ink: "#202122"
  article-link: "#3366cc"
  article-target: "#1a7f37"
typography:
  display:
    fontFamily: "Press Start 2P, monospace"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  title:
    fontFamily: "Press Start 2P, monospace"
    fontSize: "11px"
    fontWeight: 400
    lineHeight: 1.5
  score:
    fontFamily: "Press Start 2P, monospace"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
  body:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "10px"
    fontWeight: 700
    lineHeight: 1.4
    letterSpacing: "1px"
  article:
    fontFamily: "Georgia, Times New Roman, serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.7
rounded:
  sm: "2px"
  md: "4px"
  pill: "999px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "22px"
  xl: "32px"
components:
  game-tile:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "0"
  status-play:
    backgroundColor: "{colors.accent-wiki}"
    textColor: "{colors.bg}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "6px 12px"
  status-done:
    backgroundColor: "transparent"
    textColor: "{colors.ink-faint}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "6px 12px"
  hud-stat:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "6px 16px"
  button-primary:
    backgroundColor: "{colors.accent-wiki}"
    textColor: "{colors.bg}"
    rounded: "{rounded.md}"
    padding: "8px 16px"
  leaderboard:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "0"
---

# Design System: Glitch & Giggle

Visual system for **Glitch & Giggle** (the LEAP Arcade platform). Tokens above are normative; the prose below is how to apply them. Reference implementation: `docs/prototypes/lobby-arcade.html` and `docs/prototypes/wiki-arcade.html`. Production styles: `frontend/src/app/globals.css` (still on the placeholder shadcn theme; migrate to these tokens). Colors are OKLCH to match the project's Tailwind v4 `@theme` convention; this trips the Stitch hex linter by design.

## 1. Overview

**Creative North Star: "The Lit Cabinet in a Dark Arcade"**

A game-show stage and an arcade cabinet are both dark rooms where the screen is the light source. Glitch & Giggle defaults to a deep, tinted near-black environment and lets the lit things carry the energy: a tile's glowing marquee strip, a score in lime, the single bright browser window of the Wikipedia game. Dark is a deliberate metaphor here, not a reflex. The platform is competitive but never solemn; the name pairs a little retro-digital mischief ("glitch") with genuine fun ("giggle").

Personality is playful, competitive, crafted. We embrace the arcade brief (old-school cabinet, pixel characters, confetti, score-reveal drama) but execute it with restraint so it reads as a deliberate choice, not cosplay. Depth comes from hard offset shadows (the satisfying "press" of a cabinet button), never glow bloom. Pixel type is punctuation, not paragraphs.

This system explicitly rejects: neon-on-black RGB-gamer cliche (no glow bleed, no rainbow), corporate intranet dullness (no gray enterprise tables), childish gimmickry (no Comic Sans, no cartoon mascots, no balloons), and generic SaaS templates (no hero-metric blocks, no identical card grids as a layout crutch).

**Key Characteristics:**
- Dark midnight-indigo environment; lit saturated accents do the talking.
- Seven games, seven marquee accent colors; one shared chrome and type system.
- Pixel display type for wordmark / titles / scores only; Inter for everything readable.
- Hard offset "cabinet" shadows for depth; glow reserved for the marquee strip and the diegetic browser.
- Every effect (confetti, scanline, blink, reveal) is earned and has a reduced-motion fallback.

## 2. Colors

A committed dark indigo environment plus a full palette of named per-game accents, each used deliberately. Never `#000` / `#fff`; every neutral is tinted toward the base hue (~280). This intentionally exceeds the single-accent restraint rule, because per-game identity is a core principle.

### Primary
- **Marquee accents** (one per game, applied via a local `--accent`): **Wiki Cyan** (`oklch(0.78 0.16 220)`), **Rapid Amber** (`oklch(0.80 0.17 65)`), **Pinpoint Magenta** (`oklch(0.74 0.20 350)`), **Picture Violet** (`oklch(0.72 0.18 300)`), **Four-Pics Lime** (`oklch(0.82 0.19 135)`), **Word Teal** (`oklch(0.78 0.13 185)`), **Crossword Coral** (`oklch(0.72 0.19 25)`). Each lights its game's tile marquee, sprite border, points, status pill, and focus ring. Default accent when no game is in context is Wiki Cyan.

### Secondary
- **Score Lime** = Four-Pics Lime, reused as success / points / positive deltas.
- **Timer Amber** = Rapid Amber, reused as warning / timer-running.
- **Danger Coral** = Crossword Coral, reused as destructive / low-time; keep `--destructive` aligned to this hue.

### Tertiary
- **The Light Island** (Wikipedia diegetic browser only): surface `#ffffff`, ink `#202122`, rules `#a2a9b1`, link `#3366cc`, target link `#1a7f37` on a `#b6f0c4` halo, infobox `#f8f9fa`. Scoped to that frame; never leaks into app chrome.

### Neutral
- **Cabinet Base** `oklch(0.16 0.035 280)` (`--bg`): app background; with `--bg-2` `oklch(0.19 0.04 282)` for the top radial glow and raised wells.
- **Panel** `oklch(0.225 0.04 283)`: cards, tiles, HUD, sidebar. **Panel-2** `oklch(0.265 0.045 284)`: active/elevated rows.
- **Line** `oklch(0.34 0.05 285)`: 2px default chrome stroke, dividers.
- **Ink** `oklch(0.97 0.01 280)` primary, **Ink-dim** `oklch(0.72 0.03 285)` body, **Ink-faint** `oklch(0.58 0.03 285)` labels/meta (the floor for text).

### Named Rules
**The AA-on-Dark Rule.** Every accent and ink must clear WCAG AA against `--panel` / `--bg`; `--ink-faint` is the dimmest permitted text. **The Color-Plus Rule.** State is never signalled by color alone, always paired with icon, label, or position (`✓ Done`, `🔒`, blinking `LIVE`). **The One Glow Rule.** Glow (`0 0 18px`) is reserved for the lit marquee strip and the diegetic browser frame; everywhere else depth is a hard offset shadow.

## 3. Typography

**Display Font:** Press Start 2P (with monospace fallback)
**Body Font:** Inter (with system-ui, sans-serif)
**Article Font:** Georgia (with Times New Roman, serif) — only inside the diegetic Wikipedia window.

**Character:** A pixel display face for arcade swagger paired with a crisp neutral sans for total legibility. The tension between the two is the point: retro on top, modern underneath. In `@theme`, point `--font-heading` at Press Start 2P and keep `--font-sans` = Inter.

### Hierarchy
- **Display** (Press Start 2P, 18px, 1.5): wordmark, lobby H1. Layered hard text-shadow in accent colors (e.g. `3px 3px 0 var(--pin)`).
- **Score** (Press Start 2P, 14–16px, 1.5): score numerals, HUD stat values.
- **Title** (Press Start 2P, 11px, 1.5): game tile titles, leaderboard rank/score cells.
- **Kicker** (Press Start 2P, 9–10px, 1.5): section kickers, points labels.
- **Body** (Inter, 15px, 1.6): lobby intro and descriptions; cap line length at 60–75ch.
- **Meta** (Inter, 13–14px, 1.55): tile copy, rows, player names, ids.
- **Label** (Inter, 10px, 700, 1px tracking, often UPPERCASE): stat labels, status pills, captions.

### Named Rules
**The Pixel-as-Punctuation Rule.** Pixel type is for short strings only (wordmark, titles, numerals, kickers). Anything a player must read to play, descriptions, clues, quiz options, leaderboard names, is Inter. Pixel everywhere reads juvenile; pixel as accent reads crafted. Maintain ≥1.25 scale ratio between adjacent steps.

## 4. Elevation

Depth is conveyed by **hard offset shadows**, not blur, the visual language of a physical arcade button pressing in and out. Glow is deliberately not an elevation tool here (it is reserved for the marquee strip and the diegetic browser). Borders are heavier than typical product UI (2px `--line`) to reinforce the cabinet-panel feel.

### Shadow Vocabulary
- **Standard** (`box-shadow: 6px 6px 0 oklch(0.10 0.03 280 / 0.85)`): tiles, sidebar, browser frame.
- **Small** (`box-shadow: 4px 4px 0 oklch(0.10 0.03 280 / 0.85)`): HUD stats, status pills, small chrome.
- **Hover lift** (`9px 9px 0 oklch(0.10 0.03 280 / 0.85)` + `transform: translate(-3px,-3px)`): tile hover.
- **Press** (Small shadow + `transform: translate(2px,2px)`): tile / button active.
- **Marquee glow** (`box-shadow: 0 0 18px var(--accent)` on a solid accent bar): the one sanctioned glow. Sprite recess uses `inset 0 0 12px oklch(0 0 0 / 0.6)`.

### Named Rules
**The Press Rule.** Interactive surfaces lift toward the cursor on hover (bigger offset, negative translate) and press in on active (smaller offset, positive translate). The shadow stays a hard, opaque, single-direction offset, never a soft ambient blur. Radius is small (`--radius: 4px`; pills `999px`); sharp corners suit the pixel aesthetic. A fixed full-screen scanline overlay (`repeating-linear-gradient`, 2px transparent / 1px `oklch(0 0 0 / 0.05)`, `mix-blend-mode: multiply`) and a vignette add texture beneath all chrome (z-9998/9999), subtle and never a gimmick.

## 5. Components

Built on shadcn/ui + Radix + Tailwind v4 + lucide-react. Do not hand-author primitives; add via `bunx shadcn@latest add` and theme through the tokens above (mostly via the `--accent` channel).

### Buttons
- **Shape:** `--radius: 4px` (`{rounded.md}`); status pills `999px`.
- **Primary:** active `--accent` fill on dark ink (`{colors.bg}`), `--shadow-sm`, presses in on active. Focus ring uses `--accent` and must be visible (full keyboard nav is required).
- **Status pill (play):** solid `--accent`, dark ink, `--shadow-sm`. **Status pill (done):** transparent, 1.5px `--line` border, faint ink, with `✓` + score. Never color-only.

### Game Tile
A card and a cabinet: top lit `--accent` marquee strip (8px, glowing); body with a sprite recess (58px, 2px `--accent` border, inset shadow) + pixel title + Inter description; footer with pixel points in `--accent` and a status pill. Hover lifts, active presses. **Completed:** `opacity: 0.72`, desaturated marquee, `🔒` badge, locked (no re-entry). No nested cards.

### HUD Stat
Small framed `--panel` block: pixel value + uppercase faint label. Variants: `timer` (amber; `low` adds coral + `blink`), `steps`/`clicks`, `score` (lime).

### Leaderboard
Framed surface with an accent title bar (`--pin`): pixel heading + blinking `LIVE` dot. Rows: pixel rank / Inter name + faint id / pixel score (lime). `top1` shows rank+score in amber; `you` row uses `--panel-2` fill and `--wiki` name. Lobby = sticky sidebar (top 5 + you); full page = all players. Poll via React Query `refetchInterval`, not hand-rolled intervals.

### Diegetic Browser (Wikipedia Speed Run)
Dark chrome bar (traffic-light dots, disabled back/forward marked ✕, reload), white address bar with 🔒 + URL + a red "SEARCH DISABLED" chip; light serif article body inside; breadcrumb path bar below as pills (`cur` step in `--wiki`). The frame glows (`0 0 38px oklch(0.78 0.16 220 / 0.28)`) with a 2px `--wiki` border, the single bright screen in the dark room.

### Objective Ribbon (Wikipedia)
`start` node (`--wiki` border) → dashed arrow → `target` node (`--four` border), each a framed pill with an uppercase cap + bold label.

### Sprites & Motion
Per-game pixel characters in the tile recess (emoji placeholder now, `image-rendering: pixelated`; swappable for real pixel art without structural change). Easing is ease-out-quint `cubic-bezier(0.22, 1, 0.36, 1)`, no bounce. Interactive feedback 120–180ms; reveals ~350ms. Animate transform/opacity only, never layout. Named animations extend the existing `globals.css` keyframes (`picture-input-shake`, `pinpoint-badge-shake`, `pinpoint-badge-reveal`) plus `blink` (LIVE dot / low timer, `steps(2)`), score-reveal, and confetti (win only).

## 6. Do's and Don'ts

**Do**
- Default to dark; let lit accents and scores carry the energy.
- Give each game its own accent via a local `--accent`; keep all other chrome shared.
- Reserve pixel type for wordmark, titles, scores, kickers; use Inter for anything a player reads to play.
- Convey depth with hard offset shadows; lift on hover, press on active.
- Earn every effect (confetti, scanline, blink, reveal) and provide a `prefers-reduced-motion` fallback. This is required, not optional.
- Keep AA contrast on the dark base; pair every state cue with icon/label/position.
- Render the Wikipedia article in light mode inside the glowing browser frame; keep those light tokens scoped to it.
- Use the brand name "Glitch & Giggle" in player-facing copy; "LEAP Arcade" is the internal platform name.

**Don't**
- Don't use neon glow bloom, rainbow gradients, or `background-clip: text` gradient text.
- Don't set body copy, clues, or quiz options in pixel type.
- Don't use soft ambient/blurred shadows, glassmorphism, or nested cards.
- Don't add side-stripe borders, hero-metric blocks, or identical icon-card grids as a layout crutch.
- Don't signal correct/wrong/status by color alone.
- Don't let the Light Island tokens leak into the dark app chrome.
- Don't use em dashes or childish/gimmicky copy (Comic Sans, mascots, balloons).
- Don't hand-author shadcn primitives; add them via the CLI and theme with tokens.
