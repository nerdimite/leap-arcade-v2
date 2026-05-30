/** Wiki session wrap-up listing per-puzzle summaries. */

import type { CSSProperties } from "react";

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
    <div
      className="mx-auto max-w-3xl space-y-6 p-6"
      style={{ "--accent": "var(--wiki)" } as CSSProperties}
    >
      <header className="space-y-2">
        <p className="font-pixel text-[9px] uppercase tracking-[2px] text-[var(--accent)]">
          ▸ {title ?? "Wikipedia Speed Run"}
        </p>
        <p className="text-[15px] text-ink-dim">{subtitle ?? "All puzzles complete."}</p>
        <p className="flex items-baseline gap-2 pt-1 text-[11px] font-bold uppercase tracking-[1px] text-ink-faint">
          Total score{" "}
          <span className="font-pixel text-[22px] tracking-normal tabular-nums text-four">
            {totalScore}
          </span>
        </p>
      </header>
      <ul className="grid gap-3 sm:grid-cols-2">
        {ordered.map((r) => (
          <li
            key={r.round_id}
            className="rounded-[var(--radius)] border-2 border-line bg-panel p-4 shadow-[var(--shadow-cabinet)]"
          >
            <p className="text-[10px] font-bold uppercase tracking-[1px] text-ink-faint">
              Puzzle {r.puzzle_index}
            </p>
            <p className="mt-1.5 font-medium leading-snug text-ink">{r.clue}</p>
            <p className="mt-3 text-[10px] font-bold uppercase tracking-[1px] text-ink-faint">Target</p>
            <p className="text-[17px] font-semibold leading-snug text-ink">{r.target_title}</p>
            <dl className="mt-3 grid grid-cols-2 gap-x-3 gap-y-1.5 text-[14px]">
              <dt className="text-ink-dim">Score</dt>
              <dd className="text-right font-pixel text-[11px] tabular-nums text-four">{r.score}</dd>
              <dt className="text-ink-dim">Clicks</dt>
              <dd className="text-right font-pixel text-[11px] tabular-nums text-ink">{r.steps_taken}</dd>
              <dt className="text-ink-dim">Time (ms)</dt>
              <dd className="text-right font-pixel text-[11px] tabular-nums text-ink">{r.time_ms ?? "—"}</dd>
            </dl>
          </li>
        ))}
      </ul>
    </div>
  );
}
