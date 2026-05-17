// @vitest-environment happy-dom

import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { WikiPlayResponse } from "@/services/wiki/schema";

import { WikiClient } from "./WikiClient";

const {
  postWikiAbandon,
  postWikiBack,
  postWikiNavigate,
  postWikiPlay,
  postWikiTimeout,
} = vi.hoisted(() => ({
  postWikiAbandon: vi.fn(),
  postWikiBack: vi.fn(),
  postWikiNavigate: vi.fn(),
  postWikiPlay: vi.fn(),
  postWikiTimeout: vi.fn(),
}));

vi.mock("@/hooks/use-navigation-guard", () => ({
  useNavigationGuard: () => ({
    setIsDirty: vi.fn(),
    registerBeforeNavigateConfirm: () => () => {},
  }),
}));

vi.mock("@/lib/api/wiki", () => ({
  postWikiAbandon,
  postWikiBack,
  postWikiNavigate,
  postWikiPlay,
  postWikiTimeout,
}));

function activePlay(articleHtml: string): WikiPlayResponse {
  return {
    state: "active",
    total_score: 0,
    completed_count: 0,
    completed_attempts: [],
    current: {
      game_session_id: "gs",
      attempt_id: "a1",
      round_id: "r1",
      puzzle_index: 1,
      puzzle_count: 5,
      clue: "Clue text",
      current_title: "Start",
      time_limit_ms: 180_000,
      time_remaining_ms: 180_000,
      steps_taken: 0,
      click_path: [],
      article_html: articleHtml,
      back_enabled: false,
    },
  };
}

describe("WikiClient", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  it("posts wiki navigation when a rewritten article link is clicked", async () => {
    postWikiNavigate.mockResolvedValue({
      state: "active",
      current: {
        game_session_id: "gs",
        attempt_id: "a1",
        round_id: "r1",
        puzzle_index: 1,
        puzzle_count: 5,
        clue: "Clue text",
        current_title: "Next Page",
        time_limit_ms: 180_000,
        time_remaining_ms: 175_000,
        steps_taken: 1,
        click_path: ["Next Page"],
        article_html: "<p>done</p>",
        back_enabled: true,
      },
    });

    const user = userEvent.setup();
    render(
      <WikiClient
        initialPlay={activePlay(
          '<p><a data-wiki-title="Next Page" href="#">Next</a></p>',
        )}
      />,
    );

    await user.click(screen.getByRole("link", { name: "Next" }));
    await waitFor(() => {
      expect(postWikiNavigate).toHaveBeenCalledWith("Next Page");
    });
  });

  it("shows a loading overlay during navigation while the article remains in the DOM", async () => {
    let resolveNav!: (v: unknown) => void;
    postWikiNavigate.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveNav = resolve;
        }),
    );

    const user = userEvent.setup();
    render(
      <WikiClient
        initialPlay={activePlay('<p><a data-wiki-title="Target" href="#">go</a></p>')}
      />,
    );

    expect(screen.getByText("go")).toBeInTheDocument();

    await user.click(screen.getByRole("link", { name: "go" }));

    expect(await screen.findByText("Loading article")).toBeInTheDocument();

    resolveNav({
      state: "active",
      current: {
        game_session_id: "gs",
        attempt_id: "a1",
        round_id: "r1",
        puzzle_index: 1,
        puzzle_count: 5,
        clue: "Clue text",
        current_title: "Target",
        time_limit_ms: 180_000,
        time_remaining_ms: 170_000,
        steps_taken: 1,
        click_path: ["Target"],
        article_html: "<p>arrived</p>",
        back_enabled: false,
      },
    });

    await waitFor(() => {
      expect(screen.queryByText("Loading article")).not.toBeInTheDocument();
    });
    expect(screen.getByText("arrived")).toBeInTheDocument();
  });

  it("blocks non-game anchors from escaping the wiki pane", () => {
    render(
      <WikiClient
        initialPlay={activePlay('<p><a href="https://en.wikipedia.org/wiki/Outside">Outside</a></p>')}
      />,
    );

    const link = screen.getByRole("link", { name: "Outside" });
    const evt = new MouseEvent("click", { bubbles: true, cancelable: true });
    link.dispatchEvent(evt);

    expect(evt.defaultPrevented).toBe(true);
    expect(postWikiNavigate).not.toHaveBeenCalled();
  });

  it("renders a scrollable path row for long breadcrumbs", () => {
    const long = "Antidisestablishmentarianism";
    const play: WikiPlayResponse = {
      state: "active",
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
        time_limit_ms: 180_000,
        time_remaining_ms: 180_000,
        steps_taken: 3,
        click_path: [long, long, long],
        article_html: "<p>x</p>",
        back_enabled: false,
      },
    };

    render(<WikiClient initialPlay={play} />);

    const root = screen.getByTestId("wiki-breadcrumb");
    expect(within(root).getByText("Path")).toBeInTheDocument();
    expect(root.querySelector(".overflow-x-auto")).toBeTruthy();
  });

  it("transitions to the puzzle result view when navigation completes the puzzle", async () => {
    postWikiNavigate.mockResolvedValue({
      state: "puzzle_completed",
      puzzle_result: {
        round_id: "r1",
        puzzle_index: 1,
        clue: "Clue text",
        target_title: "Target",
        optimal_click_count: 2,
        steps_taken: 2,
        time_ms: 1000,
        score: 180,
        status: "completed",
      },
      next_puzzle_available: true,
      total_score: 180,
    });

    const user = userEvent.setup();
    render(
      <WikiClient
        initialPlay={activePlay(
          '<p><a data-wiki-title="Target" href="#">finish</a></p>',
        )}
      />,
    );

    await user.click(screen.getByRole("link", { name: "finish" }));

    expect(await screen.findByRole("heading", { name: "Puzzle complete" })).toBeInTheDocument();
    expect(screen.getByText("Target revealed")).toBeInTheDocument();
    const btn = screen.getByRole("button", { name: /continue to next puzzle/i });
    expect(btn).toBeEnabled();
  });
});
