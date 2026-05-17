import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { GameTile } from "./GameTile";

const meta = {
  component: GameTile,
} satisfies Meta<typeof GameTile>;

export default meta;

type Story = StoryObj<typeof meta>;

export const NotStarted: Story = {
  args: {
    name: "Rapid Fire Quiz",
    description: "Fast multiple-choice questions with a countdown — answer quickly for speed bonuses.",
    maxPoints: 100,
    badge: "Not started",
    locked: false,
    href: "/rapid-fire",
  },
};

export const InProgress: Story = {
  args: {
    name: "Wikipedia Speed Run",
    description: "Navigate Wikipedia by links only — reach the target page as fast as you can.",
    maxPoints: 100,
    badge: "In progress",
    score: 42,
    locked: false,
    href: "/wiki",
  },
};

export const Completed: Story = {
  args: {
    name: "Picture Illustration",
    description: "Images reveal a concept step by step — type the answer early for more points.",
    maxPoints: 100,
    badge: "Completed",
    score: 88,
    locked: true,
    href: "/picture",
  },
};

export { NotStarted as Default };
