import type { Meta, StoryObj } from "@storybook/nextjs-vite"

import { FeedbackBand } from "./FeedbackBand"

const meta = {
  component: FeedbackBand,
  decorators: [
    (Story) => (
      <div className="mx-auto max-w-md p-8">
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof FeedbackBand>

export default meta

type Story = StoryObj<typeof meta>

export const Correct: Story = {
  args: { lastCorrect: true, scoreDelta: 120 },
}

export const Wrong: Story = {
  args: { lastCorrect: false, scoreDelta: 0 },
}
