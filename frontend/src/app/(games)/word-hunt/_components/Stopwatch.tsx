"use client"

import { useEffect, useState } from "react"

import {
  elapsedMsFromStartedAt,
  formatMmSsFromElapsedMs,
  stopwatchToneClass,
} from "@/app/(games)/word-hunt/_lib/stopwatch"
import { WORD_HUNT_TIME_DECAY_MS } from "@/lib/constants"
import { cn } from "@/lib/utils"

export type StopwatchProps = {
  startedAt: string
}

export function Stopwatch({ startedAt }: StopwatchProps) {
  const [elapsedMs, setElapsedMs] = useState(() =>
    elapsedMsFromStartedAt(startedAt)
  )

  useEffect(() => {
    const tick = () => setElapsedMs(elapsedMsFromStartedAt(startedAt))
    tick()
    const id = window.setInterval(tick, 1000)
    return () => window.clearInterval(id)
  }, [startedAt])

  const pastDecay = elapsedMs >= WORD_HUNT_TIME_DECAY_MS

  return (
    <div className="flex flex-col items-end gap-0.5">
      <span
        className={cn(
          "font-mono text-lg tracking-tight tabular-nums",
          stopwatchToneClass(elapsedMs)
        )}
        role="timer"
        aria-live="polite"
        aria-label={`Elapsed time ${formatMmSsFromElapsedMs(elapsedMs)}`}
      >
        {formatMmSsFromElapsedMs(elapsedMs)}
      </span>
      {pastDecay ? (
        <span className="text-xs text-muted-foreground">No time bonus</span>
      ) : null}
    </div>
  )
}
