"use client"

import { useEffect, useState } from "react"

/** True when the OS asks for calmer motion — count-ups land on the target immediately. */
export function prefersReducedMotion(): boolean {
  return (
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  )
}

const easeOutQuint = (t: number) => 1 - (1 - t) ** 5

/**
 * Counts up to `target` on mount. Under reduced motion it starts at the target and
 * never animates. `target` is expected to be stable for the component's lifetime.
 */
export function useCountUp(target: number, durationMs = 480): number {
  const reduce = prefersReducedMotion()
  const [value, setValue] = useState(reduce ? target : 0)

  useEffect(() => {
    if (reduce) return
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
  }, [target, durationMs, reduce])

  return value
}
