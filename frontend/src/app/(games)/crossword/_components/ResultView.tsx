import { ArrowLeft } from "lucide-react"

import { Button } from "@/components/ui/button"
import { formatMs } from "@/lib/utils"
import type { Result } from "@/services/crossword/schema"

export type ResultViewProps = {
  result: Result
  onBackToLobby: () => void
}

function formatDirection(direction: string): string {
  return direction.charAt(0).toUpperCase() + direction.slice(1).toLowerCase()
}

function scoreBreakdown(result: Result): string | null {
  if (result.base_score === undefined || result.time_bonus === undefined) {
    return null
  }
  return `${result.base_score} (= ${result.solved_count} × 100) + ${result.time_bonus} = ${result.score}`
}

export function ResultView({ result, onBackToLobby }: ResultViewProps) {
  const breakdown = scoreBreakdown(result)

  return (
    <div className="mx-auto flex max-w-lg flex-col gap-6 p-6 pb-10">
      <div className="overflow-hidden rounded-[var(--radius)] border-2 border-line bg-panel shadow-[var(--shadow-cabinet)]">
        <div
          className="h-2 bg-[var(--accent,var(--cross))]"
          style={{ boxShadow: "0 0 18px var(--accent, var(--cross))" }}
        />
        <div className="p-6">
          <p className="font-pixel text-[9px] tracking-[2px] text-[var(--accent,var(--cross))] uppercase">
            ▸ Session complete
          </p>
          <p className="mt-4 font-pixel text-[26px] leading-none text-four tabular-nums">
            {result.score}
          </p>
          <p className="mt-2 text-[11px] font-bold tracking-[1px] text-ink-faint uppercase">
            Total score
          </p>
          {breakdown !== null ? (
            <p className="mt-3 text-[13px] text-ink-dim tabular-nums">
              {breakdown}
            </p>
          ) : null}
          <ul className="mt-4 flex flex-wrap gap-3 text-[14px] text-ink-dim">
            <li>
              <span className="font-pixel text-[11px] text-ink tabular-nums">
                {result.solved_count} / {result.total_entries}
              </span>{" "}
              entries solved
            </li>
            {result.time_elapsed_ms !== undefined ? (
              <li>
                Time{" "}
                <span className="font-pixel text-[11px] text-ink tabular-nums">
                  {formatMs(result.time_elapsed_ms)}
                </span>
              </li>
            ) : null}
          </ul>
        </div>
      </div>

      {result.solved_entries.length > 0 ? (
        <section className="space-y-3">
          <h2 className="text-[10px] font-bold tracking-[1px] text-ink-faint uppercase">
            Entries solved
          </h2>
          <ul className="overflow-hidden rounded-[var(--radius)] border-2 border-line">
            {result.solved_entries.map((entry) => (
              <li
                key={entry.entry_id}
                className="flex flex-col gap-0.5 border-t-[1.5px] border-line bg-bg-2 px-4 py-3 first:border-t-0"
              >
                <span className="font-semibold tracking-[0.5px] text-ink uppercase">
                  <span className="mr-1.5 text-[11px] font-bold tracking-[1px] text-ink-faint uppercase">
                    {entry.number} {formatDirection(entry.direction)}
                  </span>
                  {entry.answer}
                </span>
                <span className="text-[13px] text-ink-dim">{entry.clue}</span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <Button
        type="button"
        size="lg"
        className="w-full"
        onClick={onBackToLobby}
      >
        <ArrowLeft aria-hidden className="size-4" />
        Back to Lobby
      </Button>
    </div>
  )
}
