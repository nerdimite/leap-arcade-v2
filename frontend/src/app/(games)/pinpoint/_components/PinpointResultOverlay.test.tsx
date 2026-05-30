// @vitest-environment happy-dom

import { cleanup, render, screen } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { PinpointResultOverlay } from "./PinpointResultOverlay"

/** Pin reduced-motion so the score count-up jumps to its final value synchronously. */
function mockReducedMotion() {
  vi.stubGlobal("matchMedia", (query: string) => ({
    matches: true,
    media: query,
    onchange: null,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    addListener: vi.fn(),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }))
}

describe("PinpointResultOverlay", () => {
  beforeEach(() => {
    mockReducedMotion()
  })

  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  it("reveals the total score with the base and time bonus breakdown", () => {
    render(
      <PinpointResultOverlay
        kind="solved"
        baseScore={400}
        timeBonus={66}
        cluesUsed={3}
      />
    )
    const status = screen.getByRole("status")
    expect(status).toHaveTextContent("+466")
    expect(status).toHaveTextContent("400 base + 66 time")
  })

  it("omits the time line when there is no bonus", () => {
    render(
      <PinpointResultOverlay
        kind="solved"
        baseScore={400}
        timeBonus={0}
        cluesUsed={4}
      />
    )
    const status = screen.getByRole("status")
    expect(status).toHaveTextContent("+400")
    expect(status).toHaveTextContent("400 base")
    expect(status).not.toHaveTextContent("time")
  })

  it("praises a one-clue solve louder than a last-ditch one", () => {
    render(
      <PinpointResultOverlay
        kind="solved"
        baseScore={500}
        timeBonus={0}
        cluesUsed={1}
      />
    )
    expect(screen.getByRole("status")).toHaveTextContent("PINPOINTED")
    cleanup()
    render(
      <PinpointResultOverlay
        kind="solved"
        baseScore={100}
        timeBonus={0}
        cluesUsed={5}
      />
    )
    expect(screen.getByRole("status")).toHaveTextContent("JUST IN TIME")
  })

  it("shows calm failed copy with no points", () => {
    render(<PinpointResultOverlay kind="failed" baseScore={0} />)
    const status = screen.getByRole("status")
    expect(status).toHaveTextContent("OUT OF CLUES")
    expect(status).toHaveTextContent("No points this round.")
  })

  it("never renders answer or alias text from leaked props", () => {
    render(
      <PinpointResultOverlay
        kind="failed"
        baseScore={0}
        // @ts-expect-error — simulate a future API leak in tests
        answer="cloud computing"
        answer_aliases={["cloud", "computing"]}
      />
    )

    expect(screen.queryByText("cloud computing")).toBeNull()
    expect(screen.queryByText("cloud")).toBeNull()
    expect(screen.queryByText("computing")).toBeNull()
  })
})
