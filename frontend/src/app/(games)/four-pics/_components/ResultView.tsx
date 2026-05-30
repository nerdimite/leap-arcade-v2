/** End-of-run summary — per-question rows by number only (no images). */

import { ArrowLeft } from "lucide-react"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import type { Result, ResultQuestion } from "@/services/four_pics/schema"
import { useCountUp } from "../_lib/use-count-up"
import { Confetti } from "./Confetti"

export type ResultViewProps = {
  result: Result
  onBackToLobby: () => void
}

/** Game-show sign-off keyed to how clean the run was. Short, never solemn. */
function runHeadline(result: Result): string {
  if (result.questions_correct === 0) return "Run complete"
  if (result.questions_wrong === 0 && result.questions_not_reached === 0)
    return "Flawless run"
  if (result.questions_wrong === 0) return "Sharp run"
  if (result.questions_correct > result.questions_wrong) return "Good run"
  return "Run complete"
}

function statusBadge(status: ResultQuestion["status"]): {
  label: string
  className: string
} {
  switch (status) {
    case "correct":
      return {
        label: "Correct",
        className: "border-four/40 bg-four/12 text-four",
      }
    case "wrong":
      return {
        label: "Wrong",
        className: "border-cross/40 bg-cross/12 text-cross",
      }
    case "not_reached":
      return {
        label: "Not reached",
        className: "border-line bg-bg-2 text-ink-faint",
      }
  }
}

export function ResultView({ result, onBackToLobby }: ResultViewProps) {
  const rows = [...result.questions].map((q, index) => ({
    ...q,
    questionNumber: index + 1,
  }))
  const score = useCountUp(result.score)
  const cleanRun = result.questions_correct > 0 && result.questions_wrong === 0

  return (
    <div className="mx-auto flex max-w-lg flex-col gap-6 p-6 pb-10">
      <div className="overflow-hidden rounded-[var(--radius)] border-2 border-line bg-panel shadow-[var(--shadow-cabinet)]">
        <div
          className="h-2 bg-[var(--accent,var(--four))]"
          style={{ boxShadow: "0 0 18px var(--accent, var(--four))" }}
        />
        <div className="relative p-6">
          {cleanRun ? <Confetti className="top-10 left-10" /> : null}
          <p className="font-pixel text-[9px] tracking-[2px] text-[var(--accent,var(--four))] uppercase">
            ▸ {runHeadline(result)}
          </p>
          <p className="mt-4 font-pixel text-[26px] leading-none text-four tabular-nums">
            {score}
          </p>
          <p className="mt-2 text-[11px] font-bold tracking-[1px] text-ink-faint uppercase">
            Total score
          </p>
          <ul className="mt-5 flex flex-wrap gap-3 text-[14px] text-ink-dim">
            <li>
              <span className="font-pixel text-[11px] text-four tabular-nums">
                {result.questions_correct}
              </span>{" "}
              correct
            </li>
            <li>
              <span className="font-pixel text-[11px] text-cross tabular-nums">
                {result.questions_wrong}
              </span>{" "}
              wrong
            </li>
            <li>
              <span className="font-pixel text-[11px] text-ink-faint tabular-nums">
                {result.questions_not_reached}
              </span>{" "}
              not reached
            </li>
          </ul>
        </div>
      </div>

      <section className="space-y-3">
        <h2 className="text-[10px] font-bold tracking-[1px] text-ink-faint uppercase">
          Per question
        </h2>
        <div className="overflow-hidden rounded-[var(--radius)] border-2 border-line">
          <table className="w-full text-[14px]">
            <thead>
              <tr className="bg-bg-2 text-left text-[10px] font-bold tracking-[1px] text-ink-faint uppercase">
                <th className="px-4 py-2.5 font-bold">#</th>
                <th className="px-4 py-2.5 font-bold">Status</th>
                <th className="px-4 py-2.5 text-right font-bold">Score</th>
                <th className="px-4 py-2.5 text-right font-bold">Bonus</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const badge = statusBadge(row.status)
                return (
                  <tr
                    key={row.question_id}
                    className="border-t-[1.5px] border-line"
                  >
                    <td className="px-4 py-3 font-pixel text-[11px] text-ink-faint tabular-nums">
                      {row.questionNumber}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={cn(
                          "inline-flex rounded-full border-2 px-2.5 py-0.5 text-[11px] font-bold tracking-[0.5px] uppercase",
                          badge.className
                        )}
                      >
                        {badge.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right font-pixel text-[11px] text-ink tabular-nums">
                      {row.score}
                    </td>
                    <td className="px-4 py-3 text-right text-ink-dim tabular-nums">
                      {row.time_bonus}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </section>

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
