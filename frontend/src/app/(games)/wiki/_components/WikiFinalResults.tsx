/** Wiki session wrap-up listing per-puzzle summaries. */

import type { CSSProperties } from "react"

import type { WikiPuzzleResult } from "@/services/wiki/schema"

export type WikiFinalResultsProps = {
  totalScore: number
  results: WikiPuzzleResult[]
  title?: string
  subtitle?: string
}

export function WikiFinalResults(props: WikiFinalResultsProps) {
  const { totalScore, results, title, subtitle } = props
  const ordered = [...results].sort((a, b) => a.puzzle_index - b.puzzle_index)
  return (
    <div
      className="mx-auto max-w-3xl space-y-6 p-6"
      style={{ "--accent": "var(--wiki)" } as CSSProperties}
    >
      <header className="space-y-2">
        <p className="font-pixel text-[9px] tracking-[2px] text-[var(--accent)] uppercase">
          ▸ {title ?? "Wikipedia Speed Run"}
        </p>
        <p className="text-[15px] text-ink-dim">
          {subtitle ?? "All puzzles complete."}
        </p>
        <p className="flex items-baseline gap-2 pt-1 text-[11px] font-bold tracking-[1px] text-ink-faint uppercase">
          Total score{" "}
          <span className="font-pixel text-[22px] tracking-normal text-four tabular-nums">
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
            <p className="text-[10px] font-bold tracking-[1px] text-ink-faint uppercase">
              Puzzle {r.puzzle_index}
            </p>
            <p className="mt-1.5 leading-snug font-medium text-ink">{r.clue}</p>
            <p className="mt-3 text-[10px] font-bold tracking-[1px] text-ink-faint uppercase">
              Target
            </p>
            <p className="text-[17px] leading-snug font-semibold text-ink">
              {r.target_title}
            </p>
            <dl className="mt-3 grid grid-cols-2 gap-x-3 gap-y-1.5 text-[14px]">
              <dt className="text-ink-dim">Score</dt>
              <dd className="text-right font-pixel text-[11px] text-four tabular-nums">
                {r.score}
              </dd>
              <dt className="text-ink-dim">Clicks</dt>
              <dd className="text-right font-pixel text-[11px] text-ink tabular-nums">
                {r.steps_taken}
              </dd>
              <dt className="text-ink-dim">Time (ms)</dt>
              <dd className="text-right font-pixel text-[11px] text-ink tabular-nums">
                {r.time_ms ?? "—"}
              </dd>
            </dl>
          </li>
        ))}
      </ul>
    </div>
  )
}
