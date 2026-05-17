import { describe, expect, it } from "vitest";

import { formatMs } from "./utils";

describe("formatMs", () => {
  it("maps 0 to 0:00", () => {
    expect(formatMs(0)).toBe("0:00");
  });

  it("clamps negative input to 0:00", () => {
    expect(formatMs(-500)).toBe("0:00");
  });

  it("maps 1000 to 0:01", () => {
    expect(formatMs(1000)).toBe("0:01");
  });

  it("maps 59999 to 0:59", () => {
    expect(formatMs(59999)).toBe("0:59");
  });

  it("maps 60000 to 1:00", () => {
    expect(formatMs(60000)).toBe("1:00");
  });

  it("maps 61500 to 1:01", () => {
    expect(formatMs(61500)).toBe("1:01");
  });

  it("maps 3599000 to 59:59", () => {
    expect(formatMs(3599000)).toBe("59:59");
  });
});
