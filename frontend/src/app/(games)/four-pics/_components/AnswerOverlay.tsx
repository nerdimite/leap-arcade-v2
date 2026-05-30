/** 2s feedback overlay after a tap — correct shows score breakdown; wrong shows +0 only. */

import { FOUR_PICS_BASE_SCORE } from "@/lib/constants";
import { cn } from "@/lib/utils";

export type AnswerOverlayProps = {
  correct: boolean;
  score: number;
  timeBonus: number;
  selectedIndex: number;
};

export function AnswerOverlay(props: AnswerOverlayProps) {
  const { correct, score, timeBonus, selectedIndex } = props;

  return (
    <div
      className={cn(
        "pointer-events-none absolute inset-0 z-20 flex items-center justify-center rounded-[var(--radius)]",
        correct ? "bg-four/20" : "bg-cross/20",
      )}
      aria-live="polite"
      role="status"
    >
      <p
        className={cn(
          "rounded-[var(--radius)] border-2 bg-panel px-4 py-3 text-center text-[15px] font-semibold tabular-nums shadow-[var(--shadow-cabinet)]",
          correct ? "border-four text-four" : "border-cross text-cross",
        )}
      >
        {correct
          ? `+${FOUR_PICS_BASE_SCORE} base + ${timeBonus} bonus = ${score} pts`
          : "+0 pts"}
      </p>
      {/* selectedIndex reserved for parent tile ring on correct only */}
      <span className="sr-only">Selected option {selectedIndex + 1}</span>
    </div>
  );
}
