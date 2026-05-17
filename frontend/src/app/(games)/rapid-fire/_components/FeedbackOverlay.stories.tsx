import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { FeedbackOverlay } from "./FeedbackOverlay";

const meta = {
  component: FeedbackOverlay,
} satisfies Meta<typeof FeedbackOverlay>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Correct: Story = {
  args: {
    lastCorrect: true,
    currentScore: 12,
  },
};

export const Wrong: Story = {
  args: {
    lastCorrect: false,
    currentScore: 4,
  },
};

export { Correct as Default };
