/** 2s verdict reveal after a tap — a score-counting celebration on a correct spot, an
 *  empathetic shake on a miss. The answer is never revealed on a wrong tap. */

import { Check, X } from "lucide-react"

import { FOUR_PICS_BASE_SCORE } from "@/lib/constants"
import { useCountUp } from "../_lib/use-count-up"
import { Confetti } from "./Confetti"

export type AnswerOverlayProps = {
  correct: boolean
  score: number
  timeBonus: number
  selectedIndex: number
}

/**
 * Louder praise the faster you spot it — the host gets more impressed the bigger the
 * time bonus. Game-show voice: short, punchy, never solemn. The base score is fixed,
 * so the bonus is the only signal of how sharp the read was.
 */
function correctHeadline(timeBonus: number): string {
  if (timeBonus >= 40) return "EAGLE EYE"
  if (timeBonus >= 25) return "SHARP SPOT"
  if (timeBonus >= 10) return "GOOD CATCH"
  if (timeBonus > 0) return "NICE ONE"
  return "GOT IT"
}

export function AnswerOverlay(props: AnswerOverlayProps) {
  const { correct, score, timeBonus, selectedIndex } = props
  const count = useCountUp(score)

  if (!correct) {
    return (
      <div
        className="pointer-events-none absolute inset-0 z-40 flex items-center justify-center"
        aria-live="polite"
        role="status"
      >
        <div className="rounded-[var(--radius)] border-2 border-cross bg-panel px-7 py-5 text-center shadow-[var(--shadow-cabinet)] motion-safe:animate-rf-verdict-wrong">
          <p className="flex items-center justify-center gap-1.5 font-pixel text-[13px] leading-none text-cross">
            <X aria-hidden className="size-3.5 stroke-[3]" />
            NOT THAT ONE
          </p>
          <p className="mt-3 text-[14px] text-ink-dim">
            No points. Eyes up for the next.
          </p>
        </div>
        <span className="sr-only">
          Wrong. You selected option {selectedIndex + 1}. Zero points.
        </span>
      </div>
    )
  }

  return (
    <div
      className="pointer-events-none absolute inset-0 z-40 flex items-center justify-center"
      aria-live="polite"
      role="status"
    >
      <div className="relative overflow-visible rounded-[var(--radius)] border-2 border-four bg-panel px-7 py-5 text-center shadow-[var(--shadow-cabinet)] motion-safe:animate-rf-verdict-in">
        <Confetti className="top-3 left-1/2" />
        <p className="flex items-center justify-center gap-1.5 font-pixel text-[13px] leading-none text-four">
          <Check aria-hidden className="size-3.5 stroke-[3]" />
          {correctHeadline(timeBonus)}
        </p>
        <p className="mt-3 font-pixel text-[26px] leading-none text-four tabular-nums">
          +{count}
        </p>
        <p className="mt-2.5 text-[10px] font-bold tracking-[1px] text-ink-faint uppercase tabular-nums">
          {timeBonus > 0
            ? `${FOUR_PICS_BASE_SCORE} base + ${timeBonus} time`
            : `${FOUR_PICS_BASE_SCORE} base`}
        </p>
      </div>
      <span className="sr-only">
        Correct. You selected option {selectedIndex + 1}. {score} points.
      </span>
    </div>
  )
}
