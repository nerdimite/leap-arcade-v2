import type { Meta, StoryObj } from "@storybook/nextjs-vite"

import { WikiProgressBar } from "./WikiProgressBar"

const meta = {
  component: WikiProgressBar,
  args: {
    puzzleCount: 5,
    puzzleIndex: 3,
    completedCount: 2,
  },
} satisfies Meta<typeof WikiProgressBar>

export default meta

type Story = StoryObj<typeof meta>

export const Default: Story = {}
