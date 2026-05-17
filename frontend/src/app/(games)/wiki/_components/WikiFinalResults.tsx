/** Wiki session wrap-up listing per-puzzle summaries. */

import type { WikiPuzzleResult } from "@/services/wiki/schema";

export type WikiFinalResultsProps = {
  totalScore: number;
  results: WikiPuzzleResult[];
  title?: string;
  subtitle?: string;
};

export function WikiFinalResults(props: WikiFinalResultsProps) {
  const { totalScore, results, title, subtitle } = props;
  const ordered = [...results].sort((a, b) => a.puzzle_index - b.puzzle_index);
  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <header className="space-y-1">
        <h1 className="text-xl font-semibold">{title ?? "Wikipedia Speed Run"}</h1>
        <p className="text-muted-foreground">{subtitle ?? "All puzzles complete."}</p>
        <p className="text-2xl font-bold tabular-nums">
          Total score <span className="text-primary">{totalScore}</span>
        </p>
      </header>
      <ul className="grid gap-3 sm:grid-cols-2">
        {ordered.map((r) => (
          <li
            key={r.round_id}
            className="rounded-lg border bg-card p-4 shadow-sm"
          >
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Puzzle {r.puzzle_index}
            </p>
            <p className="mt-1 font-medium leading-snug">{r.clue}</p>
            <p className="mt-2 text-sm text-muted-foreground">Target</p>
            <p className="text-lg font-semibold leading-snug">{r.target_title}</p>
            <dl className="mt-3 grid grid-cols-2 gap-2 text-sm">
              <dt className="text-muted-foreground">Score</dt>
              <dd className="font-mono tabular-nums text-right">{r.score}</dd>
              <dt className="text-muted-foreground">Clicks</dt>
              <dd className="font-mono tabular-nums text-right">{r.steps_taken}</dd>
              <dt className="text-muted-foreground">Time (ms)</dt>
              <dd className="font-mono tabular-nums text-right">{r.time_ms ?? "—"}</dd>
            </dl>
          </li>
        ))}
      </ul>
    </div>
  );
}
