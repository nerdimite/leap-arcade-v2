import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { ScoreReadout } from "./ScoreReadout";

const meta = {
  component: ScoreReadout,
} satisfies Meta<typeof ScoreReadout>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { score: 420 },
};

export const Zero: Story = {
  args: { score: 0 },
};

/** With a `+points` increment chip anchored to the plate's top-right corner. */
export const WithAccessory: Story = {
  args: {
    score: 800,
    accessory: (
      <span className="pointer-events-none absolute -right-3 -top-3 font-pixel text-[11px] text-four">
        +200
      </span>
    ),
  },
};
