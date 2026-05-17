import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import type { MiniLeaderboardRow } from "./MiniLeaderboard";
import { MiniLeaderboard } from "./MiniLeaderboard";

const sampleEntries: MiniLeaderboardRow[] = [
  { rank: 1, corp_id: "corp-alpha", display_name: "Alpha", total_score: 420, games_completed: 5 },
  { rank: 2, corp_id: "corp-beta", display_name: "Beta", total_score: 380, games_completed: 4 },
  { rank: 3, corp_id: "corp-gamma", display_name: "Gamma", total_score: 350, games_completed: 5 },
  { rank: 4, corp_id: "corp-delta", display_name: "Delta", total_score: 300, games_completed: 3 },
  { rank: 5, corp_id: "corp-self", display_name: "You", total_score: 280, games_completed: 4 },
  { rank: 6, corp_id: "corp-zeta", display_name: "Zeta", total_score: 260, games_completed: 4 },
];

const meta = {
  component: MiniLeaderboard,
} satisfies Meta<typeof MiniLeaderboard>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    entries: sampleEntries,
    currentCorpId: "corp-self",
  },
};

export const WithPinnedRow: Story = {
  args: {
    entries: sampleEntries
      .filter((row) => row.corp_id !== "corp-self")
      .slice(0, 5)
      .map((row, i) => ({ ...row, rank: i + 1 })),
    currentCorpId: "corp-self",
    pinnedEntry: {
      rank: 12,
      corp_id: "corp-self",
      display_name: "You",
      total_score: 280,
      games_completed: 4,
    },
  },
};
