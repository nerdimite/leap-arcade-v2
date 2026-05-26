"use client";

import Image from "next/image";
import { useCallback, useEffect, useRef, useState } from "react";

import { AnswerOverlay } from "@/app/(games)/four-pics/_components/AnswerOverlay";
import { ResultView } from "@/app/(games)/four-pics/_components/ResultView";
import { Stopwatch } from "@/app/(games)/four-pics/_components/Stopwatch";
import { elapsedMsFromStartedAt } from "@/app/(games)/four-pics/_lib/stopwatch";
import { useNavigationGuard } from "@/hooks/use-navigation-guard";
import { FOUR_PICS_ANSWER_OVERLAY_MS } from "@/lib/constants";
import { cn } from "@/lib/utils";
import { useAbandonFourPics, useSubmitFourPicsAnswer } from "@/services/four_pics/hooks";
import type { AnswerResponse, PlayResponse, QuestionState, Result } from "@/services/four_pics/schema";

type Props = {
  initialPlay: PlayResponse;
};

type OverlayState = {
  correct: boolean;
  score: number;
  timeBonus: number;
  selectedIndex: number;
};

export function FourPicsClient({ initialPlay }: Props) {
  const { setIsDirty, navigateSafe, registerBeforeNavigateConfirm } =
    useNavigationGuard();
  const { mutateAsync: submitAnswer, isPending } = useSubmitFourPicsAnswer();
  const { mutateAsync: abandonSession } = useAbandonFourPics();
  const advanceTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingAdvanceRef = useRef<AnswerResponse | null>(null);
  const resultDirtyClearedRef = useRef(false);

  const [question, setQuestion] = useState<QuestionState | null>(() =>
    initialPlay.session_status === "active" ? initialPlay.question : null,
  );
  const [result, setResult] = useState<Result | null>(() =>
    initialPlay.session_status !== "active" ? initialPlay.result : null,
  );
  const [sessionScore, setSessionScore] = useState(initialPlay.session_score);
  const [overlay, setOverlay] = useState<OverlayState | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const isInputLocked = isPending || overlay !== null;

  useEffect(() => {
    const inPlay = question !== null && result === null;
    setIsDirty(inPlay);
  }, [question, result, setIsDirty]);

  useEffect(() => {
    const inPlay = question !== null && result === null;
    if (!inPlay) {
      return undefined;
    }
    return registerBeforeNavigateConfirm(async () => {
      await abandonSession();
    });
  }, [abandonSession, question, registerBeforeNavigateConfirm, result]);

  useEffect(() => {
    if (result === null) {
      resultDirtyClearedRef.current = false;
      return;
    }
    if (resultDirtyClearedRef.current) return;
    resultDirtyClearedRef.current = true;
    setIsDirty(false);
  }, [result, setIsDirty]);

  const applyAdvance = useCallback((res: AnswerResponse) => {
    setSessionScore(res.session_score);
    setOverlay(null);
    pendingAdvanceRef.current = null;

    if (res.result) {
      setQuestion(null);
      setResult(res.result);
      return;
    }

    if (res.question) {
      setQuestion(res.question);
    }
  }, []);

  useEffect(() => {
    return () => {
      if (advanceTimeoutRef.current !== null) {
        clearTimeout(advanceTimeoutRef.current);
      }
    };
  }, []);

  const scheduleAdvance = useCallback(
    (res: AnswerResponse) => {
      pendingAdvanceRef.current = res;
      if (advanceTimeoutRef.current !== null) {
        clearTimeout(advanceTimeoutRef.current);
      }
      advanceTimeoutRef.current = setTimeout(() => {
        advanceTimeoutRef.current = null;
        const pending = pendingAdvanceRef.current;
        if (pending) {
          applyAdvance(pending);
        }
      }, FOUR_PICS_ANSWER_OVERLAY_MS);
    },
    [applyAdvance],
  );

  const handleSelect = useCallback(
    async (selectedIndex: number) => {
      if (question === null || isInputLocked) {
        return;
      }

      setSubmitError(null);
      const timeMs = elapsedMsFromStartedAt(question.started_at);

      try {
        const res = await submitAnswer({
          question_id: question.question_id,
          selected_index: selectedIndex,
          time_ms: timeMs,
        });
        setSessionScore(res.session_score);
        setOverlay({
          correct: res.correct,
          score: res.score,
          timeBonus: res.time_bonus,
          selectedIndex,
        });
        scheduleAdvance(res);
      } catch {
        setSubmitError("Could not submit answer. Try again.");
      }
    },
    [isInputLocked, question, scheduleAdvance, submitAnswer],
  );

  if (result !== null) {
    return <ResultView result={result} onBackToLobby={() => navigateSafe("/lobby")} />;
  }

  if (question === null) {
    return (
      <div className="p-6">
        <p className="text-muted-foreground text-sm">No question available.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto flex max-w-lg flex-col gap-4 p-6">
      <div className="flex items-center justify-between gap-4">
        <h1 className="font-semibold text-xl">Four Pics, One Lie</h1>
        <div className="flex flex-col items-end gap-1">
          <p className="text-muted-foreground text-sm tabular-nums">
            {question.question_number}/{question.total_questions} · {sessionScore} pts
          </p>
          <Stopwatch startedAt={question.started_at} />
        </div>
      </div>

      {submitError !== null ? (
        <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-destructive text-sm">
          {submitError}
        </p>
      ) : null}

      <div className="relative">
        <div className="grid grid-cols-2 gap-3">
          {question.image_paths.map((path, index) => (
            <button
              key={path}
              type="button"
              disabled={isInputLocked}
              className={cn(
                "relative aspect-square overflow-hidden rounded-lg border bg-muted disabled:pointer-events-none disabled:opacity-60",
                overlay?.correct && overlay.selectedIndex === index
                  ? "ring-2 ring-emerald-300 ring-offset-2 ring-offset-background"
                  : null,
              )}
              onClick={() => void handleSelect(index)}
            >
              <Image
                src={path}
                alt={`Option ${index + 1}`}
                fill
                className="object-cover"
                sizes="(max-width: 512px) 50vw, 256px"
              />
            </button>
          ))}
        </div>
        {overlay !== null ? (
          <AnswerOverlay
            correct={overlay.correct}
            score={overlay.score}
            timeBonus={overlay.timeBonus}
            selectedIndex={overlay.selectedIndex}
          />
        ) : null}
      </div>
    </div>
  );
}
