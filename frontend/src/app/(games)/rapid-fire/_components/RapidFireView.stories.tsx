import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { fn } from "storybook/test";

import type { Question as RapidFireQuestion, Result as RapidFireResult } from "@/services/rapid_fire/schema";

import { RapidFireView } from "./RapidFireView";
import type { RapidFireViewState } from "./rapid-fire-view-state";

const sampleQuestion: RapidFireQuestion = {
  id: "story-q1",
  question: "Pick the best answer.",
  options: ["Alpha", "Bravo", "Charlie", "Delta"],
  time_limit_ms: 20_000,
};

const sampleResult: RapidFireResult = {
  score: 55,
  correct_count: 8,
  wrong_count: 5,
  skipped_count: 2,
  time_taken_seconds: 120.4,
};

const timingRef = { current: Date.now() };

const meta = {
  component: RapidFireView,
  args: {
    questionEnteredAtRef: timingRef,
    onSelectOption: fn(),
    onBackToLobby: fn(),
  },
} satisfies Meta<typeof RapidFireView>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Loading: Story = {
  args: {
    viewState: {
      status: "loading",
      currentScore: 0,
      questionsAnswered: 0,
      questionsTotal: 0,
    } satisfies RapidFireViewState,
  },
};

export const Question: Story = {
  args: {
    viewState: {
      status: "question",
      question: sampleQuestion,
      timerBarPct: 70,
      currentScore: 3,
      questionsAnswered: 2,
      questionsTotal: 15,
      locked: false,
      submittedOption: null,
      lastCorrect: null,
      lastCorrectOption: null,
    } satisfies RapidFireViewState,
  },
};

export const QuestionLocked: Story = {
  args: {
    viewState: {
      status: "question",
      question: sampleQuestion,
      timerBarPct: 0,
      currentScore: 3,
      questionsAnswered: 2,
      questionsTotal: 15,
      locked: true,
      submittedOption: 2,
      lastCorrect: null,
      lastCorrectOption: null,
    } satisfies RapidFireViewState,
  },
};

export const Feedback: Story = {
  args: {
    viewState: {
      status: "feedback",
      question: sampleQuestion,
      lastCorrect: true,
      lastCorrectOption: 1,
      submittedOption: 1,
      currentScore: 7,
      questionsAnswered: 3,
      questionsTotal: 15,
    } satisfies RapidFireViewState,
  },
};

export const Result: Story = {
  args: {
    viewState: {
      status: "result",
      result: sampleResult,
    } satisfies RapidFireViewState,
  },
};

export const ErrorStory: Story = {
  name: "Error",
  args: {
    viewState: {
      status: "error",
      message: "Something went wrong.",
    } satisfies RapidFireViewState,
  },
};
