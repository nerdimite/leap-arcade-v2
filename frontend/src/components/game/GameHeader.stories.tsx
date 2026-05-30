import type { Meta, StoryObj } from "@storybook/nextjs-vite"
import type { CSSProperties } from "react"

import { GAME_VISUALS } from "@/lib/game-tiles"

import { GameHeader } from "./GameHeader"
import { ScoreReadout } from "./ScoreReadout"

/**
 * `GameHeader` is the in-page marquee bar, not a full game shell: each
 * `<Game>View` still owns its page container, the `--accent` wrapper, and the
 * playing/result switch. The accent is inherited, so these stories supply it
 * via a decorator keyed off the story's `gameId`, mirroring each View's root.
 */
const meta = {
  component: GameHeader,
  parameters: { layout: "fullscreen" },
  decorators: [
    (Story, { args }) => (
      <div
        className="mx-auto max-w-2xl p-6"
        style={
          { "--accent": GAME_VISUALS[args.gameId].accent } as CSSProperties
        }
      >
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof GameHeader>

export default meta

type Story = StoryObj<typeof meta>

/** The common case: identity plate, a progress line, and a score readout. */
export const ScoreOnly: Story = {
  args: {
    gameId: "rapid_fire",
    progress: "Question 3 of 10",
    children: <ScoreReadout score={420} />,
  },
}

/** A game-specific control sits left of the score in the right-side cluster. */
export const WithMeta: Story = {
  args: {
    gameId: "picture",
    progress: "2 of 8 solved",
    children: (
      <>
        <span className="rounded-[var(--radius)] border-2 border-line bg-panel px-3 py-1.5 font-pixel text-[12px] text-[var(--accent)] tabular-nums shadow-[var(--shadow-cabinet-sm)]">
          ⏱ 1:24
        </span>
        <ScoreReadout score={680} />
      </>
    ),
  },
}

/** Crossword pattern: score plate (with `+points` accessory) plus an action. */
export const WithAction: Story = {
  args: {
    gameId: "crossword",
    progress: "Solved 4/12",
    children: (
      <>
        <ScoreReadout
          score={800}
          accessory={
            <span className="pointer-events-none absolute -top-3 -right-3 font-pixel text-[11px] text-four">
              +200
            </span>
          }
        />
        <button
          type="button"
          className="inline-flex h-11 items-center justify-center rounded-[var(--radius)] border-2 border-[var(--accent)] bg-[var(--accent)] px-5 text-[12px] font-extrabold tracking-[1.5px] text-bg uppercase shadow-[var(--shadow-cabinet-sm)]"
        >
          Submit
        </button>
      </>
    ),
  },
}

/** No right-side cluster: the plate and progress line stand alone. */
export const PlateOnly: Story = {
  args: {
    gameId: "word_hunt",
    progress: "Found 3 / 9",
  },
}

/** Denser variant for sticky/space-tight headers (Wikipedia Speed Run). */
export const Compact: Story = {
  args: {
    gameId: "wiki",
    compact: true,
    progress: "Puzzle 2 of 5",
    children: <ScoreReadout score={180} />,
  },
}
