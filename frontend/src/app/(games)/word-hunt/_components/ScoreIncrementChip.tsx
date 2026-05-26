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
      className="pointer-events-none absolute -right-2 -top-2 animate-bounce text-sm font-semibold text-green-600"
    >
      +{WORD_HUNT_BASE_PER_WORD}
    </span>
  );
}
