/** Shared score plate: the lit-number cabinet readout every game's header shares. */

import type { ReactNode } from "react"

export type ScoreReadoutProps = {
  score: number
  /**
   * Absolutely-positioned overlay anchored to the plate's top-right corner,
   * e.g. a `+points` increment chip. The plate is `relative` so it can anchor.
   */
  accessory?: ReactNode
}

export function ScoreReadout({ score, accessory }: ScoreReadoutProps) {
  return (
    <div className="relative flex flex-col items-end rounded-[var(--radius)] border-2 border-line bg-panel px-4 py-2 shadow-[var(--shadow-cabinet-sm)]">
      <span className="sr-only">Score: {score}</span>
      <span
        aria-hidden
        className="font-pixel text-[14px] text-four tabular-nums"
      >
        {score}
      </span>
      <span
        aria-hidden
        className="mt-1 text-[10px] font-bold tracking-[1px] text-ink-faint uppercase"
      >
        Score
      </span>
      {accessory}
    </div>
  )
}
