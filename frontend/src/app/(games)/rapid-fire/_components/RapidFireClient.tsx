"use client";

import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { useNavigationGuard } from "@/hooks/use-navigation-guard";
import { FEEDBACK_DURATION_MS, QUESTION_START_DELAY_MS } from "@/lib/constants";
import { useAbandon, useSubmitAnswer } from "@/services/rapid_fire/hooks";
import type { PlayResponse } from "@/services/rapid_fire/schema";

import { useRapidFireReducer } from "../_hooks/useRapidFireReducer";

function optionButtonClass(
  optionIndex1: number,
  ctx: {
    phase: "question" | "feedback";
    selected: number | null;
    correctOption: number | null;
    lastCorrect: boolean | null;
  },
): string {
  const base =
    "h-auto min-h-10 w-full justify-start whitespace-normal py-2 text-left";

  if (ctx.phase === "question") {
    return base;
  }

  const isCorrect = optionIndex1 === ctx.correctOption;
  const isWrongPick =
    ctx.selected != null && !ctx.lastCorrect && optionIndex1 === ctx.selected;

  if (isCorrect) {
    return `${base} border-green-600 bg-green-600/15 hover:bg-green-600/20`;
  }
  if (isWrongPick) {
    return `${base} border-red-600 bg-red-600/15 hover:bg-red-600/20`;
  }
  return `${base} opacity-60`;
}

