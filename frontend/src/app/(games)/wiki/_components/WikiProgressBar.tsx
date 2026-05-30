/** Determinate segment progress across wiki puzzles. */

import { cn } from "@/lib/utils";

export type WikiProgressBarProps = {
  puzzleIndex: number;
  puzzleCount: number;
  completedCount: number;
};

export function WikiProgressBar(props: WikiProgressBarProps) {
  const { puzzleIndex, puzzleCount, completedCount } = props;
  return (
    <div
      className="flex gap-1"
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={puzzleCount}
      aria-valuenow={completedCount}
      aria-label={`${completedCount} of ${puzzleCount} puzzles completed`}
    >
      {Array.from({ length: puzzleCount }, (_, i) => {
        const idx = i + 1;
        const done = idx <= completedCount;
        const current = idx === puzzleIndex;
        return (
          <div
            key={idx}
            className={cn(
              "h-2 min-w-[1.5rem] flex-1 rounded-full transition-colors",
              done && "bg-[var(--accent,var(--wiki))]",
              !done &&
                current &&
                "bg-[var(--accent,var(--wiki))]/35 ring-2 ring-[var(--accent,var(--wiki))] ring-offset-2 ring-offset-bg",
              !done && !current && "bg-line",
            )}
          />
        );
      })}
    </div>
  );
}
