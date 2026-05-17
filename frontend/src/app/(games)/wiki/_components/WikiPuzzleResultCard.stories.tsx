import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { fn } from "storybook/test";

import { WikiPuzzleResultCard } from "./WikiPuzzleResultCard";

const meta = {
  component: WikiPuzzleResultCard,
  args: {
    targetTitle: "Great Barrier Reef",
    steps: 6,
    score: 420,
    timeMs: 88_000,
    totalScore: 1280,
    continuePending: false,
    onContinue: fn(),
  },
} satisfies Meta<typeof WikiPuzzleResultCard>;

export default meta;

type Story = StoryObj<typeof meta>;

export const HasNext: Story = {
  args: {
    hasNext: true,
  },
};

export const ViewFinalResults: Story = {
  args: {
    hasNext: false,
  },
};

export { HasNext as Default };
