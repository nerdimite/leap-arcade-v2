import type { LobbyGameId } from "@/lib/constants";
import { GAME_MAX_POINTS } from "@/lib/constants";

export type GameTileDefinition = {
  id: LobbyGameId;
  name: string;
  description: string;
  href: string;
  maxPoints: (typeof GAME_MAX_POINTS)[LobbyGameId];
};

/**
 * Per-game marquee identity: one accent color, one pixel sprite, and the header
 * cabinet plate (`label` kicker + `tagline`) each, so the lobby and every game
 * screen read as seven distinct lit cabinets sharing one chrome. `accent` is a
 * CSS var reference set on the local `--accent` channel; `sprite` is an emoji
 * placeholder (image-rendering: pixelated) swappable for real pixel art. The
 * shared `GameHeader` reads `label`/`tagline` so the marquee copy lives once.
 */
export type GameVisual = {
  accent: string;
  sprite: string;
  /** Kicker text rendered after the `▸` marquee arrow. */
  label: string;
  /** Pixel-font tagline shown as the screen's `<h1>`. */
  tagline: string;
};

export const GAME_VISUALS: Record<LobbyGameId, GameVisual> = {
  wiki: { accent: "var(--wiki)", sprite: "🌐", label: "Wikipedia", tagline: "SPEED RUN" },
  rapid_fire: { accent: "var(--rapid)", sprite: "⚡", label: "Rapid Fire", tagline: "QUICK DRAW" },
  pinpoint: { accent: "var(--pin)", sprite: "🎯", label: "Pinpoint", tagline: "NAME IT" },
  picture: { accent: "var(--pic)", sprite: "🖼️", label: "Picture Illustration", tagline: "DECODE IT" },
  four_pics: { accent: "var(--four)", sprite: "🃏", label: "Four Pics, One Lie", tagline: "ODD ONE OUT" },
  word_hunt: { accent: "var(--word)", sprite: "🔤", label: "Word Hunt", tagline: "TRACE IT" },
  crossword: { accent: "var(--cross)", sprite: "📝", label: "Crossword", tagline: "FILL IT IN" },
};

/** Static lobby copy and routes — session status comes from `GET /players/me/sessions`. */
export const GAME_TILES: readonly GameTileDefinition[] = [
  {
    id: "wiki",
    name: "Wikipedia Speed Run",
    description: "Navigate Wikipedia by links only — reach the target page as fast as you can.",
    href: "/wiki",
    maxPoints: GAME_MAX_POINTS.wiki,
  },
  {
    id: "rapid_fire",
    name: "Rapid Fire Quiz",
    description: "Fast multiple-choice questions with a countdown — answer quickly for speed bonuses.",
    href: "/rapid-fire",
    maxPoints: GAME_MAX_POINTS.rapid_fire,
  },
  {
    id: "pinpoint",
    name: "Pinpoint",
    description: "Word-association puzzles — guess the hidden category from thematic clues, one at a time.",
    href: "/pinpoint",
    maxPoints: GAME_MAX_POINTS.pinpoint,
  },
  {
    id: "picture",
    name: "Picture Illustration",
    description: "Images reveal a concept step by step — type the answer early for more points.",
    href: "/picture",
    maxPoints: GAME_MAX_POINTS.picture,
  },
  {
    id: "four_pics",
    name: "Four Pics, One Lie",
    description: "Spot the image that does not belong with the other three.",
    href: "/four-pics",
    maxPoints: GAME_MAX_POINTS.four_pics,
  },
  {
    id: "word_hunt",
    name: "Word Hunt",
    description: "Trace hidden words in a letter grid using riddle clues.",
    href: "/word-hunt",
    maxPoints: GAME_MAX_POINTS.word_hunt,
  },
  {
    id: "crossword",
    name: "Crossword",
    description: "Fill in a classic intersecting-word grid from Across and Down clues.",
    href: "/crossword",
    maxPoints: GAME_MAX_POINTS.crossword,
  },
];
