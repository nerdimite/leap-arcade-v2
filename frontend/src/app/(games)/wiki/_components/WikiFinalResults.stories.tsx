import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import type { WikiPuzzleResult } from "@/services/wiki/schema";

import { WikiFinalResults } from "./WikiFinalResults";

const sampleResults: WikiPuzzleResult[] = [
  {
    round_id: "r1",
    puzzle_index: 1,
    clue: "Start at photosynthesis",
    target_title: "Chlorophyll",
    optimal_click_count: 3,
    steps_taken: 4,
    time_ms: 120_000,
    score: 180,
    status: "completed",
  },
  {
    round_id: "r2",
    puzzle_index: 2,
    clue: "Reach a programming language",
    target_title: "Python (programming language)",
    optimal_click_count: 5,
    steps_taken: 6,
    time_ms: 145_000,
    score: 150,
    status: "completed",
  },
];

const meta = {
  component: WikiFinalResults,
  args: {
    totalScore: 330,
    results: sampleResults,
  },
} satisfies Meta<typeof WikiFinalResults>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Completed: Story = {};

export const Abandoned: Story = {
  args: {
    title: "Wikipedia Speed Run",
    subtitle: "Session ended. Completed puzzles keep their scores; others count as zero.",
  },
};

export { Completed as Default };
