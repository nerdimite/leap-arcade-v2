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
              "flex min-h-16 items-center justify-center rounded-lg border px-2 py-3 text-center text-sm font-medium transition-all duration-300",
              isRevealed
                ? "border-primary/30 bg-primary/10 text-foreground animate-pinpoint-badge-reveal"
                : "border-muted bg-muted/40 text-muted-foreground blur-[1px]",
              isShaking && "animate-pinpoint-badge-shake bg-destructive/20 text-destructive",
            )}
          >
            {isRevealed ? clues[index] : "Locked"}
          </li>
        );
      })}
    </ol>
  );
}
