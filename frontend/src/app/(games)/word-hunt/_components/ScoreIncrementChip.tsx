"use client"

import { WORD_HUNT_BASE_PER_WORD } from "@/lib/constants"

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
      +{WORD_HUNT_BASE_PER_WORD}
    </span>
  )
}
