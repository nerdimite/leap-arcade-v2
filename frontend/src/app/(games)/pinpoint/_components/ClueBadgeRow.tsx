import { Lock } from "lucide-react";

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
    <ol className="flex flex-col gap-2.5" aria-label="Clue badges">
      {Array.from({ length: PINPOINT_CLUE_COUNT }, (_, index) => {
        const isRevealed = index < cluesRevealed;
        const isShaking = shakeBadgeIndex === index;

        return (
          <li
            key={index}
            data-testid="clue-badge-slot"
            data-shake={isShaking ? "true" : undefined}
            className={cn(
              "flex min-h-[58px] items-center gap-3.5 rounded-[var(--radius)] border-2 px-4 py-3 transition-all duration-300",
              isRevealed
                ? "border-[var(--accent)]/45 bg-[var(--accent)]/12 animate-pinpoint-badge-reveal"
                : "border-line bg-bg-2",
              isShaking && "animate-pinpoint-badge-shake border-cross bg-cross/20",
            )}
          >
            <span
              className={cn(
                "grid size-7 shrink-0 place-items-center rounded-[var(--radius)] font-pixel text-[9px] tabular-nums transition-colors duration-300",
                isRevealed ? "bg-[var(--accent)] text-bg" : "bg-line text-ink-faint",
                isShaking && "bg-cross text-bg",
              )}
            >
              {index + 1}
            </span>
            <span
              className={cn(
                "flex flex-1 items-center gap-2 text-[15px] transition-colors duration-300",
                isRevealed ? "font-medium text-ink" : "text-ink-faint",
                isShaking && "text-cross",
              )}
            >
              {isRevealed ? (
                clues[index]
              ) : (
                <>
                  <Lock aria-hidden className="size-3.5 opacity-50" />
                  Locked
                </>
              )}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
