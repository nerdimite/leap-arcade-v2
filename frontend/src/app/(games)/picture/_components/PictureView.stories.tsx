import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { fn } from "storybook/test";

import type { Puzzle, Result } from "@/services/picture/schema";

import { PictureView } from "./PictureView";

const samplePuzzle: Puzzle = {
  id: "p-1",
  image_filename: "neural_network.png",
  puzzles_answered: 2,
  puzzles_total: 5,
};

const sampleResult: Result = {
  score: 640,
  accuracy_score: 520,
  time_bonus: 120,
  time_remaining_seconds: 84,
  puzzles: [
    { puzzle_id: "p-1", image_filename: "neural_network.png", status: "correct", score_earned: 180 },
    { puzzle_id: "p-2", image_filename: "nlp.png", status: "correct", score_earned: 160 },
    {
      puzzle_id: "p-3",
      image_filename: "large_language_model.png",
      status: "skipped",
      score_earned: 0,
    },
    { puzzle_id: "p-4", image_filename: "gradient_descent.png", status: "wrong", score_earned: 0 },
    {
      puzzle_id: "p-5",
      image_filename: "huggingface.png",
      status: "not_reached",
      score_earned: 0,
    },
  ],
};

const meta = {
  component: PictureView,
  parameters: { layout: "fullscreen" },
  args: {
    onAnswerChange: fn(),
    onSubmit: fn((e) => e.preventDefault()),
    onSkip: fn(),
    onInputAnimationEnd: fn(),
    onSessionExpired: fn(),
    onBackToLobby: fn(),
  },
} satisfies Meta<typeof PictureView>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Playing: Story = {
  args: {
    viewState: {
      status: "playing",
      puzzle: samplePuzzle,
      currentScore: 340,
      answer: "",
      wrongMessage: null,
      inputShakeActive: false,
      isPending: false,
      timer: { startedAt: new Date().toISOString(), limitMs: 300_000 },
    },
  },
};

export const WrongAnswer: Story = {
  args: {
    viewState: {
      status: "playing",
      puzzle: samplePuzzle,
      currentScore: 340,
      answer: "perceptron",
      wrongMessage: "Incorrect, try again.",
      inputShakeActive: true,
      isPending: false,
      timer: { startedAt: new Date().toISOString(), limitMs: 300_000 },
    },
  },
};

export const UrgentTimer: Story = {
  args: {
    viewState: {
      status: "playing",
      puzzle: samplePuzzle,
      currentScore: 480,
      answer: "",
      wrongMessage: null,
      inputShakeActive: false,
      isPending: false,
      timer: { startedAt: new Date().toISOString(), limitMs: 25_000 },
    },
  },
};

export const ResultStory: Story = {
  name: "Result",
  args: {
    viewState: { status: "result", result: sampleResult },
  },
};
