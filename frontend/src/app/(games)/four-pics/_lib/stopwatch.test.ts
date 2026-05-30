import { describe, expect, it } from "vitest"

import { FOUR_PICS_TIME_DECAY_MS } from "@/lib/constants"

import {
  elapsedMsFromStartedAt,
  formatMmSsFromElapsedMs,
  stopwatchToneClass,
} from "./stopwatch"

describe("elapsedMsFromStartedAt", () => {
  it("computes elapsed from ISO started_at and a reference now", () => {
    const started = "2026-05-26T12:00:00.000Z"
    const now = new Date("2026-05-26T12:00:15.500Z").getTime()
    expect(elapsedMsFromStartedAt(started, now)).toBe(15_500)
  })

  it("never returns negative elapsed", () => {
    const started = "2026-05-26T12:01:00.000Z"
    const now = new Date("2026-05-26T12:00:00.000Z").getTime()
    expect(elapsedMsFromStartedAt(started, now)).toBe(0)
  })
})

describe("formatMmSsFromElapsedMs", () => {
  it("formats minutes and zero-padded seconds", () => {
    expect(formatMmSsFromElapsedMs(0)).toBe("00:00")
    expect(formatMmSsFromElapsedMs(65_000)).toBe("01:05")
    expect(formatMmSsFromElapsedMs(125_000)).toBe("02:05")
  })
})

describe("stopwatchToneClass", () => {
  it("stays neutral early in the question", () => {
    expect(stopwatchToneClass(5_000)).toContain("muted")
  })

  it("warms as elapsed approaches the decay floor", () => {
    expect(stopwatchToneClass(20_000)).toContain("amber")
  })

  it("intensifies near the bonus floor", () => {
    expect(stopwatchToneClass(28_000)).toContain("destructive")
  })

  it("settles into no-bonus state past decay", () => {
    expect(stopwatchToneClass(FOUR_PICS_TIME_DECAY_MS)).toContain("no-bonus")
    expect(stopwatchToneClass(60_000)).toContain("no-bonus")
  })
})
