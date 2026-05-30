import { PINPOINT_CLUE_COUNT } from "../_hooks/usePinpointReducer";

import { cn } from "@/lib/utils";

export type ClueBadgeRowProps = {
  cluesRevealed: number;
  clues: string[];
  shakeBadgeIndex?: number | null;
};

export function ClueBadgeRow(props: ClueBadgeRowProps) {
  const { cluesRevealed, clues, shakeBadgeIndex = null } = props;

  return (
    <ol
      className="grid grid-cols-5 gap-2"
      aria-label="Clue badges"
    >
      {Array.from({ length: PINPOINT_CLUE_COUNT }, (_, index) => {
        const isRevealed = index < cluesRevealed;
        const isShaking = shakeBadgeIndex === index;

        return (
          <li
            key={index}
            data-testid="clue-badge-slot"
            data-shake={isShaking ? "true" : undefined}
            className={cn(
              "flex min-h-16 items-center justify-center rounded-[var(--radius)] border-2 px-2 py-3 text-center text-[13px] font-medium transition-all duration-300",
              isRevealed
                ? "border-[var(--accent)]/40 bg-[var(--accent)]/12 text-ink animate-pinpoint-badge-reveal"
                : "border-line bg-bg-2 text-ink-faint blur-[1px]",
              isShaking && "animate-pinpoint-badge-shake border-cross bg-cross/20 text-cross",
            )}
          >
            {isRevealed ? clues[index] : "Locked"}
          </li>
        );
      })}
    </ol>
  );
}
