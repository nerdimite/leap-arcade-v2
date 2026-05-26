import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { ClueListPanel } from "./ClueListPanel";
import { allFoundClues, allUnfoundClues, partialFoundClues } from "../_lib/storyFixtures";

const meta = {
  component: ClueListPanel,
} satisfies Meta<typeof ClueListPanel>;

export default meta;

type Story = StoryObj<typeof meta>;

export const AllUnfound: Story = {
  args: {
    clues: allUnfoundClues,
  },
};

export const Partial: Story = {
  args: {
    clues: partialFoundClues,
  },
};

export const AllFound: Story = {
  args: {
    clues: allFoundClues,
  },
};

export { AllUnfound as Default };
