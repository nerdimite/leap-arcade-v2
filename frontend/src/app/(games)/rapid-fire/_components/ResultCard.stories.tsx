import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { fn } from "storybook/test";

import type { Result } from "@/services/rapid_fire/schema";

import { ResultCard } from "./ResultCard";

const midResult: Result = {
  score: 42,
  correct_count: 6,
  wrong_count: 4,
  skipped_count: 1,
  time_taken_seconds: 92.3,
};

const meta = {
  component: ResultCard,
  args: {
    onBackToLobby: fn(),
  },
} satisfies Meta<typeof ResultCard>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    score: midResult.score,
    correctCount: midResult.correct_count,
    wrongCount: midResult.wrong_count,
    skippedCount: midResult.skipped_count,
    timeTakenSeconds: midResult.time_taken_seconds,
  },
};
