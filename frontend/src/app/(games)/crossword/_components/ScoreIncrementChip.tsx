"use client"

import { CROSSWORD_BASE_PER_ENTRY } from "@/lib/constants"

type Props = {
  visible: boolean
}

export function ScoreIncrementChip({ visible }: Props) {
  if (!visible) {
    return null
  }

  return (
    <span
      aria-live="polite"
      className="pointer-events-none absolute -top-3 -right-3 animate-score-rise font-pixel text-[11px] text-four motion-reduce:animate-none"
    >
      +{CROSSWORD_BASE_PER_ENTRY}
    </span>
  )
}
