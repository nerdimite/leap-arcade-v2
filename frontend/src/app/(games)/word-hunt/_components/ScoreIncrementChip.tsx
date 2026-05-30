"use client";

import { WORD_HUNT_BASE_PER_WORD } from "@/lib/constants";

type Props = {
  visible: boolean;
};

export function ScoreIncrementChip({ visible }: Props) {
  if (!visible) {
    return null;
  }

  return (
    <span
      aria-live="polite"
      className="animate-score-rise pointer-events-none absolute -right-3 -top-3 font-pixel text-[11px] text-four motion-reduce:animate-none"
    >
      +{WORD_HUNT_BASE_PER_WORD}
    </span>
  );
}
