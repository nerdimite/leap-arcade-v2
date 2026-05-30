// @vitest-environment happy-dom

import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { QueryClientProviderWrapper } from "@/components/query-client-provider";
import type { PlayResponse, Result } from "@/services/crossword/schema";

import { CrosswordClient } from "./CrosswordClient";

const { setIsDirty, navigateSafe, postSubmit, postCheck, postPlay } = vi.hoisted(() => ({
  setIsDirty: vi.fn(),
  navigateSafe: vi.fn(),
  postSubmit: vi.fn(),
  postCheck: vi.fn(),
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

vi.mock("@/lib/api/crossword", () => ({
  postSubmit,
  postCheck,
  postPlay,
}));

function renderCrossword(initialPlay: PlayResponse) {
  return render(
    <QueryClientProviderWrapper>
      <CrosswordClient initialPlay={initialPlay} />
    </QueryClientProviderWrapper>,
  );
}

const completedResult: Result = {
  score: 350,
  solved_count: 2,
  total_entries: 5,
  base_score: 200,
  time_bonus: 150,
  time_elapsed_ms: 90_000,
  solved_entries: [
    {
      entry_id: "e1",
      number: 7,
      direction: "across",
      clue: "Database property ensuring all-or-nothing commits",
      answer: "ATOMICITY",
      cells: [{ row: 0, col: 0 }],
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
      cells: [
        [
          { row: 0, col: 0, number: 1, letter: null },
          { row: 0, col: 1, number: null, letter: null },
          { row: 0, col: 2, number: null, letter: null },
        ],
        [
          { row: 1, col: 0, number: null, letter: null },
          { row: 1, col: 1, number: null, letter: null },
          { row: 1, col: 2, number: null, letter: null },
        ],
        [
          { row: 2, col: 0, number: null, letter: null },
          { row: 2, col: 1, number: null, letter: null },
          { row: 2, col: 2, number: null, letter: null },
        ],
      ],
      clues: [
        {
          entry_id: "e1",
          number: 1,
          direction: "across",
          clue: "First clue",
          length: 3,
          start_row: 0,
          start_col: 0,
          solved: true,
          answer: "ABC",
          cells: [
            { row: 0, col: 0 },
            { row: 0, col: 1 },
            { row: 0, col: 2 },
          ],
        },
        {
          entry_id: "e2",
          number: 2,
          direction: "down",
          clue: "Second clue",
          length: 3,
          start_row: 0,
          start_col: 0,
          solved: false,
        },
      ],
      solved_count: 1,
      total_entries: 2,
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

describe("CrosswordClient", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    capturedConfirmHandler = null;
  });

  afterEach(() => {
    cleanup();
  });

  it("arms the navigation guard for an active session", () => {
    renderCrossword(activePlay());
    expect(setIsDirty).toHaveBeenCalledWith(true);
  });

  it("does not arm the navigation guard for a completed session", () => {
    renderCrossword(completedPlay());
    expect(setIsDirty).not.toHaveBeenCalledWith(true);
  });

  it("registers submit as the navigation guard confirm handler while active", async () => {
    postSubmit.mockResolvedValue({ result: completedResult });

    renderCrossword(activePlay());

    expect(capturedConfirmHandler).not.toBeNull();
    await capturedConfirmHandler?.();

    expect(postSubmit).toHaveBeenCalledOnce();
  });

  it("shows ResultView directly when re-entering a completed session", () => {
    renderCrossword(completedPlay());

    expect(screen.getByText("350")).toBeInTheDocument();
    expect(screen.queryByTestId("crossword-grid")).toBeNull();
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
    renderCrossword(activePlay());

    await user.click(screen.getByRole("button", { name: /^submit$/i }));
    expect(postSubmit).toHaveBeenCalledOnce();

    await user.click(screen.getByRole("button", { name: /^submit$/i }));
    expect(postSubmit).toHaveBeenCalledOnce();

    resolveSubmit({ result: completedResult });

    expect(await screen.findByText("350")).toBeInTheDocument();
    expect(screen.queryByTestId("crossword-grid")).toBeNull();
  });

  it("disarms the guard after submit completes", async () => {
    postSubmit.mockResolvedValue({ result: completedResult });

    const user = userEvent.setup();
    renderCrossword(activePlay());

    await user.click(screen.getByRole("button", { name: /^submit$/i }));

    await waitFor(() => {
      expect(setIsDirty).toHaveBeenCalledWith(false);
    });
  });

  it("routes back to lobby via navigateSafe", async () => {
    const user = userEvent.setup();
    renderCrossword(completedPlay());

    await user.click(screen.getByRole("button", { name: /back to lobby/i }));
    expect(navigateSafe).toHaveBeenCalledWith("/lobby");
  });
});
