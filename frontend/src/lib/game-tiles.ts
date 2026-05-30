import type { LobbyGameId } from "@/lib/constants";
import { GAME_MAX_POINTS } from "@/lib/constants";

export type GameTileDefinition = {
  id: LobbyGameId;
  name: string;
  description: string;
  href: string;
  maxPoints: (typeof GAME_MAX_POINTS)[LobbyGameId];
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
