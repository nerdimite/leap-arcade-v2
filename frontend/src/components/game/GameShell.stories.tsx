import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { GameHeader } from "./GameHeader";
import { GameShell } from "./GameShell";
import { ScoreReadout } from "./ScoreReadout";

/**
 * `GameShell` is the frame each `<Game>View` renders into: it sets the local
 * `--accent` from `gameId`, applies the page container, and renders the slot for
 * the current `state`. These stories flip `state` to show the switch, and the
 * `Result (bleed)` story shows a state that owns its own layout.
 */
const meta = {
  component: GameShell,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof GameShell>;

export default meta;

type Story = StoryObj<typeof meta>;

const stage = (
  <div className="space-y-5">
    <GameHeader gameId="rapid_fire" progress="Question 3 of 15">
      <ScoreReadout score={420} />
    </GameHeader>
    <div className="rounded-[var(--radius)] border-2 border-line bg-panel p-6 shadow-[var(--shadow-cabinet)]">
      <p className="text-[20px] font-semibold leading-snug text-ink">
        Which deployment model gives the customer the least operational responsibility?
      </p>
    </div>
  </div>
);

const resultSlot = (
  <div className="mx-auto max-w-lg p-6">
    <div className="overflow-hidden rounded-[var(--radius)] border-2 border-line bg-panel shadow-[var(--shadow-cabinet)]">
      <div className="h-2 bg-[var(--accent)]" style={{ boxShadow: "0 0 18px var(--accent)" }} />
      <div className="p-6 text-center">
        <p className="font-pixel text-[9px] uppercase tracking-[2px] text-[var(--accent)]">
          ▸ Round complete
        </p>
        <p className="mt-4 font-pixel text-[28px] text-four tabular-nums">1,440</p>
        <p className="mt-2 text-[13px] text-ink-dim">12 correct · 3 wrong</p>
      </div>
    </div>
  </div>
);

const slots = { question: stage, result: resultSlot };

/** The playing stage: shell-owned container at `xl` width on the amber accent. */
export const Playing: Story = {
  args: { gameId: "rapid_fire", state: "question", size: "xl", slots },
};

/** A bleed state owns its own width; the shell contributes only the accent. */
export const ResultBleed: Story = {
  args: {
    gameId: "rapid_fire",
    state: "result",
    size: "xl",
    bleedStates: ["result"],
    slots,
  },
};

/** Same shell, a different game — only the inherited accent changes. */
export const DifferentGame: Story = {
  args: {
    gameId: "crossword",
    state: "question",
    size: "xl",
    slots: {
      question: (
        <div className="space-y-5">
          <GameHeader gameId="crossword" progress="Solved 4 / 12">
            <ScoreReadout score={800} />
          </GameHeader>
          <div className="rounded-[var(--radius)] border-2 border-line bg-panel p-6 text-[15px] text-ink-dim shadow-[var(--shadow-cabinet)]">
            Play surface goes here.
          </div>
        </div>
      ),
    },
  },
};
