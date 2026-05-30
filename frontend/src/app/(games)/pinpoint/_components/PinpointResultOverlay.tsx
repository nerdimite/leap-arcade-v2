/** Terminal puzzle feedback overlay — celebrates a solve, never reveals the answer. */

import { Check, X } from "lucide-react"
import { useEffect, useState } from "react"

export type PinpointResultOverlayProps = {
  kind: "solved" | "failed"
  baseScore: number
  timeBonus?: number
  /** Clues the player burned before solving (1 = read it instantly). */
  cluesUsed?: number
}

/**
 * Fewer clues earns louder praise — the host gets more impressed the less you needed.
 * Game-show voice: short, punchy, never solemn.
 */
function solvedHeadline(cluesUsed: number): string {
  switch (cluesUsed) {
    case 1:
      return "PINPOINTED"
    case 2:
      return "SHARP READ"
    case 3:
      return "NAILED IT"
    case 4:
      return "GOT IT"
    default:
      return "JUST IN TIME"
  }
}

/** Deterministic confetti trajectories — stable across renders, win-only. */
const CONFETTI = [
  {
    dx: "-58px",
    dy: "-34px",
    rot: "-160deg",
    color: "var(--four)",
    delay: "0ms",
  },
  {
    dx: "-32px",
    dy: "-50px",
    rot: "120deg",
    color: "var(--pin)",
    delay: "20ms",
  },
  {
    dx: "-10px",
    dy: "-58px",
    rot: "-90deg",
    color: "var(--wiki)",
    delay: "0ms",
  },
  {
    dx: "14px",
    dy: "-56px",
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
  { dx: "58px", dy: "-30px", rot: "90deg", color: "var(--pin)", delay: "30ms" },
  {
    dx: "-46px",
    dy: "-14px",
    rot: "160deg",
    color: "var(--wiki)",
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

function prefersReducedMotion(): boolean {
  return (
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  )
}

const easeOutQuint = (t: number) => 1 - (1 - t) ** 5

/** Counts up to `target` on mount; jumps straight to it under reduced motion. */
function useCountUp(target: number, durationMs = 420): number {
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

function SolvedOverlay({
  baseScore,
  timeBonus,
  cluesUsed,
}: {
  baseScore: number
  timeBonus: number
  cluesUsed: number
}) {
  const total = baseScore + timeBonus
  const count = useCountUp(total)

  return (
    <div
      className="pointer-events-none absolute inset-0 z-20 flex items-center justify-center rounded-[var(--radius)] bg-four/15"
      aria-live="polite"
      role="status"
    >
      <div className="relative overflow-visible rounded-[var(--radius)] border-2 border-four bg-panel px-7 py-5 text-center shadow-[var(--shadow-cabinet)] motion-safe:animate-rf-verdict-in">
        <span className="pointer-events-none absolute top-3 left-1/2 motion-reduce:hidden">
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

        <p className="flex items-center justify-center gap-1.5 font-pixel text-[13px] leading-none text-four">
          <Check aria-hidden className="size-3.5 stroke-[3]" />
          {solvedHeadline(cluesUsed)}
        </p>

        <p className="mt-3 font-pixel text-[26px] leading-none text-four tabular-nums">
          +{count}
        </p>

        <p className="mt-2.5 text-[10px] font-bold tracking-[1px] text-ink-faint uppercase tabular-nums">
          {timeBonus > 0
            ? `${baseScore} base + ${timeBonus} time`
            : `${baseScore} base`}
        </p>
      </div>
    </div>
  )
}

function FailedOverlay() {
  return (
    <div
      className="pointer-events-none absolute inset-0 z-20 flex items-center justify-center rounded-[var(--radius)] bg-cross/15"
      aria-live="polite"
      role="status"
    >
      <div className="rounded-[var(--radius)] border-2 border-cross bg-panel px-7 py-5 text-center shadow-[var(--shadow-cabinet)]">
        <p className="flex items-center justify-center gap-1.5 font-pixel text-[13px] leading-none text-cross">
          <X aria-hidden className="size-3.5 stroke-[3]" />
          OUT OF CLUES
        </p>
        <p className="mt-3 text-[14px] text-ink-dim">No points this round.</p>
      </div>
    </div>
  )
}

export function PinpointResultOverlay(props: PinpointResultOverlayProps) {
  const { kind, baseScore, timeBonus = 0, cluesUsed = 5 } = props

  if (kind === "failed") {
    return <FailedOverlay />
  }

  return (
    <SolvedOverlay
      baseScore={baseScore}
      timeBonus={timeBonus}
      cluesUsed={cluesUsed}
    />
  )
}
