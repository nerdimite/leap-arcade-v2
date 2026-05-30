"use client";

import { useReducer } from "react";

import type {
  AnswerResponse,
  PlayResponse,
  Question,
  Result,
} from "@/services/rapid_fire/schema";

export type RapidFirePhase =
  | "idle"
  | "loading"
  | "question"
  | "submitting"
  | "feedback"
  | "result"
  | "error";

export type RapidFireState = {
  status: RapidFirePhase;
  sessionId: string | null;
  questionsAnswered: number;
  questionsTotal: number;
  currentQuestion: Question | null;
  currentScore: number;
  submittedOption: number | null;
  pendingTimeMs: number | null;
  lastCorrect: boolean | null;
  lastCorrectOption: number | null;
  /** Points earned on the most recent answer (current_score delta); drives the +N feedback. */
  lastScoreDelta: number;
  pendingNextQuestion: Question | null;
  pendingResult: Result | null;
  result: Result | null;
  errorMessage: string | null;
};

export type RapidFireAction =
  | { type: "START" }
  | {
      type: "PLAY_SUCCESS";
      payload: {
        game_session_id: string;
        questions_answered: number;
        questions_total: number;
        question: Question;
      };
    }
  | { type: "PLAY_ERROR"; payload: { message: string } }
  | { type: "SELECT_OPTION"; payload: { selected_option: number | null; time_ms: number } }
  | {
      type: "TIMER_EXPIRE";
      payload: { time_ms: number };
    }
  | { type: "ANSWER_SUCCESS"; payload: AnswerResponse }
  | { type: "ANSWER_ERROR" }
  | { type: "FEEDBACK_COMPLETE" }
  | { type: "RESULT_SHOWN" };

export const rapidFireInitialState: RapidFireState = {
  status: "idle",
  sessionId: null,
  questionsAnswered: 0,
  questionsTotal: 0,
  currentQuestion: null,
  currentScore: 0,
  submittedOption: null,
  pendingTimeMs: null,
  lastCorrect: null,
  lastCorrectOption: null,
  lastScoreDelta: 0,
  pendingNextQuestion: null,
  pendingResult: null,
  result: null,
  errorMessage: null,
};

export function initRapidFireFromPlayResponse(play: PlayResponse): RapidFireState {
  if (play.status === "active") {
    return {
      ...rapidFireInitialState,
      status: "question",
      sessionId: play.game_session_id,
      questionsAnswered: play.questions_answered,
      questionsTotal: play.questions_total,
      currentQuestion: play.question,
      currentScore: 0,
    };
  }
  return {
    ...rapidFireInitialState,
    status: "result",
    result: play.result,
  };
}

export function rapidFireReducer(state: RapidFireState, action: RapidFireAction): RapidFireState {
  switch (action.type) {
    case "START":
      if (state.status !== "idle") {
        return state;
      }
      return {
        ...state,
        status: "loading",
        errorMessage: null,
      };
    case "PLAY_SUCCESS": {
      if (state.status !== "loading") {
        return state;
      }
      return {
        ...state,
        status: "question",
        sessionId: action.payload.game_session_id,
        questionsAnswered: action.payload.questions_answered,
        questionsTotal: action.payload.questions_total,
        currentQuestion: action.payload.question,
        currentScore: 0,
        errorMessage: null,
      };
    }
    case "PLAY_ERROR":
      if (state.status !== "loading") {
        return state;
      }
      return {
        ...rapidFireInitialState,
        status: "error",
        errorMessage: action.payload.message,
      };
    case "SELECT_OPTION": {
      if (state.status !== "question") {
        return state;
      }
      return {
        ...state,
        status: "submitting",
        submittedOption: action.payload.selected_option,
        pendingTimeMs: action.payload.time_ms,
      };
    }
    case "TIMER_EXPIRE": {
      if (state.status !== "question") {
        return state;
      }
      return rapidFireReducer(state, {
        type: "SELECT_OPTION",
        payload: { selected_option: null, time_ms: action.payload.time_ms },
      });
    }
    case "ANSWER_SUCCESS": {
      if (state.status !== "submitting") {
        return state;
      }
      return {
        ...state,
        status: "feedback",
        lastCorrect: action.payload.correct,
        lastCorrectOption: action.payload.correct_option,
        currentScore: action.payload.current_score,
        lastScoreDelta: action.payload.current_score - state.currentScore,
        questionsAnswered: action.payload.questions_answered,
        pendingNextQuestion: action.payload.next_question,
        pendingResult: action.payload.result,
      };
    }
    case "ANSWER_ERROR": {
      if (state.status !== "submitting") {
        return state;
      }
      return {
        ...rapidFireInitialState,
        status: "error",
        errorMessage: "Could not submit your answer. Please refresh the page.",
        sessionId: state.sessionId,
      };
    }
    case "FEEDBACK_COMPLETE": {
      if (state.status !== "feedback") {
        return state;
      }
      if (state.pendingNextQuestion) {
        const next = state.pendingNextQuestion;
        return {
          ...state,
          status: "question",
          currentQuestion: next,
          pendingNextQuestion: null,
          pendingResult: null,
          submittedOption: null,
          pendingTimeMs: null,
          lastCorrect: null,
          lastCorrectOption: null,
          lastScoreDelta: 0,
        };
      }
      if (state.pendingResult) {
        return {
          ...state,
          status: "result",
          result: state.pendingResult,
          currentQuestion: null,
          pendingNextQuestion: null,
          pendingResult: null,
          submittedOption: null,
          pendingTimeMs: null,
          lastCorrect: null,
          lastCorrectOption: null,
        };
      }
      return {
        ...state,
        status: "error",
        errorMessage: "Unexpected end of game.",
      };
    }
    case "RESULT_SHOWN":
      return state;
    default:
      return state;
  }
}

export function useRapidFireReducer(initialPlay: PlayResponse) {
  return useReducer(rapidFireReducer, initialPlay, initRapidFireFromPlayResponse);
}
