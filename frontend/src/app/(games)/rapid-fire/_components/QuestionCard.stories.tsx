import type { Meta, StoryObj } from "@storybook/nextjs-vite"
import { fn } from "storybook/test"

import type { Question as RapidFireQuestion } from "@/services/rapid_fire/schema"

import { QuestionCard } from "./QuestionCard"

const sampleQuestion: RapidFireQuestion = {
  id: "story-q1",
  question: "Which port does HTTP typically use?",
  options: ["20", "80", "443", "8080"],
  time_limit_ms: 15_000,
}

const timingRef = { current: Date.now() }

const meta = {
  component: QuestionCard,
  args: {
    question: sampleQuestion,
    options: sampleQuestion.options,
    questionEnteredAtRef: timingRef,
    onSelectOption: fn(),
  },
} satisfies Meta<typeof QuestionCard>

export default meta

type Story = StoryObj<typeof meta>

export const Question: Story = {
  args: {
    phase: "question",
    selected: null,
    correctOption: null,
    lastCorrect: null,
    locked: false,
  },
}

export const FeedbackCorrect: Story = {
  args: {
    phase: "feedback",
    selected: 2,
    correctOption: 2,
    lastCorrect: true,
    locked: false,
  },
}

export const FeedbackWrong: Story = {
  args: {
    phase: "feedback",
    selected: 1,
    correctOption: 3,
    lastCorrect: false,
    locked: false,
  },
}

export { Question as Default }
