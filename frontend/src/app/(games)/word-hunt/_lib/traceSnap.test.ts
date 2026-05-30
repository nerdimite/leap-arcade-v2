import { describe, expect, it } from "vitest"

import { snapTraceFromPointer } from "./traceSnap"

describe("snapTraceFromPointer", () => {
  it("snaps a horizontal drag to a straight line", () => {
    expect(snapTraceFromPointer(0, 0, 0, 3, 10, 10)).toEqual({
      start_row: 0,
      start_col: 0,
      end_row: 0,
      end_col: 3,
    })
  })

  it("keeps a drifted path on horizontal when still closer to horizontal than diagonal", () => {
    expect(snapTraceFromPointer(0, 0, 1, 3, 10, 10)).toEqual({
      start_row: 0,
      start_col: 0,
      end_row: 0,
      end_col: 3,
    })
  })

  it("returns null for a single-cell pointer path", () => {
    expect(snapTraceFromPointer(2, 2, 2, 2, 10, 10)).toBeNull()
  })

  it("snaps a diagonal drag to the nearest diagonal line", () => {
    expect(snapTraceFromPointer(0, 0, 2, 3, 10, 10)).toEqual({
      start_row: 0,
      start_col: 0,
      end_row: 3,
      end_col: 3,
    })
  })

  it("clamps the snapped end to the grid edge", () => {
    expect(snapTraceFromPointer(0, 0, 0, 20, 10, 10)).toEqual({
      start_row: 0,
      start_col: 0,
      end_row: 0,
      end_col: 9,
    })
  })
})
