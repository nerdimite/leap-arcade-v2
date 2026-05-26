import { describe, expect, it } from "vitest";

import {
  elapsedMsFromStartedAt,
  formatMmSsFromElapsedMs,
  stopwatchToneClass,
} from "./stopwatch";

describe("pinpoint stopwatch helpers", () => {
  it("formats elapsed time as mm:ss", () => {
    expect(formatMmSsFromElapsedMs(0)).toBe("00:00");
    expect(formatMmSsFromElapsedMs(65_000)).toBe("01:05");
  });

  it("computes elapsed ms from started_at", () => {
    const startedAt = "2026-05-26T12:00:00.000Z";
    expect(elapsedMsFromStartedAt(startedAt, Date.parse(startedAt) + 30_000)).toBe(30_000);
  });

  it("uses muted tone after decay window", () => {
    expect(stopwatchToneClass(90_000)).toContain("no-bonus");
  });
});
