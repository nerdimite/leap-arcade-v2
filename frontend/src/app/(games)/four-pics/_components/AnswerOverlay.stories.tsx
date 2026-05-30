import type { Meta, StoryObj } from "@storybook/nextjs-vite"

import { AnswerOverlay } from "./AnswerOverlay"

const meta = {
  component: AnswerOverlay,
  decorators: [
    (Story) => (
      <div className="relative aspect-square max-w-xs overflow-hidden rounded-xl border bg-muted">
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof AnswerOverlay>

export default meta

type Story = StoryObj<typeof meta>

export const Correct: Story = {
  args: {
    correct: true,
    score: 142,
    timeBonus: 42,
    selectedIndex: 2,
  },
}

export const Wrong: Story = {
  args: {
    correct: false,
    score: 0,
    timeBonus: 0,
    selectedIndex: 1,
  },
}

export { Correct as Default }
