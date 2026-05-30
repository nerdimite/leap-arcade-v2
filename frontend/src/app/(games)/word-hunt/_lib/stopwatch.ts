import { WORD_HUNT_TIME_DECAY_MS } from "@/lib/constants"

export function elapsedMsFromStartedAt(
  startedAt: string,
  nowMs: number = Date.now()
): number {
  const startedMs = new Date(startedAt).getTime()
  return Math.max(0, nowMs - startedMs)
}

export function formatMmSsFromElapsedMs(elapsedMs: number): string {
  const totalSeconds = Math.floor(elapsedMs / 1000)
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`
}

/** Visual decay cue: neutral → warm → urgent → stable no-bonus once the bonus floors out. */
export function stopwatchToneClass(elapsedMs: number): string {
  if (elapsedMs >= WORD_HUNT_TIME_DECAY_MS) {
    return "text-muted-foreground no-bonus"
  }
  if (elapsedMs >= 480_000) {
    return "font-semibold text-destructive"
  }
  if (elapsedMs >= 300_000) {
    return "font-medium text-amber-600 dark:text-amber-400"
  }
  return "text-muted-foreground"
}
