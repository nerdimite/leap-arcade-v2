// @vitest-environment happy-dom

import { cleanup, render, screen } from "@testing-library/react"
import { afterEach, describe, expect, it } from "vitest"

import { ClueBadgeRow } from "./ClueBadgeRow"

describe("ClueBadgeRow", () => {
  afterEach(() => {
    cleanup()
  })

  it("renders five slots with revealed clue text and locked placeholders", () => {
    render(<ClueBadgeRow cluesRevealed={2} clues={["cloud", "server"]} />)

    const slots = screen.getAllByTestId("clue-badge-slot")
    expect(slots).toHaveLength(5)

    expect(screen.getByText("cloud")).toBeTruthy()
    expect(screen.getByText("server")).toBeTruthy()
    expect(screen.getAllByText("Locked")).toHaveLength(3)
  })

  it("marks the shake badge slot for wrong-guess feedback", () => {
    render(
      <ClueBadgeRow
        cluesRevealed={2}
        clues={["cloud", "server"]}
        shakeBadgeIndex={1}
      />
    )

    const slots = screen.getAllByTestId("clue-badge-slot")
    expect(slots[1]?.dataset.shake).toBe("true")
    expect(slots[0]?.dataset.shake).toBeUndefined()
  })
})
