import type { Meta, StoryObj } from "@storybook/nextjs-vite"
import { fn } from "storybook/test"

import type { QuestionState, Result } from "@/services/four_pics/schema"

import { FourPicsView } from "./FourPicsView"

const sampleQuestion: QuestionState = {
  question_id: "q-1",
  question_number: 2,
  total_questions: 6,
  image_paths: [
    "/images/four-pics/animals/1.png",
    "/images/four-pics/animals/2.png",
    "/images/four-pics/animals/3.png",
    "/images/four-pics/animals/4.png",
  ],
  status: "active",
  started_at: new Date(Date.now() - 8_000).toISOString(),
}

const sampleResult: Result = {
  score: 1840,
  questions_correct: 4,
  questions_wrong: 1,
  questions_not_reached: 1,
  questions: [
    { question_id: "q-1", status: "correct", score: 380, time_bonus: 80 },
    { question_id: "q-2", status: "correct", score: 360, time_bonus: 60 },
    { question_id: "q-3", status: "wrong", score: 0, time_bonus: 0 },
    { question_id: "q-4", status: "correct", score: 340, time_bonus: 40 },
    { question_id: "q-5", status: "correct", score: 360, time_bonus: 60 },
    { question_id: "q-6", status: "not_reached", score: 0, time_bonus: 0 },
  ],
}

const meta = {
  component: FourPicsView,
  parameters: { layout: "fullscreen" },
  args: {
    onSelect: fn(),
    onBackToLobby: fn(),
  },
} satisfies Meta<typeof FourPicsView>

export default meta

type Story = StoryObj<typeof meta>

export const Playing: Story = {
  args: {
    viewState: {
      status: "playing",
      question: sampleQuestion,
      sessionScore: 760,
      overlay: null,
      submitError: null,
      inputDisabled: false,
    },
  },
}

export const CorrectOverlay: Story = {
  args: {
    viewState: {
      status: "playing",
      question: sampleQuestion,
      sessionScore: 1140,
      overlay: { correct: true, score: 380, timeBonus: 80, selectedIndex: 2 },
      submitError: null,
      inputDisabled: true,
    },
  },
}

export const WrongOverlay: Story = {
  args: {
    viewState: {
      status: "playing",
      question: sampleQuestion,
      sessionScore: 760,
      overlay: { correct: false, score: 0, timeBonus: 0, selectedIndex: 1 },
      submitError: null,
      inputDisabled: true,
    },
  },
}

export const SubmitError: Story = {
  args: {
    viewState: {
      status: "playing",
      question: sampleQuestion,
      sessionScore: 760,
      overlay: null,
      submitError: "Could not submit answer. Try again.",
      inputDisabled: false,
    },
  },
}

export const ResultStory: Story = {
  name: "Result",
  args: {
    viewState: { status: "result", result: sampleResult },
  },
}
