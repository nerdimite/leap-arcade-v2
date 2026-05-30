import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { fn } from "storybook/test";

import type { PuzzleState, Result } from "@/services/word_hunt/schema";

import {
  allUnfoundClues,
  devopsTrace,
  midDragPreview,
  partialFoundClues,
  sampleGrid,
} from "../_lib/storyFixtures";
import { WordHuntView } from "./WordHuntView";

const basePuzzle: PuzzleState = {
  puzzle_id: "wh-1",
  rows: 6,
  cols: 6,
  grid: sampleGrid,
  clues: allUnfoundClues,
  found_count: 0,
  total_words: 3,
  started_at: new Date(Date.now() - 45_000).toISOString(),
};

const sampleResult: Result = {
  score: 350,
  base_score: 200,
  time_bonus: 150,
  time_elapsed_ms: 125_000,
  found_count: 2,
  total_words: 3,
  found_words: [
    {
      word_id: "w1",
      word: "DEVOPS",
      clue: "Culture where dev and ops stop pointing fingers.",
      coordinates: devopsTrace,
    },
    {
      word_id: "w3",
      word: "ANGULAR",
      clue: "Google's framework for building SPAs with TypeScript.",
      coordinates: { start_row: 4, start_col: 0, end_row: 4, end_col: 5 },
    },
  ],
};

const meta = {
  component: WordHuntView,
  parameters: { layout: "fullscreen" },
  args: {
    onDragStart: fn(),
    onDragMove: fn(),
    onDragEnd: fn(),
    onSubmit: fn(),
    onBackToLobby: fn(),
  },
} satisfies Meta<typeof WordHuntView>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Playing: Story = {
  args: {
    viewState: {
      status: "playing",
      puzzle: basePuzzle,
      sessionScore: 0,
      highlights: [],
      dragPreview: null,
      missFlash: null,
      landAnimation: null,
      showScoreIncrement: false,
      disabled: false,
    },
  },
};

export const Dragging: Story = {
  args: {
    viewState: {
      status: "playing",
      puzzle: basePuzzle,
      sessionScore: 0,
      highlights: [],
      dragPreview: midDragPreview,
      missFlash: null,
      landAnimation: null,
      showScoreIncrement: false,
      disabled: false,
    },
  },
};

export const PartiallyFound: Story = {
  args: {
    viewState: {
      status: "playing",
      puzzle: {
        ...basePuzzle,
        clues: partialFoundClues,
        found_count: 2,
      },
      sessionScore: 200,
      highlights: [
        devopsTrace,
        { start_row: 4, start_col: 0, end_row: 4, end_col: 5 },
      ],
      dragPreview: null,
      missFlash: null,
      landAnimation: null,
      showScoreIncrement: true,
      disabled: false,
    },
  },
};

export const ResultStory: Story = {
  name: "Result",
  args: {
    viewState: { status: "result", result: sampleResult },
  },
};
