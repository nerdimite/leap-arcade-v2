import type { Meta, StoryObj } from "@storybook/nextjs-vite"

import type { MiniLeaderboardRow } from "./MiniLeaderboard"
import { MiniLeaderboard } from "./MiniLeaderboard"

const sampleEntries: MiniLeaderboardRow[] = [
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
    corp_id: "am2026",
    display_name: "A. Mehta",
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
  {
    rank: 6,
    corp_id: "zk2026",
    display_name: "Z. Kapoor",
    total_score: 2080,
    games_completed: 4,
  },
]

const meta = {
  component: MiniLeaderboard,
  parameters: { layout: "centered" },
  decorators: [
    (Story) => (
      <div className="w-[320px]">
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof MiniLeaderboard>

export default meta

type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    entries: sampleEntries,
    currentCorpId: "am2026",
    fullBoardHref: "/leaderboard",
  },
}

export const LeadingPlayer: Story = {
  args: {
    entries: sampleEntries,
    currentCorpId: "ri2026",
  },
}

export const WithPinnedRow: Story = {
  args: {
    entries: sampleEntries.slice(0, 5),
    currentCorpId: "jd2026",
    pinnedEntry: {
      rank: 12,
      corp_id: "jd2026",
      display_name: "J. Dube",
      total_score: 1250,
      games_completed: 3,
    },
    fullBoardHref: "/leaderboard",
  },
}

export const Empty: Story = {
  args: {
    entries: [],
    currentCorpId: null,
  },
}
