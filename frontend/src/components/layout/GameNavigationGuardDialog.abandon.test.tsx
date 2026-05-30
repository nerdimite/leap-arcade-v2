// @vitest-environment happy-dom

import { cleanup, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { HttpResponse, http } from "msw"
import { useEffect } from "react"
import { flushSync } from "react-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import {
  NavigationGuardProvider,
  useNavigationGuard,
} from "@/hooks/use-navigation-guard"
import { postAbandon } from "@/lib/api/rapid_fire"
import { server } from "@/test/msw-server"

import { GameNavigationGuardDialog } from "./GameNavigationGuardDialog"

const push = vi.fn()

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    replace: vi.fn(),
    push,
    prefetch: vi.fn(),
  }),
}))

function TripHarness() {
  const { navigateSafe, registerBeforeNavigateConfirm, setIsDirty } =
    useNavigationGuard()

  useEffect(() => {
    return registerBeforeNavigateConfirm(async () => {
      await postAbandon({
        baseUrl: "http://localhost:3000",
        cookieHeader: "token=abc",
      })
    })
  }, [registerBeforeNavigateConfirm])

  return (
    <button
      type="button"
      onClick={() => {
        flushSync(() => setIsDirty(true))
        navigateSafe("/lobby")
      }}
    >
      Trip guard
    </button>
  )
}

function App() {
  return (
    <NavigationGuardProvider>
      <TripHarness />
      <GameNavigationGuardDialog />
    </NavigationGuardProvider>
  )
}

describe("GameNavigationGuardDialog abandon", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    window.history.replaceState(
      {},
      "",
      "http://localhost:3000/games/rapid-fire"
    )
  })

  afterEach(() => {
    cleanup()
  })

  it("confirming leave calls POST /abandon once then navigates", async () => {
    let abandonCalls = 0
    server.use(
      http.post(
        ({ request }) =>
          new URL(request.url).pathname.endsWith(
            "/api/games/rapid-fire/abandon"
          ),
        () => {
          abandonCalls += 1
          return HttpResponse.json({
            result: {
              score: 10,
              correct_count: 1,
              wrong_count: 0,
              skipped_count: 0,
              time_taken_seconds: 5,
            },
          })
        }
      )
    )

    const user = userEvent.setup()
    render(<App />)

    await user.click(screen.getByRole("button", { name: /trip guard/i }))
    expect(await screen.findByRole("alertdialog")).toBeInTheDocument()

    await user.click(screen.getByRole("button", { name: /leave anyway/i }))

    await waitFor(() => {
      expect(abandonCalls).toBe(1)
    })
    await waitFor(() => {
      expect(push).toHaveBeenCalledWith("/lobby")
    })
  })
})
