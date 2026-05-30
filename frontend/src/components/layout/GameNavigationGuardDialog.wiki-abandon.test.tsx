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
import { postWikiAbandon } from "@/lib/api/wiki"
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

function WikiTripHarness() {
  const { navigateSafe, registerBeforeNavigateConfirm, setIsDirty } =
    useNavigationGuard()

  useEffect(() => {
    return registerBeforeNavigateConfirm(async () => {
      await postWikiAbandon({
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
      Trip wiki guard
    </button>
  )
}

function WikiApp() {
  return (
    <NavigationGuardProvider>
      <WikiTripHarness />
      <GameNavigationGuardDialog />
    </NavigationGuardProvider>
  )
}

describe("GameNavigationGuardDialog wiki abandon", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    window.history.replaceState({}, "", "http://localhost:3000/games/wiki")
  })

  afterEach(() => {
    cleanup()
  })

  it("confirming leave calls POST wiki abandon once then navigates", async () => {
    let abandonCalls = 0
    server.use(
      http.post(
        ({ request }) =>
          new URL(request.url).pathname.endsWith("/api/games/wiki/abandon"),
        () => {
          abandonCalls += 1
          return HttpResponse.json({
            state: "abandoned",
            total_score: 0,
            results: [],
          })
        }
      )
    )

    const user = userEvent.setup()
    render(<WikiApp />)

    await user.click(screen.getByRole("button", { name: /trip wiki guard/i }))
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
