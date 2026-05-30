/** Picture Illustration win celebration: a transient verdict stamp + confetti
 *  over the clue frame, plus a floating +points chip on the score plate. It is
 *  purely non-blocking — the next puzzle is already swapping in underneath, and
 *  the parent clears it on a timer so nothing lingers. */

import { Check } from "lucide-react"

/** Confetti trajectories, weighted toward the violet picture accent + lime score. */
const CONFETTI = [
  {
    dx: "-58px",
    dy: "-40px",
    rot: "-160deg",
    color: "var(--pic)",
    delay: "0ms",
  },
  {
    dx: "-30px",
    dy: "-56px",
    rot: "120deg",
    color: "var(--four)",
    delay: "20ms",
  },
  { dx: "-8px", dy: "-62px", rot: "-90deg", color: "var(--pic)", delay: "0ms" },
  {
    dx: "16px",
    dy: "-58px",
    rot: "200deg",
    color: "var(--rapid)",
    delay: "40ms",
  },
  {
    dx: "36px",
    dy: "-48px",
    rot: "-140deg",
    color: "var(--four)",
    delay: "10ms",
  },
  { dx: "58px", dy: "-34px", rot: "90deg", color: "var(--pic)", delay: "30ms" },
  {
    dx: "-46px",
    dy: "-16px",
    rot: "160deg",
    color: "var(--four)",
    delay: "50ms",
  },
  {
    dx: "48px",
    dy: "-12px",
    rot: "-110deg",
    color: "var(--rapid)",
    delay: "60ms",
  },
]

/** Game-show host verdicts: rotate on solo wins, escalate as the streak builds. */
const SOLO_PHRASES = [
  "NICE",
  "GOT IT",
  "SHARP EYE",
  "CLEAN",
  "SPOT ON",
] as const

function verdictLabel(token: number, streak: number): string {
  if (streak >= 6) return `\u00d7${streak} UNREAL`
  if (streak >= 4) return `\u00d7${streak} ON FIRE`
  if (streak >= 2) return `STREAK \u00d7${streak}`
  return SOLO_PHRASES[token % SOLO_PHRASES.length]
}

function announcement(scoreDelta: number, streak: number): string {
  const points = scoreDelta > 0 ? `, plus ${scoreDelta} points` : ""
  const run = streak >= 2 ? `, ${streak} in a row` : ""
  return `Correct${points}${run}.`
}

export type CorrectBurstProps = {
  scoreDelta: number
  streak: number
  /** Bump to replay the one-shot animation on each new correct answer. */
  token: number
}

export function CorrectBurst({ scoreDelta, streak, token }: CorrectBurstProps) {
  return (
    <div className="pointer-events-none absolute inset-0 z-10 overflow-visible">
      <span className="sr-only" aria-live="polite">
        {announcement(scoreDelta, streak)}
      </span>

      <span
        aria-hidden
        className="absolute inset-0 rounded-[var(--radius)] border-2 border-[var(--accent)] opacity-0 motion-safe:animate-picture-correct-glow motion-reduce:hidden"
        style={{ boxShadow: "0 0 22px var(--accent)" }}
      />

      <span
        aria-hidden
        className="absolute top-1/2 left-1/2 motion-reduce:hidden"
      >
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

      <span
        aria-hidden
        className="absolute top-1/2 left-1/2 motion-safe:animate-picture-correct-stamp motion-reduce:animate-picture-correct-stamp-soft"
      >
        <span className="flex items-center gap-2 rounded-[var(--radius)] border-2 border-[var(--accent)] bg-bg/85 px-4 py-2 font-pixel text-[13px] leading-none text-four shadow-[var(--shadow-cabinet-sm)]">
          <Check className="size-4 stroke-[3] text-[var(--accent)]" />
          {verdictLabel(token, streak)}
        </span>
      </span>
    </div>
  )
}

export type ScorePopProps = {
  scoreDelta: number
}

export function ScorePop({ scoreDelta }: ScorePopProps) {
  if (scoreDelta <= 0) return null
  return (
    <span
      aria-hidden
      className="pointer-events-none absolute -top-3 right-1 font-pixel text-[12px] text-four tabular-nums opacity-0 motion-safe:animate-picture-score-pop motion-reduce:animate-picture-score-pop-soft"
    >
      +{scoreDelta}
    </span>
  )
}
