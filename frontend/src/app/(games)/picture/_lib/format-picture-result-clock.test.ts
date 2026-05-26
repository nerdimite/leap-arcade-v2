import { describe, expect, it } from "vitest";

import { formatPictureResultClockLine } from "./format-picture-result-clock";

describe("formatPictureResultClockLine", () => {
  it("formats seconds only when under one minute", () => {
    expect(formatPictureResultClockLine(45, 120)).toBe("45s left on the clock — +120 pts");
  });

  it("formats minutes and seconds", () => {
    expect(formatPictureResultClockLine(134, 134)).toBe("2m 14s left on the clock — +134 pts");
  });

  it("clamps negatives to zero for display", () => {
    expect(formatPictureResultClockLine(-5, 0)).toBe("0s left on the clock — +0 pts");
  });
});
