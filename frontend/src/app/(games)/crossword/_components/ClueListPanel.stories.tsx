import type { Meta, StoryObj } from "@storybook/nextjs-vite"
import { fn } from "storybook/test"
import {
  allSolvedPuzzle,
  emptyPuzzle,
  inProgressPuzzle,
} from "../_lib/storyFixtures"
import { ClueListPanel } from "./ClueListPanel"

const meta = {
  component: ClueListPanel,
  args: {
    activeEntryId: null,
    onClueClick: fn(),
  },
} satisfies Meta<typeof ClueListPanel>

export default meta

type Story = StoryObj<typeof meta>

export const AllUnsolved: Story = {
  args: {
    clues: emptyPuzzle.clues,
  },
}

export const Partial: Story = {
  args: {
    clues: inProgressPuzzle.clues,
    activeEntryId: "down-1",
  },
}

export const AllSolved: Story = {
  args: {
    clues: allSolvedPuzzle.clues,
  },
}

export { AllUnsolved as Default }
