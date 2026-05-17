import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { TimerBar } from "./TimerBar";

const meta = {
  component: TimerBar,
} satisfies Meta<typeof TimerBar>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { percentage: 60 },
};

export const Low: Story = {
  args: { percentage: 15 },
};

export const Full: Story = {
  args: { percentage: 100 },
};
