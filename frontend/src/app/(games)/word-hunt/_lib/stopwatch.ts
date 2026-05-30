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
