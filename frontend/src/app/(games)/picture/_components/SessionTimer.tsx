"use client"

import { useEffect, useRef, useState } from "react"

type Props = {
  sessionStartedAt: string
  timeLimitMs: number
  onExpired: () => void | Promise<void>
}

function remainingMs(sessionStartedAt: string, timeLimitMs: number): number {
  const started = new Date(sessionStartedAt).getTime()
  return timeLimitMs - (Date.now() - started)
}

function formatCountdown(totalSeconds: number): string {
  const m = Math.floor(totalSeconds / 60)
  const s = totalSeconds % 60
  return `${m}:${s.toString().padStart(2, "0")}`
}

export function SessionTimer({
  sessionStartedAt,
  timeLimitMs,
  onExpired,
}: Props) {
  const [displaySeconds, setDisplaySeconds] = useState(() =>
    Math.max(0, Math.ceil(remainingMs(sessionStartedAt, timeLimitMs) / 1000))
  )
  const expiredRef = useRef(false)
  const onExpiredRef = useRef(onExpired)

  onExpiredRef.current = onExpired

  useEffect(() => {
    expiredRef.current = false

    const tick = () => {
      const msLeft = remainingMs(sessionStartedAt, timeLimitMs)
      const sec = Math.max(0, Math.ceil(msLeft / 1000))
      setDisplaySeconds(sec)

      if (msLeft <= 0 && !expiredRef.current) {
        expiredRef.current = true
        void onExpiredRef.current()
      }
    }

    tick()
    const id = window.setInterval(tick, 250)
    return () => window.clearInterval(id)
  }, [sessionStartedAt, timeLimitMs])

  const urgent = displaySeconds > 0 && displaySeconds < 60

  return (
    <div
      className={
        urgent
          ? "animate-arcade-blink rounded-[var(--radius)] border-2 border-cross bg-panel px-3 py-1.5 font-pixel text-[13px] text-cross tabular-nums shadow-[var(--shadow-cabinet-sm)] motion-reduce:animate-none"
          : "rounded-[var(--radius)] border-2 border-line bg-panel px-3 py-1.5 font-pixel text-[13px] text-ink-dim tabular-nums shadow-[var(--shadow-cabinet-sm)]"
      }
      aria-live="polite"
    >
      {formatCountdown(displaySeconds)}
    </div>
  )
}
