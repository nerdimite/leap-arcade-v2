"use client";

import { CROSSWORD_BASE_PER_ENTRY } from "@/lib/constants";

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
      +{CROSSWORD_BASE_PER_ENTRY}
    </span>
  );
}
