/** Human-readable line for time remaining + time bonus on the Picture result screen. */

export function formatPictureResultClockLine(
  timeRemainingSeconds: number,
  timeBonusPoints: number
): string {
  const clamped = Math.max(0, Math.floor(timeRemainingSeconds))
  const m = Math.floor(clamped / 60)
  const s = clamped % 60
  const durationLabel = m > 0 ? `${m}m ${s}s` : `${s}s`
  return `${durationLabel} left on the clock — +${timeBonusPoints} pts`
}
