import type { Meta, StoryObj } from "@storybook/nextjs-vite"

import { GameTile } from "./GameTile"

const meta = {
  component: GameTile,
  parameters: { layout: "centered" },
  decorators: [
    (Story) => (
      <div className="w-[340px]">
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof GameTile>

export default meta

type Story = StoryObj<typeof meta>

export const NotStarted: Story = {
  args: {
    gameId: "rapid_fire",
    name: "Rapid Fire Quiz",
    description:
      "Fast multiple-choice questions with a countdown — answer quickly for speed bonuses.",
    maxPoints: 1500,
    badge: "Not started",
    locked: false,
    href: "/rapid-fire",
  },
}

export const InProgress: Story = {
  args: {
    gameId: "wiki",
    name: "Wikipedia Speed Run",
    description:
      "Navigate Wikipedia by links only — reach the target page as fast as you can.",
    maxPoints: 1000,
    badge: "In progress",
    score: 420,
    locked: false,
    href: "/wiki",
  },
}

export const Completed: Story = {
  args: {
    gameId: "four_pics",
    name: "Four Pics, One Lie",
    description: "Spot the image that does not belong with the other three.",
    maxPoints: 600,
    badge: "Completed",
    score: 480,
    locked: true,
    href: "/four-pics",
  },
}

export const Abandoned: Story = {
  args: {
    gameId: "crossword",
    name: "Crossword",
    description:
      "Fill in a classic intersecting-word grid from Across and Down clues.",
    maxPoints: 1500,
    badge: "Abandoned",
    score: 0,
    locked: true,
    href: "/crossword",
  },
}

export { NotStarted as Default }
