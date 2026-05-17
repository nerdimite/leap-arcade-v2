// @vitest-environment happy-dom

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";

import { QueryClientProviderWrapper } from "@/components/query-client-provider";
import { server } from "@/test/msw-server";

import { usePlayerSessions } from "./hooks";
import type { PlayerSessionsResponse } from "./schema";

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

  it("refetches on remount even while cached data is fresh", async () => {
    let responseBody: PlayerSessionsResponse = [
      { game_id: "rapid_fire", status: "active", score: null },
    ];

    server.use(
      http.get(
        ({ request }) =>
          new URL(request.url).pathname.endsWith("/api/players/me/sessions"),
        () => HttpResponse.json(responseBody),
      ),
    );

    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });

    function Wrapper({ children }: { children: ReactNode }) {
      return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
    }

    const firstRender = renderHook(() => usePlayerSessions(), {
      wrapper: Wrapper,
    });

    await waitFor(() => {
      expect(firstRender.result.current.isSuccess).toBe(true);
    });

    expect(firstRender.result.current.data).toEqual([
      { game_id: "rapid_fire", status: "active", score: null },
    ]);

    firstRender.unmount();

    responseBody = [{ game_id: "rapid_fire", status: "completed", score: 800 }];

    const secondRender = renderHook(() => usePlayerSessions(), {
      wrapper: Wrapper,
    });

    await waitFor(() => {
      expect(secondRender.result.current.data).toEqual([
        { game_id: "rapid_fire", status: "completed", score: 800 },
      ]);
    });
  });
});
