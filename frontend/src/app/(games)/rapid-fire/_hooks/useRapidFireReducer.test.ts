import { describe, expect, it } from "vitest";

import type { AnswerResponse } from "@/services/rapid_fire/schema";

import {
  initRapidFireFromPlayResponse,
  rapidFireInitialState,
  rapidFireReducer,
} from "./useRapidFireReducer";

const sampleQuestion = {
  id: "q1",
  question: "Sample?",
  options: ["A", "B", "C", "D"],
  time_limit_ms: 10_000,
};

const sampleQuestion2 = {
  id: "q2",
  question: "Next?",
  options: ["E", "F", "G", "H"],
  time_limit_ms: 10_000,
};

function answerPayload(partial: Partial<AnswerResponse> & Pick<AnswerResponse, "next_question">): AnswerResponse {
  return {
    correct: true,
    correct_option: 1,
    correct_answer_text: "A",
    current_score: 10,
    questions_answered: 1,
    questions_remaining: 14,
    result: null,
    ...partial,
  };
}

describe("rapidFireReducer", () => {
  it("idle → loading → question on START + PLAY_SUCCESS", () => {
    let s = rapidFireReducer(rapidFireInitialState, { type: "START" });
    expect(s.status).toBe("loading");
    s = rapidFireReducer(s, {
      type: "PLAY_SUCCESS",
      payload: {
        game_session_id: "gs",
        questions_answered: 0,
        questions_total: 15,
        question: sampleQuestion,
      },
    });
    expect(s.status).toBe("question");
    expect(s.currentQuestion?.id).toBe("q1");
    expect(s.sessionId).toBe("gs");
  });

  it("question → submitting → feedback → question on happy-path answer cycle", () => {
    let s = initRapidFireFromPlayResponse({
      status: "active",
      game_session_id: "gs",
      questions_answered: 0,
      questions_total: 15,
      question: sampleQuestion,
    });
    expect(s.status).toBe("question");

    s = rapidFireReducer(s, {
      type: "SELECT_OPTION",
      payload: { selected_option: 1, time_ms: 100 },
    });
    expect(s.status).toBe("submitting");

    s = rapidFireReducer(
      s,
      {
        type: "ANSWER_SUCCESS",
        payload: answerPayload({
          correct: true,
          current_score: 5,
          questions_answered: 1,
          questions_remaining: 14,
          next_question: sampleQuestion2,
        }),
      },
    );
    expect(s.status).toBe("feedback");

    s = rapidFireReducer(s, { type: "FEEDBACK_COMPLETE" });
    expect(s.status).toBe("question");
    expect(s.currentQuestion?.id).toBe("q2");
    expect(s.currentScore).toBe(5);
  });

  it("feedback → result when next_question is null after FEEDBACK_COMPLETE", () => {
    let s = initRapidFireFromPlayResponse({
      status: "active",
      game_session_id: "gs",
      questions_answered: 14,
      questions_total: 15,
      question: sampleQuestion,
    });
    s = rapidFireReducer(s, {
      type: "SELECT_OPTION",
      payload: { selected_option: 2, time_ms: 200 },
    });
    s = rapidFireReducer(
      s,
      {
        type: "ANSWER_SUCCESS",
        payload: answerPayload({
          correct: true,
          current_score: 999,
          questions_answered: 15,
          questions_remaining: 0,
          next_question: null,
          result: {
            score: 999,
            correct_count: 12,
            wrong_count: 2,
            skipped_count: 1,
            time_taken_seconds: 88,
          },
        }),
      },
    );
    expect(s.status).toBe("feedback");
    s = rapidFireReducer(s, { type: "FEEDBACK_COMPLETE" });
    expect(s.status).toBe("result");
    expect(s.result?.score).toBe(999);
  });

  it("ignores SELECT_OPTION while submitting", () => {
    let s = initRapidFireFromPlayResponse({
      status: "active",
      game_session_id: "gs",
      questions_answered: 0,
      questions_total: 15,
      question: sampleQuestion,
    });
    s = rapidFireReducer(s, {
      type: "SELECT_OPTION",
      payload: { selected_option: 1, time_ms: 50 },
    });
    expect(s.status).toBe("submitting");
    const before = s;
    s = rapidFireReducer(s, {
      type: "SELECT_OPTION",
      payload: { selected_option: 4, time_ms: 50 },
    });
    expect(s).toEqual(before);
  });

  it("TIMER_EXPIRE in question transitions like SELECT_OPTION with null", () => {
    const s = initRapidFireFromPlayResponse({
      status: "active",
      game_session_id: "gs",
      questions_answered: 0,
      questions_total: 15,
      question: sampleQuestion,
    });
    const viaTimer = rapidFireReducer(s, {
      type: "TIMER_EXPIRE",
      payload: { time_ms: sampleQuestion.time_limit_ms },
    });
    const viaSelect = rapidFireReducer(s, {
      type: "SELECT_OPTION",
      payload: { selected_option: null, time_ms: sampleQuestion.time_limit_ms },
    });
    expect(viaTimer).toEqual(viaSelect);
    expect(viaTimer.status).toBe("submitting");
    expect(viaTimer.submittedOption).toBeNull();
    expect(viaTimer.pendingTimeMs).toBe(sampleQuestion.time_limit_ms);
  });

  it("TIMER_EXPIRE in submitting is a no-op", () => {
    let s = initRapidFireFromPlayResponse({
      status: "active",
      game_session_id: "gs",
      questions_answered: 0,
      questions_total: 15,
      question: sampleQuestion,
    });
    s = rapidFireReducer(s, {
      type: "SELECT_OPTION",
      payload: { selected_option: 1, time_ms: 50 },
    });
    const before = s;
    s = rapidFireReducer(s, {
      type: "TIMER_EXPIRE",
      payload: { time_ms: sampleQuestion.time_limit_ms },
    });
    expect(s).toEqual(before);
  });

  it("TIMER_EXPIRE in feedback is a no-op", () => {
    let s = initRapidFireFromPlayResponse({
      status: "active",
      game_session_id: "gs",
      questions_answered: 0,
      questions_total: 15,
      question: sampleQuestion,
    });
    s = rapidFireReducer(s, {
      type: "SELECT_OPTION",
      payload: { selected_option: 1, time_ms: 50 },
    });
    s = rapidFireReducer(
      s,
      {
        type: "ANSWER_SUCCESS",
        payload: answerPayload({
          correct: false,
          current_score: 0,
          questions_answered: 1,
          questions_remaining: 14,
          next_question: sampleQuestion2,
        }),
      },
    );
    expect(s.status).toBe("feedback");
    const before = s;
    s = rapidFireReducer(s, {
      type: "TIMER_EXPIRE",
      payload: { time_ms: sampleQuestion.time_limit_ms },
    });
    expect(s).toEqual(before);
  });
});
