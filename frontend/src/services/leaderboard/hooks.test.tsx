// @vitest-environment happy-dom

import { renderHook, waitFor } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { describe, expect, it } from "vitest";

import { QueryClientProviderWrapper } from "@/components/query-client-provider";
import { server } from "@/test/msw-server";

import { useLeaderboard } from "./hooks";

describe("useLeaderboard", () => {
  it("returns ranked entries from the API", async () => {
    server.use(
      http.get(
        ({ request }) => new URL(request.url).pathname.endsWith("/api/leaderboard"),
        () =>
          HttpResponse.json({
            entries: [
              {
                rank: 1,
                player_id: "bob",
                display_name: "Bob",
                total_score: 50,
                games_completed: 1,
              },
              {
                rank: 2,
                player_id: "alice",
                display_name: "Alice",
                total_score: 40,
                games_completed: 1,
              },
            ],
            total_players: 2,
          }),
      ),
    );

    const { result } = renderHook(() => useLeaderboard(), {
      wrapper: QueryClientProviderWrapper,
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.entries).toEqual([
      {
        rank: 1,
        corp_id: "bob",
        display_name: "Bob",
        total_score: 50,
        games_completed: 1,
      },
      {
        rank: 2,
        corp_id: "alice",
        display_name: "Alice",
        total_score: 40,
        games_completed: 1,
      },
    ]);
  });
});
