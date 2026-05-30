import type { Meta, StoryObj } from "@storybook/nextjs-vite"

import { Stopwatch } from "./Stopwatch"

function startedAtSecondsAgo(seconds: number): string {
  return new Date(Date.now() - seconds * 1000).toISOString()
}

const meta = {
  component: Stopwatch,
} satisfies Meta<typeof Stopwatch>

export default meta

type Story = StoryObj<typeof meta>

export const Fresh: Story = {
  args: {
    startedAt: startedAtSecondsAgo(5),
  },
}

export const MidGame: Story = {
  args: {
    startedAt: startedAtSecondsAgo(22),
  },
}

export const PastDecay: Story = {
  args: {
    startedAt: startedAtSecondsAgo(45),
  },
}

export { Fresh as Default }
