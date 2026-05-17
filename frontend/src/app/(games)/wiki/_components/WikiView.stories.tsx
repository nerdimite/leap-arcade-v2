import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { fn } from "storybook/test";

import type { WikiActivePuzzle, WikiPuzzleResult } from "@/services/wiki/schema";

import { WikiView } from "./WikiView";
import type { WikiViewState } from "./wiki-view-state";

const sampleActive: WikiActivePuzzle = {
  game_session_id: "gs-story",
  attempt_id: "attempt-1",
  round_id: "round-1",
  puzzle_index: 3,
  puzzle_count: 5,
  clue: "Find the Nobel Prize physicist.",
  current_title: "Copenhagen",
  time_limit_ms: 180_000,
  time_remaining_ms: 52_250,
  steps_taken: 3,
  click_path: ["Denmark"],
  article_html: '<p><a data-wiki-title="Niels Bohr" href="#">Bohr</a></p>',
  back_enabled: true,
};

const samplePuzzleResult: WikiPuzzleResult = {
  round_id: "round-3",
  puzzle_index: 3,
  clue: "Reach the inventor of the transistor",
  target_title: "John Bardeen",
  optimal_click_count: 6,
  steps_taken: 7,
  time_ms: 96_000,
  score: 140,
  status: "completed",
};

const finalResults: WikiPuzzleResult[] = [
  samplePuzzleResult,
  {
    round_id: "round-4",
    puzzle_index: 4,
    clue: "Another clue",
    target_title: "Target",
    optimal_click_count: 2,
    steps_taken: 2,
    time_ms: 40_000,
    score: 200,
    status: "completed",
  },
];

const timingRefFns = () => ({
  onNavigate: fn(async () => Promise.resolve()),
  onBack: fn(async () => Promise.resolve()),
  onContinue: fn(async () => Promise.resolve()),
});

const meta = {
  component: WikiView,
  args: timingRefFns(),
} satisfies Meta<typeof WikiView>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Active: Story = {
  args: {
    ...timingRefFns(),
    viewState: {
      status: "active",
      current: sampleActive,
      pathRoot: "Atlantic Ocean",
      timerRemainingMs: 52_250,
      completedCount: 2,
      totalScore: 580,
      navPending: false,
    } satisfies WikiViewState,
  },
};

export const PuzzleResult: Story = {
  args: {
    ...timingRefFns(),
    viewState: {
      status: "puzzleResult",
      result: samplePuzzleResult,
      totalScore: 720,
      hasNext: true,
      continuePending: false,
    } satisfies WikiViewState,
  },
};

export const FinalCompleted: Story = {
  args: {
    ...timingRefFns(),
    viewState: {
      status: "finalCompleted",
      totalScore: 990,
      results: finalResults,
    } satisfies WikiViewState,
  },
};

export const FinalAbandoned: Story = {
  args: {
    ...timingRefFns(),
    viewState: {
      status: "finalAbandoned",
      totalScore: 620,
      results: finalResults,
    } satisfies WikiViewState,
  },
};

export const ErrorStory: Story = {
  name: "Error",
  args: {
    ...timingRefFns(),
    viewState: {
      status: "error",
      message: "Could not load the wiki session.",
    } satisfies WikiViewState,
  },
};
