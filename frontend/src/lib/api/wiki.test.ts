import { HttpResponse, http } from "msw";
import { describe, expect, it } from "vitest";

import { server } from "@/test/msw-server";

import { postWikiNavigate, postWikiPlay, postWikiTimeout } from "./wiki";

const sampleActive = {
  state: "active" as const,
  total_score: 0,
  completed_count: 0,
  completed_attempts: [],
  current: {
    game_session_id: "gs",
    attempt_id: "a1",
    round_id: "r1",
    puzzle_index: 1,
    puzzle_count: 5,
    clue: "Clue",
    current_title: "Start",
    time_limit_ms: 120_000,
    time_remaining_ms: 120_000,
    steps_taken: 0,
    click_path: [] as string[],
    article_html: "<p>x</p>",
    back_enabled: false,
  },
};

describe("postWikiPlay", () => {
  it("POST /api/games/wiki/play returns parsed WikiPlayResponse", async () => {
    server.use(
      http.post(
        ({ request }) => new URL(request.url).pathname.endsWith("/api/games/wiki/play"),
        async ({ request }) => {
          expect(request.headers.get("cookie")).toBe("token=abc");
          expect(request.headers.get("accept")).toBe("application/json");
          return HttpResponse.json(sampleActive);
        },
      ),
    );

    const res = await postWikiPlay({
      baseUrl: "http://localhost:3000",
      cookieHeader: "token=abc",
    });
    expect(res.state).toBe("active");
    if (res.state === "active") {
      expect(res.current.puzzle_index).toBe(1);
      expect(res.current.puzzle_count).toBe(5);
    }
  });

  it("parses terminal completed payload with results", async () => {
    const terminal = {
      state: "completed" as const,
      total_score: 1000,
      results: [
        {
          round_id: "r1",
          puzzle_index: 1,
          clue: "c1",
          target_title: "T1",
          optimal_click_count: 1,
          steps_taken: 1,
          time_ms: 10,
          score: 200,
          status: "completed",
        },
      ],
    };
    server.use(
      http.post(
        ({ request }) => new URL(request.url).pathname.endsWith("/api/games/wiki/play"),
        () => HttpResponse.json(terminal),
      ),
    );

    const res = await postWikiPlay({ baseUrl: "http://localhost:3000", cookieHeader: "x=1" });
    expect(res.state).toBe("completed");
    if (res.state === "completed") {
      expect(res.results).toHaveLength(1);
      expect(res.results[0]?.target_title).toBe("T1");
    }
  });
});

describe("postWikiNavigate", () => {
  it("POST navigate with title JSON body", async () => {
    server.use(
      http.post(
        ({ request }) => new URL(request.url).pathname.endsWith("/api/games/wiki/navigate"),
        async ({ request }) => {
          expect(request.headers.get("content-type")).toContain("application/json");
          const body = (await request.json()) as { title: string };
          expect(body.title).toBe("Next");
          return HttpResponse.json({
            state: "puzzle_completed",
            puzzle_result: {
              round_id: "r1",
              puzzle_index: 1,
              clue: "c",
              target_title: "Next",
              optimal_click_count: 1,
              steps_taken: 1,
              time_ms: 5,
              score: 200,
              status: "completed",
            },
            next_puzzle_available: true,
            total_score: 200,
          });
        },
      ),
    );

    const res = await postWikiNavigate("Next", { baseUrl: "http://localhost:3000", cookieHeader: "y=1" });
    expect(res.state).toBe("puzzle_completed");
    if (res.state === "puzzle_completed") {
      expect(res.next_puzzle_available).toBe(true);
    }
  });
});

describe("postWikiTimeout", () => {
  it("POST /api/games/wiki/timeout returns WikiPlayResponse", async () => {
    server.use(
      http.post(
        ({ request }) => new URL(request.url).pathname.endsWith("/api/games/wiki/timeout"),
        () => HttpResponse.json(sampleActive),
      ),
    );

    const res = await postWikiTimeout({
      baseUrl: "http://localhost:3000",
      cookieHeader: "token=abc",
    });
    expect(res.state).toBe("active");
    if (res.state === "active") {
      expect(res.current.time_remaining_ms).toBe(120_000);
    }
  });
});
