import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { fn } from "storybook/test";

import { RapidFireErrorState } from "./RapidFireErrorState";

const meta = {
  component: RapidFireErrorState,
  args: {
    onBackToLobby: fn(),
  },
} satisfies Meta<typeof RapidFireErrorState>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    message: "Could not submit your answer. Please refresh the page.",
  },
};
