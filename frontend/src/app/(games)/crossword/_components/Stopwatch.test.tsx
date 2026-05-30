// @vitest-environment happy-dom

import { cleanup, render, screen } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { Stopwatch } from "./Stopwatch"

describe("Stopwatch", () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date("2026-05-26T12:01:30.000Z"))
  })

  afterEach(() => {
    cleanup()
    vi.useRealTimers()
  })

  it("renders elapsed mm:ss from server started_at", () => {
    render(<Stopwatch startedAt="2026-05-26T12:00:00.000Z" />)
    expect(screen.getByText("01:30")).toBeInTheDocument()
  })

  it("resumes elapsed time from started_at after remount", () => {
    const { unmount } = render(
      <Stopwatch startedAt="2026-05-26T12:00:00.000Z" />
    )
    expect(screen.getByText("01:30")).toBeInTheDocument()
    unmount()

    vi.setSystemTime(new Date("2026-05-26T12:02:00.000Z"))
    render(<Stopwatch startedAt="2026-05-26T12:00:00.000Z" />)
    expect(screen.getByText("02:00")).toBeInTheDocument()
  })
})
