/** Maps reducer state + timer tick to the 5-variant view model (ADR-0005 §4). */

import type { Question, Result } from "@/services/rapid_fire/schema";

import type { RapidFireState } from "../_hooks/useRapidFireReducer";

export type RapidFireViewState =
  | {
      status: "loading";
      currentScore: number;
      questionsAnswered: number;
      questionsTotal: number;
    }
  | {
      status: "question";
      question: Question;
      timerBarPct: number;
      currentScore: number;
      questionsAnswered: number;
      questionsTotal: number;
      locked: boolean;
      submittedOption: number | null;
      lastCorrect: boolean | null;
      lastCorrectOption: number | null;
    }
  | {
      status: "feedback";
      question: Question;
      lastCorrect: boolean;
      lastCorrectOption: number | null;
      submittedOption: number | null;
      currentScore: number;
      questionsAnswered: number;
      questionsTotal: number;
    }
  | { status: "result"; result: Result }
  | { status: "error"; message: string };

export function toRapidFireViewState(
  state: RapidFireState,
  timerBarPct: number | null,
): RapidFireViewState {
  switch (state.status) {
    case "idle":
      return {
        status: "loading",
        currentScore: state.currentScore,
        questionsAnswered: state.questionsAnswered,
        questionsTotal: state.questionsTotal,
      };
    case "loading":
      return {
        status: "loading",
        currentScore: state.currentScore,
        questionsAnswered: state.questionsAnswered,
        questionsTotal: state.questionsTotal,
      };
    case "question": {
      if (!state.currentQuestion) {
        return {
          status: "loading",
          currentScore: state.currentScore,
          questionsAnswered: state.questionsAnswered,
          questionsTotal: state.questionsTotal,
        };
      }
      return {
        status: "question",
        question: state.currentQuestion,
        timerBarPct: timerBarPct ?? 100,
        currentScore: state.currentScore,
        questionsAnswered: state.questionsAnswered,
        questionsTotal: state.questionsTotal,
        locked: false,
        submittedOption: state.submittedOption,
        lastCorrect: state.lastCorrect,
        lastCorrectOption: state.lastCorrectOption,
      };
    }
    case "submitting": {
      if (!state.currentQuestion) {
        return {
          status: "loading",
          currentScore: state.currentScore,
          questionsAnswered: state.questionsAnswered,
          questionsTotal: state.questionsTotal,
        };
      }
      return {
        status: "question",
        question: state.currentQuestion,
        timerBarPct: timerBarPct ?? 0,
        currentScore: state.currentScore,
        questionsAnswered: state.questionsAnswered,
        questionsTotal: state.questionsTotal,
        locked: true,
        submittedOption: state.submittedOption,
        lastCorrect: state.lastCorrect,
        lastCorrectOption: state.lastCorrectOption,
      };
    }
    case "feedback": {
      if (!state.currentQuestion) {
        return {
          status: "loading",
          currentScore: state.currentScore,
          questionsAnswered: state.questionsAnswered,
          questionsTotal: state.questionsTotal,
        };
      }
      return {
        status: "feedback",
        question: state.currentQuestion,
        lastCorrect: state.lastCorrect ?? false,
        lastCorrectOption: state.lastCorrectOption,
        submittedOption: state.submittedOption,
        currentScore: state.currentScore,
        questionsAnswered: state.questionsAnswered,
        questionsTotal: state.questionsTotal,
      };
    }
    case "result": {
      if (!state.result) {
        return {
          status: "loading",
          currentScore: state.currentScore,
          questionsAnswered: state.questionsAnswered,
          questionsTotal: state.questionsTotal,
        };
      }
      return {
        status: "result",
        result: state.result,
      };
    }
    case "error":
      return {
        status: "error",
        message: state.errorMessage ?? "Something went wrong.",
      };
  }
}
