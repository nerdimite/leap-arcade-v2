/** Between-round summary after completing a wiki puzzle. */

import { Button } from "@/components/ui/button";

export type WikiPuzzleResultCardProps = {
  targetTitle: string;
  steps: number;
  score: number;
  timeMs: number | null | undefined;
  totalScore: number;
  hasNext: boolean;
  continuePending: boolean;
  onContinue: () => void;
};

export function WikiPuzzleResultCard(props: WikiPuzzleResultCardProps) {
  const {
    targetTitle,
    steps,
    score,
    timeMs,
    totalScore,
    hasNext,
    continuePending,
    onContinue,
  } = props;
  return (
    <div className="mx-auto flex max-w-lg flex-col gap-4 p-6">
      <div className="overflow-hidden rounded-[var(--radius)] border-2 border-line bg-panel shadow-[var(--shadow-cabinet)]">
        <div
          className="h-2 bg-[var(--accent,var(--wiki))]"
          style={{ boxShadow: "0 0 18px var(--accent, var(--wiki))" }}
        />
        <div className="p-6">
          <h1 className="font-pixel text-[9px] uppercase tracking-[2px] text-[var(--accent,var(--wiki))]">
            <span aria-hidden>▸ </span>Puzzle complete
          </h1>
          <p className="mt-4 text-[11px] font-bold uppercase tracking-[1px] text-ink-faint">
            Target revealed
          </p>
          <p className="mt-1 text-[18px] font-semibold text-ink">{targetTitle}</p>
          <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-2 text-[14px]">
            <dt className="text-ink-dim">Clicks</dt>
            <dd className="text-right font-pixel text-[11px] tabular-nums text-ink">{steps}</dd>
            <dt className="text-ink-dim">Score</dt>
            <dd className="text-right font-pixel text-[11px] tabular-nums text-four">{score}</dd>
            <dt className="text-ink-dim">Time (ms)</dt>
            <dd className="text-right font-pixel text-[11px] tabular-nums text-ink">{timeMs ?? "—"}</dd>
            <dt className="text-ink-dim">Total so far</dt>
            <dd className="text-right font-pixel text-[11px] tabular-nums text-four">{totalScore}</dd>
          </dl>
        </div>
      </div>
      <Button
        type="button"
        className="w-full sm:w-auto"
        disabled={continuePending}
        onClick={() => void onContinue()}
      >
        {continuePending ? "Loading…" : hasNext ? "Continue to next puzzle" : "View final results"}
      </Button>
    </div>
  );
}
