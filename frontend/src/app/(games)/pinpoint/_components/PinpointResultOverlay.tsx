/** 2s terminal puzzle feedback — never reveals the canonical answer. */

import { cn } from "@/lib/utils";

export type PinpointResultOverlayProps = {
  kind: "solved" | "failed";
  baseScore: number;
  timeBonus?: number;
};

export function PinpointResultOverlay(props: PinpointResultOverlayProps) {
  const { kind, baseScore, timeBonus = 0 } = props;

  const copy =
    kind === "solved"
      ? timeBonus > 0
        ? `Correct! +${baseScore} + ${timeBonus} = ${baseScore + timeBonus}`
        : `Correct! +${baseScore}`
      : "Out of clues — +0";

  return (
    <div
      className={cn(
        "pointer-events-none absolute inset-0 z-20 flex items-center justify-center rounded-[var(--radius)]",
        kind === "solved" ? "bg-four/20" : "bg-cross/20",
      )}
      aria-live="polite"
      role="status"
    >
      <p
        className={cn(
          "rounded-[var(--radius)] border-2 bg-panel px-4 py-3 text-center text-[15px] font-semibold tabular-nums shadow-[var(--shadow-cabinet)]",
          kind === "solved" ? "border-four text-four" : "border-cross text-cross",
        )}
      >
        {copy}
      </p>
    </div>
  );
}
