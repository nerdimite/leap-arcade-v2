import type { Meta, StoryObj } from "@storybook/nextjs-vite"
import { fn } from "storybook/test"

import {
  buildFeedbackState,
  buildQuestionState,
  buildResultState,
  RAPID_FIRE_TOTAL,
} from "../_lib/seedFixtures"
import { RapidFireView } from "./RapidFireView"
import type { RapidFireViewState } from "./rapid-fire-view-state"

const timingRef = { current: Date.now() }

const meta = {
  component: RapidFireView,
  parameters: { layout: "fullscreen" },
  args: {
    questionEnteredAtRef: timingRef,
    onSelectOption: fn(),
    onBackToLobby: fn(),
  },
} satisfies Meta<typeof RapidFireView>

export default meta

type Story = StoryObj<typeof meta>

export const Loading: Story = {
  args: {
    viewState: {
      status: "loading",
      currentScore: 0,
      questionsAnswered: 0,
      questionsTotal: RAPID_FIRE_TOTAL,
    } satisfies RapidFireViewState,
  },
}

export const Question: Story = {
  args: {
    viewState: buildQuestionState({ index: 0, timerBarPct: 70 }),
  },
}

export const QuestionLocked: Story = {
  args: {
    viewState: buildQuestionState({
      index: 0,
      timerBarPct: 0,
      locked: true,
      submittedOption: 2,
    }),
  },
}

export const FeedbackCorrect: Story = {
  name: "Feedback (correct)",
  args: {
    viewState: buildFeedbackState({ index: 0, correct: true }),
  },
}

export const FeedbackWrong: Story = {
  name: "Feedback (wrong)",
  args: {
    viewState: buildFeedbackState({ index: 0, correct: false }),
  },
}

export const Result: Story = {
  args: {
    viewState: buildResultState(),
  },
}

export const ErrorStory: Story = {
  name: "Error",
  args: {
    viewState: {
      status: "error",
      message: "Something went wrong.",
    } satisfies RapidFireViewState,
  },
}
