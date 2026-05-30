import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { fn } from "storybook/test";

import { PinpointView } from "./PinpointView";
import type { PinpointViewState } from "./pinpoint-view-state";

const basePuzzle = {
  puzzle_id: "pz-1",
  puzzle_number: 2,
  total_puzzles: 5,
  clues_revealed: 3,
  clues: ["Has a tail", "Barks", "Loyal", "Fetches", "Best friend"],
  status: "active" as const,
  score: null,
  time_bonus: null,
  // ~12s ago, so the stopwatch shows a live, sensible value in the story.
  started_at: new Date(Date.now() - 12_000).toISOString(),
};

const meta = {
  component: PinpointView,
  parameters: { layout: "fullscreen" },
  args: {
    onGuessChange: fn(),
    onSubmitGuess: fn(),
  },
} satisfies Meta<typeof PinpointView>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Playing: Story = {
  args: {
    viewState: {
      status: "playing",
      sessionScore: 820,
      puzzle: basePuzzle,
      guess: "",
      inputDisabled: false,
      overlay: null,
      shakeBadgeIndex: null,
      errorMessage: null,
    } satisfies PinpointViewState,
  },
};

export const WrongGuessShake: Story = {
  args: {
    viewState: {
      status: "playing",
      sessionScore: 820,
      puzzle: { ...basePuzzle, clues_revealed: 4 },
      guess: "cat",
      inputDisabled: false,
      overlay: null,
      shakeBadgeIndex: 3,
      errorMessage: null,
    } satisfies PinpointViewState,
  },
};

export const SolvedOverlay: Story = {
  args: {
    viewState: {
      status: "playing",
      sessionScore: 1286,
      puzzle: basePuzzle,
      guess: "dog",
      inputDisabled: true,
      overlay: { kind: "solved", baseScore: 400, timeBonus: 66, cluesUsed: 2 },
      shakeBadgeIndex: null,
      errorMessage: null,
    } satisfies PinpointViewState,
  },
};

export const Loading: Story = {
  args: {
    viewState: { status: "loading" } satisfies PinpointViewState,
  },
};

export const Result: Story = {
  args: {
    viewState: {
      status: "result",
      result: {
        score: 1286,
        puzzles_solved: 3,
        puzzles_failed: 1,
        puzzles_not_reached: 1,
        puzzles: [
          { puzzle_id: "pz-1", status: "solved", clues_used: 2, score: 466, time_bonus: 66 },
          { puzzle_id: "pz-2", status: "solved", clues_used: 3, score: 420, time_bonus: 20 },
          { puzzle_id: "pz-3", status: "solved", clues_used: 4, score: 400, time_bonus: 0 },
          { puzzle_id: "pz-4", status: "failed", clues_used: 5, score: 0, time_bonus: 0 },
          { puzzle_id: "pz-5", status: "not_reached", clues_used: null, score: 0, time_bonus: 0 },
        ],
      },
    } satisfies PinpointViewState,
  },
};
