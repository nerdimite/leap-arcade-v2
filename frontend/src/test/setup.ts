import "@testing-library/jest-dom/vitest"
import { afterAll, afterEach, beforeAll } from "vitest"

import { server } from "./msw-server"

beforeAll(() => {
  // Intercept fetches in tests until handlers are registered per test case.
  server.listen({ onUnhandledRequest: "error" })
})

afterEach(() => {
  server.resetHandlers()
})

afterAll(() => {
  server.close()
})
