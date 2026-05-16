// @vitest-environment happy-dom

import { renderHook, waitFor } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { describe, expect, it } from "vitest";

import { QueryClientProviderWrapper } from "@/components/query-client-provider";
import { server } from "@/test/msw-server";

import { usePlayerSessions } from "./hooks";

describe("usePlayerSessions", () => {
  it("returns session data from the API", async () => {
    server.use(
      http.get(
        ({ request }) =>
          new URL(request.url).pathname.endsWith("/api/players/me/sessions"),
        () =>
          HttpResponse.json([
            { game_id: "rapid_fire", status: "active", score: null },
          ]),
      ),
    );

    const { result } = renderHook(() => usePlayerSessions(), {
      wrapper: QueryClientProviderWrapper,
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual([
      { game_id: "rapid_fire", status: "active", score: null },
    ]);
  });
});
