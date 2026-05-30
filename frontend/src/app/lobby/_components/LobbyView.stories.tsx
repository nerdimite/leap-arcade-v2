import type { Meta, StoryObj } from "@storybook/nextjs-vite"

import type { GameTileProps } from "./GameTile"
import { LobbyView } from "./LobbyView"
import type { MiniLeaderboardRow } from "./MiniLeaderboard"
import { MiniLeaderboard } from "./MiniLeaderboard"

/** Full seven-cabinet roster; each story overlays per-game status + score. */
const ROSTER: Omit<GameTileProps, "badge" | "locked" | "score">[] = [
  {
    gameId: "wiki",
    name: "Wikipedia Speed Run",
    description:
      "Navigate Wikipedia by links only — reach the target page as fast as you can.",
    maxPoints: 1000,
    href: "/wiki",
  },
  {
    gameId: "rapid_fire",
    name: "Rapid Fire Quiz",
    description:
      "Fast multiple-choice questions with a countdown — answer quickly for speed bonuses.",
    maxPoints: 1500,
    href: "/rapid-fire",
  },
  {
    gameId: "pinpoint",
    name: "Pinpoint",
    description:
      "Guess the hidden category from thematic clues, revealed one at a time.",
    maxPoints: 3000,
    href: "/pinpoint",
  },
  {
    gameId: "picture",
    name: "Picture Illustration",
    description:
      "Images reveal a concept step by step — type the answer early for more points.",
    maxPoints: 800,
    href: "/picture",
  },
  {
    gameId: "four_pics",
    name: "Four Pics, One Lie",
    description: "Spot the image that does not belong with the other three.",
    maxPoints: 600,
    href: "/four-pics",
  },
  {
    gameId: "word_hunt",
    name: "Word Hunt",
    description: "Trace hidden words in a letter grid using riddle clues.",
    maxPoints: 1000,
    href: "/word-hunt",
  },
  {
    gameId: "crossword",
    name: "Crossword",
    description:
      "Fill in a classic intersecting-word grid from Across and Down clues.",
    maxPoints: 1500,
    href: "/crossword",
  },
]

type Overlay = Pick<GameTileProps, "badge" | "locked"> & { score?: number }

/** Build the tile list, applying per-game status overlays by gameId. */
function tiles(
  overlays: Partial<Record<GameTileProps["gameId"], Overlay>>
): GameTileProps[] {
  return ROSTER.map((game) => {
    const o = overlays[game.gameId] ?? { badge: "Not started", locked: false }
    return { ...game, badge: o.badge, locked: o.locked, score: o.score }
  })
}

const sidebarEntries: MiniLeaderboardRow[] = [
  {
    rank: 1,
    corp_id: "ri2026",
    display_name: "R. Iyer",
    total_score: 3420,
    games_completed: 6,
  },
  {
    rank: 2,
    corp_id: "sk2026",
    display_name: "S. Khan",
    total_score: 3180,
    games_completed: 5,
  },
  {
    rank: 3,
    corp_id: "pd2026",
    display_name: "P. Das",
    total_score: 2960,
    games_completed: 5,
  },
  {
    rank: 4,
    corp_id: "nr2026",
    display_name: "N. Roy",
    total_score: 2510,
    games_completed: 4,
  },
  {
    rank: 5,
    corp_id: "vn2026",
    display_name: "V. Nair",
    total_score: 2300,
    games_completed: 4,
  },
]

const meta = {
  component: LobbyView,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof LobbyView>

export default meta

type Story = StoryObj<typeof meta>

export const AllAvailable: Story = {
  args: {
    tiles: tiles({}),
    sidebar: <MiniLeaderboard entries={sidebarEntries} currentCorpId={null} />,
  },
}

export const MixedStatuses: Story = {
  args: {
    tiles: tiles({
      wiki: { badge: "In progress", locked: false, score: 420 },
      rapid_fire: { badge: "Completed", locked: true, score: 1150 },
      four_pics: { badge: "Abandoned", locked: true, score: 0 },
      picture: { badge: "Completed", locked: false, score: 560 },
    }),
    sidebar: (
      <MiniLeaderboard
        entries={sidebarEntries}
        currentCorpId="sk2026"
        pinnedEntry={{
          rank: 9,
          corp_id: "am2026",
          display_name: "A. Mehta",
          total_score: 1250,
          games_completed: 3,
        }}
      />
    ),
  },
}

export const AllCompleted: Story = {
  args: {
    tiles: tiles({
      wiki: { badge: "Completed", locked: true, score: 820 },
      rapid_fire: { badge: "Completed", locked: true, score: 1150 },
      pinpoint: { badge: "Completed", locked: true, score: 2100 },
      picture: { badge: "Completed", locked: false, score: 700 },
      four_pics: { badge: "Abandoned", locked: true, score: 0 },
      word_hunt: { badge: "Completed", locked: true, score: 910 },
      crossword: { badge: "Completed", locked: true, score: 1300 },
    }),
    sidebar: (
      <MiniLeaderboard entries={sidebarEntries} currentCorpId="ri2026" />
    ),
  },
}

export { AllAvailable as Default }
