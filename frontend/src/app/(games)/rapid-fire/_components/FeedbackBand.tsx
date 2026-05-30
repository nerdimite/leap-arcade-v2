/** Full-width verdict band shown at the top of the question card during feedback. */

import { Check, X } from "lucide-react"
import { useEffect, useState } from "react"

import { cn } from "@/lib/utils"

/** Confetti piece trajectories (deterministic, so renders are stable). */
const CONFETTI = [
  {
    dx: "-46px",
    dy: "-30px",
    rot: "-160deg",
    color: "var(--four)",
    delay: "0ms",
  },
  {
    dx: "-26px",
    dy: "-44px",
    rot: "120deg",
    color: "var(--rapid)",
    delay: "20ms",
  },
  {
    dx: "-8px",
    dy: "-50px",
    rot: "-90deg",
    color: "var(--wiki)",
    delay: "0ms",
  },
  {
    dx: "12px",
    dy: "-48px",
    rot: "200deg",
    color: "var(--pin)",
    delay: "40ms",
  },
  {
    dx: "30px",
    dy: "-40px",
    rot: "-140deg",
    color: "var(--four)",
    delay: "10ms",
  },
  {
    dx: "48px",
    dy: "-26px",
    rot: "90deg",
    color: "var(--rapid)",
    delay: "30ms",
  },
  {
    dx: "-38px",
    dy: "-12px",
    rot: "160deg",
    color: "var(--wiki)",
    delay: "50ms",
  },
  {
    dx: "40px",
    dy: "-10px",
    rot: "-110deg",
    color: "var(--four)",
    delay: "60ms",
  },
]

function prefersReducedMotion(): boolean {
  return (
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  )
}

const easeOutQuint = (t: number) => 1 - (1 - t) ** 5

/** Counts up to `target` on mount; jumps straight to it under reduced motion. */
function useCountUp(target: number, durationMs = 360): number {
  const [value, setValue] = useState(
    target <= 0 || prefersReducedMotion() ? target : 0
  )

  useEffect(() => {
    if (target <= 0 || prefersReducedMotion()) {
      setValue(target)
      return
    }
    let raf = 0
    const start = performance.now()
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / durationMs)
      setValue(Math.round(target * easeOutQuint(t)))
      if (t < 1) {
        raf = requestAnimationFrame(tick)
      }
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [target, durationMs])

  return value
}

export function FeedbackBand(props: {
  lastCorrect: boolean
  scoreDelta: number
}) {
  const correct = props.lastCorrect
  const delta = useCountUp(correct ? props.scoreDelta : 0)

  return (
    <div
      aria-live="polite"
      className={cn(
        "relative flex items-center justify-between gap-3 overflow-visible rounded-[var(--radius)] border-2 px-4 py-2.5",
        correct
          ? "border-four bg-four/15 motion-safe:animate-rf-verdict-in"
          : "border-cross bg-cross/15 motion-safe:animate-rf-verdict-wrong"
      )}
    >
      <span
        className={cn(
          "flex items-center gap-1.5 font-pixel text-[13px] leading-none",
          correct ? "text-four" : "text-cross"
        )}
      >
        {correct ? (
          <Check aria-hidden className="size-3.5 stroke-[3]" />
        ) : (
          <X aria-hidden className="size-3.5 stroke-[3]" />
        )}
        {correct ? "CORRECT" : "WRONG"}
      </span>
      {correct && props.scoreDelta > 0 ? (
        <span className="font-pixel text-[14px] text-four tabular-nums">
          +{delta}
        </span>
      ) : null}

      {correct && props.scoreDelta > 0 ? (
        <span className="pointer-events-none absolute top-1/2 right-6 motion-reduce:hidden">
          {CONFETTI.map((p) => (
            <span
              key={`${p.dx}-${p.dy}-${p.rot}`}
              className="absolute block h-1.5 w-1.5 rounded-[1px] motion-safe:animate-rf-confetti"
              style={{
                backgroundColor: p.color,
                animationDelay: p.delay,
                ["--dx" as string]: p.dx,
                ["--dy" as string]: p.dy,
                ["--rot" as string]: p.rot,
              }}
            />
          ))}
        </span>
      ) : null}
    </div>
  )
}
