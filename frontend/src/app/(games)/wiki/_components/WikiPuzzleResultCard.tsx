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
      <h1 className="text-lg font-semibold">Puzzle complete</h1>
      <div className="rounded-lg border bg-card p-4 shadow-sm">
        <p className="text-sm text-muted-foreground">Target revealed</p>
        <p className="text-lg font-medium">{targetTitle}</p>
        <dl className="mt-3 grid grid-cols-2 gap-2 text-sm">
          <dt className="text-muted-foreground">Clicks</dt>
          <dd className="font-mono tabular-nums">{steps}</dd>
          <dt className="text-muted-foreground">Score</dt>
          <dd className="font-mono tabular-nums">{score}</dd>
          <dt className="text-muted-foreground">Time (ms)</dt>
          <dd className="font-mono tabular-nums">{timeMs ?? "—"}</dd>
          <dt className="text-muted-foreground">Total so far</dt>
          <dd className="font-mono tabular-nums">{totalScore}</dd>
        </dl>
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