export function RapidFireClient({ initialPlay }: { initialPlay: PlayResponse }) {
  const [state, dispatch] = useRapidFireReducer(initialPlay);
  const { setIsDirty, navigateSafe, registerBeforeNavigateConfirm } =
    useNavigationGuard();
  const { mutateAsync: submitAnswer } = useSubmitAnswer();
  const { mutateAsync: abandonSession } = useAbandon();

  const questionEnteredAtRef = useRef<number>(Date.now());
  const resultDirtyClearedRef = useRef(false);
  const [timerPulse, setTimerPulse] = useState(0);

  useEffect(() => {
    if (state.status === "question" && state.currentQuestion) {
      questionEnteredAtRef.current = Date.now();
    }
  }, [state.status, state.currentQuestion?.id, state.currentQuestion]);

  useEffect(() => {
    const inProgress =
      state.status === "loading" ||
      state.status === "question" ||
      state.status === "submitting" ||
      state.status === "feedback";
    setIsDirty(inProgress);
  }, [state.status, setIsDirty]);

  useEffect(() => {
    const inProgress =
      state.status === "loading" ||
      state.status === "question" ||
      state.status === "submitting" ||
      state.status === "feedback";
    if (!inProgress) {
      return undefined;
    }
    return registerBeforeNavigateConfirm(async () => {
      await abandonSession();
    });
  }, [abandonSession, registerBeforeNavigateConfirm, state.status]);

  useEffect(() => {
    if (state.status !== "result") {
      resultDirtyClearedRef.current = false;
      return;
    }
    if (resultDirtyClearedRef.current) return;
    resultDirtyClearedRef.current = true;
    dispatch({ type: "RESULT_SHOWN" });
    setIsDirty(false);
  }, [dispatch, setIsDirty, state.status]);

  useEffect(() => {
    if (state.status !== "feedback") return;
    const id = window.setTimeout(() => {
      dispatch({ type: "FEEDBACK_COMPLETE" });
    }, FEEDBACK_DURATION_MS);
    return () => window.clearTimeout(id);
  }, [dispatch, state.status]);

  useEffect(() => {
    const question = state.currentQuestion;
    if (state.status !== "submitting" || !question) return;
    let cancelled = false;
    void (async () => {
      try {
        const res = await submitAnswer({
          question_id: question.id,
          selected_option: state.submittedOption,
          time_ms: state.pendingTimeMs ?? 0,
        });
        if (cancelled) return;
        dispatch({ type: "ANSWER_SUCCESS", payload: res });
      } catch {
        if (cancelled) return;
        dispatch({ type: "ANSWER_ERROR" });
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [
    dispatch,
    state.currentQuestion,
    state.pendingTimeMs,
    state.status,
    state.submittedOption,
    submitAnswer,
  ]);

  useEffect(() => {
    if (state.status !== "question" || !state.currentQuestion) return;
    const limit = state.currentQuestion.time_limit_ms;
    const interval = window.setInterval(() => {
      const elapsed = Date.now() - questionEnteredAtRef.current;
      const displayElapsed = Math.max(0, elapsed - QUESTION_START_DELAY_MS);
      if (displayElapsed >= limit) {
        dispatch({
          type: "TIMER_EXPIRE",
          payload: { time_ms: limit },
        });
      }
      setTimerPulse((n) => n + 1);
    }, 50);
    return () => window.clearInterval(interval);
  }, [dispatch, state.currentQuestion, state.status]);

  const progressLabel =
    state.currentQuestion && state.questionsTotal > 0
      ? `Question ${state.questionsAnswered + 1} of ${state.questionsTotal}`
      : null;

  let timerBarPct: number | null = null;
  if (state.status === "question" && state.currentQuestion) {
    void timerPulse;
    const limit = state.currentQuestion.time_limit_ms;
    const elapsed = Date.now() - questionEnteredAtRef.current;
    const displayElapsed = Math.max(0, elapsed - QUESTION_START_DELAY_MS);
    const frac = Math.min(1, displayElapsed / limit);
    timerBarPct = (1 - frac) * 100;
  }

  if (state.status === "error") {
    return (
      <div className="mx-auto max-w-lg p-6">
        <h1 className="mb-2 font-semibold text-lg">Rapid Fire</h1>
        <p className="mb-4 text-muted-foreground">
          {state.errorMessage ?? "Something went wrong."}
        </p>
        <Button type="button" variant="outline" onClick={() => navigateSafe("/lobby")}>
          Back to Lobby
        </Button>
      </div>
    );
  }

  if (state.status === "result" && state.result) {
    const r = state.result;
    return (
      <div className="mx-auto max-w-lg space-y-6 p-6">
        <h1 className="font-semibold text-lg">Rapid Fire — Results</h1>
        <div className="space-y-2 rounded-xl border border-border bg-card p-4 shadow-sm">
          <p className="font-medium text-2xl tabular-nums">{r.score} points</p>
          <ul className="space-y-1 text-muted-foreground text-sm">
            <li>Correct: {r.correct_count}</li>
            <li>Wrong: {r.wrong_count}</li>
            <li>Skipped: {r.skipped_count}</li>
            <li>Time: {r.time_taken_seconds.toFixed(1)}s</li>
          </ul>
          <Button type="button" className="mt-4 w-full" onClick={() => navigateSafe("/lobby")}>
            Back to Lobby
          </Button>
        </div>
      </div>
    );
  }

  const q = state.currentQuestion;
  const showFeedback = state.status === "feedback";
  const phase: "question" | "feedback" = showFeedback ? "feedback" : "question";
  const locked = state.status === "submitting";

  return (
    <div className="mx-auto max-w-lg space-y-4 p-6">
      <header className="flex flex-col gap-1">
        <h1 className="font-semibold text-lg">Rapid Fire</h1>
        {progressLabel ? (
          <p className="text-muted-foreground text-sm">{progressLabel}</p>
        ) : null}
        <p className="font-medium text-sm tabular-nums">Score: {state.currentScore}</p>
      </header>

      {q ? (
        <div className="relative space-y-4 rounded-xl border border-border bg-card p-4 shadow-sm">
          {state.status === "question" && timerBarPct !== null ? (
            <div
              className="h-2 overflow-hidden rounded-full bg-muted"
              aria-label="Time remaining"
              role="progressbar"
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={Math.round(timerBarPct)}
            >
              <div
                className="h-full rounded-full bg-primary transition-[width] duration-75 ease-linear"
                style={{ width: `${timerBarPct}%` }}
              />
            </div>
          ) : null}

          {showFeedback ? (
            <div
              className="pointer-events-none absolute inset-0 z-10 flex items-end justify-center rounded-xl bg-background/40 pb-6"
              aria-live="polite"
            >
              <div className="rounded-md border border-border bg-card px-3 py-2 text-center font-medium text-sm shadow-sm">
                <p>{state.lastCorrect ? "Correct!" : "Wrong"}</p>
                <p className="mt-1 text-muted-foreground text-xs tabular-nums">
                  Score: {state.currentScore}
                </p>
              </div>
            </div>
          ) : null}

          <p className="pr-2 font-medium leading-snug">{q.question}</p>

          <div className="flex flex-col gap-2">
            {q.options.map((label, idx) => {
              const optionIndex1 = idx + 1;
              return (
                <Button
                  key={optionIndex1}
                  type="button"
                  variant="outline"
                  disabled={locked || showFeedback}
                  className={optionButtonClass(optionIndex1, {
                    phase,
                    selected: state.submittedOption,
                    correctOption: state.lastCorrectOption,
                    lastCorrect: state.lastCorrect,
                  })}
                  onClick={() => {
                    const limit = q.time_limit_ms;
                    const elapsed = Date.now() - questionEnteredAtRef.current;
                    dispatch({
                      type: "SELECT_OPTION",
                      payload: {
                        selected_option: optionIndex1,
                        time_ms: Math.min(limit, Math.max(0, elapsed)),
                      },
                    });
                  }}
                >
                  <span className="mr-2 font-mono text-muted-foreground text-xs">
                    {optionIndex1}.
                  </span>
                  {label}
                </Button>
              );
            })}
          </div>
        </div>
      ) : (
        <p className="text-muted-foreground text-sm">No question loaded.</p>
      )}
    </div>
  );
}
