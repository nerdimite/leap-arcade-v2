import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { LeaderboardTable, type LeaderboardTableRow } from "./LeaderboardTable";

const mockEntries: LeaderboardTableRow[] = [
  { rank: 1, corp_id: "c01", display_name: "Avery Kim", total_score: 2840, games_completed: 5 },
  { rank: 2, corp_id: "c02", display_name: "Jordan Lee", total_score: 2610, games_completed: 5 },
  { rank: 3, corp_id: "c03", display_name: "Riley Chen", total_score: 2395, games_completed: 4 },
  { rank: 4, corp_id: "c04", display_name: "Casey Singh", total_score: 2180, games_completed: 5 },
  { rank: 5, corp_id: "c05", display_name: "Morgan Patel", total_score: 1920, games_completed: 3 },
  { rank: 6, corp_id: "c06", display_name: "Quinn Garcia", total_score: 1650, games_completed: 4 },
  { rank: 7, corp_id: "c07", display_name: "Blake Nguyen", total_score: 1420, games_completed: 3 },
  { rank: 8, corp_id: "c08", display_name: "Sage Okonkwo", total_score: 980, games_completed: 2 },
];

const meta = {
  component: LeaderboardTable,
  args: {
    entries: mockEntries,
  },
} satisfies Meta<typeof LeaderboardTable>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Empty: Story = {
  args: {
    entries: [],
  },
};
