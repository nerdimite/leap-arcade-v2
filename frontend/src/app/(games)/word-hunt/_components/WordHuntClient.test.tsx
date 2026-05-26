// @vitest-environment happy-dom

import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { QueryClientProviderWrapper } from "@/components/query-client-provider";
import type { PlayResponse, Result } from "@/services/word_hunt/schema";

import { WordHuntClient } from "./WordHuntClient";

const { setIsDirty, navigateSafe, postSubmit, postFind, postPlay } = vi.hoisted(() => ({
  setIsDirty: vi.fn(),
  navigateSafe: vi.fn(),
  postSubmit: vi.fn(),
  postFind: vi.fn(),
  postPlay: vi.fn(),
}));

let capturedConfirmHandler: (() => Promise<void>) | null = null;

vi.mock("@/hooks/use-navigation-guard", () => ({
  useNavigationGuard: () => ({
    setIsDirty,
    registerBeforeNavigateConfirm: (fn: () => Promise<void>) => {
      capturedConfirmHandler = fn;
      return () => {
        capturedConfirmHandler = null;
      };
    },
    navigateSafe,
  }),
}));

vi.mock("@/lib/api/word-hunt", () => ({
  postSubmit,
  postFind,
  postPlay,
}));

vi.mock("./LetterGrid", () => ({
  LetterGrid: () => <div data-testid="letter-grid">grid</div>,
}));

function renderWordHunt(initialPlay: PlayResponse) {
  return render(
    <QueryClientProviderWrapper>
      <WordHuntClient initialPlay={initialPlay} />
    </QueryClientProviderWrapper>,
  );
}

const completedResult: Result = {
  score: 350,
  found_count: 2,
  total_words: 5,
  base_score: 200,
  time_bonus: 150,
  time_elapsed_ms: 90_000,
  found_words: [
    {
      word_id: "w1",
      word: "CLOUD",
      clue: "Fluffy data center metaphor",
      coordinates: { start_row: 0, start_col: 0, end_row: 0, end_col: 4 },
    },
  ],
};

function activePlay(): PlayResponse {
  return {
    session_status: "active",
    session_score: 100,
    puzzle: {
      puzzle_id: "p1",
      rows: 3,
      cols: 3,
      grid: [
        ["A", "B", "C"],
        ["D", "E", "F"],
        ["G", "H", "I"],
      ],
      clues: [
        { word_id: "w1", clue: "First clue", found: true, word: "ABC" },
        { word_id: "w2", clue: "Second clue", found: false },
      ],
      found_count: 1,
      total_words: 2,
      started_at: "2026-05-26T12:00:00.000Z",
    },
    result: null,
  };
}

function completedPlay(): PlayResponse {
  return {
    session_status: "completed",
    session_score: completedResult.score,
    puzzle: null,
    result: completedResult,
  };
}

describe("WordHuntClient", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    capturedConfirmHandler = null;
  });

  afterEach(() => {
    cleanup();
  });

  it("arms the navigation guard for an active session", () => {
    renderWordHunt(activePlay());
    expect(setIsDirty).toHaveBeenCalledWith(true);
  });

  it("does not arm the navigation guard for a completed session", () => {
    renderWordHunt(completedPlay());
    expect(setIsDirty).not.toHaveBeenCalledWith(true);
  });

  it("registers submit as the navigation guard confirm handler while active", async () => {
    postSubmit.mockResolvedValue({ result: completedResult });

    renderWordHunt(activePlay());

    expect(capturedConfirmHandler).not.toBeNull();
    await capturedConfirmHandler?.();

    expect(postSubmit).toHaveBeenCalledOnce();
  });

  it("shows ResultView directly when re-entering a completed session", () => {
    renderWordHunt(completedPlay());

    expect(screen.getByText("350")).toBeInTheDocument();
    expect(screen.queryByTestId("letter-grid")).toBeNull();
    expect(screen.getByRole("button", { name: /back to lobby/i })).toBeInTheDocument();
  });

  it("transitions to ResultView after submit without reloading", async () => {
    let resolveSubmit!: (value: { result: Result }) => void;
    postSubmit.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveSubmit = resolve;
        }),
    );

    const user = userEvent.setup();
    renderWordHunt(activePlay());

    await user.click(screen.getByRole("button", { name: /^submit$/i }));
    expect(postSubmit).toHaveBeenCalledOnce();

    await user.click(screen.getByRole("button", { name: /^submit$/i }));
    expect(postSubmit).toHaveBeenCalledOnce();

    resolveSubmit({ result: completedResult });

    expect(await screen.findByText("350")).toBeInTheDocument();
    expect(screen.queryByTestId("letter-grid")).toBeNull();
  });

  it("disarms the guard after submit completes", async () => {
    postSubmit.mockResolvedValue({ result: completedResult });

    const user = userEvent.setup();
    renderWordHunt(activePlay());

    await user.click(screen.getByRole("button", { name: /^submit$/i }));

    await waitFor(() => {
      expect(setIsDirty).toHaveBeenCalledWith(false);
    });
  });

  it("routes back to lobby via navigateSafe", async () => {
    const user = userEvent.setup();
    renderWordHunt(completedPlay());

    await user.click(screen.getByRole("button", { name: /back to lobby/i }));
    expect(navigateSafe).toHaveBeenCalledWith("/lobby");
  });
});
