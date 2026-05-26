import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { fn } from "storybook/test";

import type { Result } from "@/services/four_pics/schema";

import { ResultView } from "./ResultView";

const mixedResult: Result = {
  score: 275,
  questions_correct: 2,
  questions_wrong: 1,
  questions_not_reached: 0,
  questions: [
    { question_id: "q1", status: "correct", score: 142, time_bonus: 42 },
    { question_id: "q2", status: "wrong", score: 0, time_bonus: 0 },
    { question_id: "q3", status: "correct", score: 133, time_bonus: 33 },
  ],
};

const meta = {
  component: ResultView,
  args: {
    onBackToLobby: fn(),
  },
} satisfies Meta<typeof ResultView>;

export default meta;

type Story = StoryObj<typeof meta>;

export const MixedStatuses: Story = {
  args: {
    result: mixedResult,
  },
};

export const WithNotReached: Story = {
  args: {
    result: {
      ...mixedResult,
      score: 142,
      questions_correct: 1,
      questions_wrong: 1,
      questions_not_reached: 1,
      questions: [
        ...mixedResult.questions,
        { question_id: "q4", status: "not_reached", score: 0, time_bonus: 0 },
      ],
    },
  },
};

export { MixedStatuses as Default };
