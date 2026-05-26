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
        "pointer-events-none absolute inset-0 z-20 flex items-center justify-center rounded-xl",
        kind === "solved" ? "bg-emerald-600/75" : "bg-destructive/75",
      )}
      aria-live="polite"
      role="status"
    >
      <p
        className={cn(
          "rounded-lg px-4 py-3 text-center font-semibold text-lg text-white shadow-lg tabular-nums",
          kind === "solved" ? "bg-emerald-800/90" : "bg-destructive/90",
        )}
      >
        {copy}
      </p>
    </div>
  );
}
