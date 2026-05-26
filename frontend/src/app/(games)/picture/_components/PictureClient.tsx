"use client";

import Image from "next/image";
import { type FormEvent, useCallback, useEffect, useRef, useState } from "react";

import { useNavigationGuard } from "@/hooks/use-navigation-guard";
import { postPictureAbandon } from "@/lib/api/picture";
import { cn } from "@/lib/utils";
import { useSubmitPictureAnswer } from "@/services/picture/hooks";
import type { AnswerResponse, PlayResponse, Puzzle, Result } from "@/services/picture/schema";

import { ResultScreen } from "./ResultScreen";
import { SessionTimer } from "./SessionTimer";

type Props = {
  initialPlay: PlayResponse;
};

function applyAnswer(
  previous: Puzzle | null,
  res: AnswerResponse,
): { puzzle: Puzzle | null; result: Result | null; wrong: string | null } {
  if (res.result) {
    return { puzzle: null, result: res.result, wrong: null };
  }
  if (res.correct && res.next_puzzle) {
    return { puzzle: res.next_puzzle, result: null, wrong: null };
  }
  if (!res.correct && res.next_puzzle) {
    return { puzzle: res.next_puzzle, result: null, wrong: null };
  }
  if (res.correct) {
    return { puzzle: previous, result: null, wrong: null };
  }
  return {
    puzzle: previous,
    result: null,
    wrong: "Incorrect, try again.",
  };
}

const WRONG_ANSWER_CLEAR_MS = 1000;

export function PictureClient({ initialPlay }: Props) {
  const { setIsDirty, navigateSafe, registerBeforeNavigateConfirm } = useNavigationGuard();
  const { mutateAsync: submitAnswer, isPending } = useSubmitPictureAnswer();
  const wrongAnswerClearTimerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const [timerStartedAt, setTimerStartedAt] = useState<string | null>(() =>
    initialPlay.status === "active" ? initialPlay.session_started_at : null,
  );
  const [timerLimitMs, setTimerLimitMs] = useState<number | null>(() =>
    initialPlay.status === "active" ? initialPlay.time_limit_ms : null,
  );

  const [puzzle, setPuzzle] = useState<Puzzle | null>(() =>
    initialPlay.status === "active" ? initialPlay.puzzle : null,
  );
  const [result, setResult] = useState<Result | null>(() =>
    initialPlay.status !== "active" ? initialPlay.result : null,
  );
  const [currentScore, setCurrentScore] = useState(0);
  const [answer, setAnswer] = useState("");
  const [wrongMessage, setWrongMessage] = useState<string | null>(null);
  const [inputShakeActive, setInputShakeActive] = useState(false);

  const clearWrongAnswerTimer = useCallback(() => {
    if (wrongAnswerClearTimerRef.current !== undefined) {
      clearTimeout(wrongAnswerClearTimerRef.current);
      wrongAnswerClearTimerRef.current = undefined;
    }
  }, []);

  useEffect(() => {
    return () => clearWrongAnswerTimer();
  }, [clearWrongAnswerTimer]);

  const handleSessionExpired = useCallback(async () => {
    try {
      const { result: next } = await postPictureAbandon();
      setResult(next);
      setPuzzle(null);
      setTimerStartedAt(null);
      setTimerLimitMs(null);
    } catch {
      setWrongMessage("Time is up, but we could not save your session. Try again.");
    }
  }, []);

  useEffect(() => {
    return registerBeforeNavigateConfirm(async () => {
      if (puzzle === null || result !== null) return;
      await postPictureAbandon();
    });
  }, [puzzle, result, registerBeforeNavigateConfirm]);

  useEffect(() => {
    if (puzzle === null || result !== null) return;

    const onUnload = (): void => {
      void postPictureAbandon({ keepalive: true });
    };

    window.addEventListener("beforeunload", onUnload);
    return () => window.removeEventListener("beforeunload", onUnload);
  }, [puzzle, result]);

  useEffect(() => {
    const inPlay = puzzle !== null && result === null;
    setIsDirty(inPlay);
  }, [puzzle, result, setIsDirty]);

  if (result !== null) {
    return <ResultScreen result={result} onBackToLobby={() => navigateSafe("/lobby")} />;
  }

  if (puzzle === null) {
    return (
      <div className="p-6">
        <p className="text-muted-foreground text-sm">No puzzle available.</p>
      </div>
    );
  }

  const imgSrc = `/games/picture/${puzzle.image_filename}`;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!puzzle || isPending) return;
    clearWrongAnswerTimer();
    setInputShakeActive(false);
    try {
      const res = await submitAnswer({ puzzle_id: puzzle.id, submitted_answer: answer });
      setCurrentScore(res.current_score);
      const next = applyAnswer(puzzle, res);
      setPuzzle(next.puzzle);
      if (next.result !== null) {
        setResult(next.result);
        setTimerStartedAt(null);
        setTimerLimitMs(null);
      }
      const advanced = Boolean(res.result) || Boolean(res.next_puzzle);
      if (!advanced && !res.correct) {
        setWrongMessage("Incorrect, try again.");
        setInputShakeActive(true);
        wrongAnswerClearTimerRef.current = setTimeout(() => {
          setAnswer("");
          setWrongMessage(null);
          wrongAnswerClearTimerRef.current = undefined;
        }, WRONG_ANSWER_CLEAR_MS);
      } else {
        setWrongMessage(next.wrong);
        if (advanced || res.correct) {
          setAnswer("");
        }
      }
    } catch {
      setWrongMessage("Something went wrong. Try again.");
    }
  }

  async function handleSkip() {
    if (!puzzle || isPending) return;
    clearWrongAnswerTimer();
    setInputShakeActive(false);
    try {
      const res = await submitAnswer({ puzzle_id: puzzle.id, submitted_answer: null });
      setCurrentScore(res.current_score);
      const next = applyAnswer(puzzle, res);
      setPuzzle(next.puzzle);
      if (next.result !== null) {
        setResult(next.result);
        setTimerStartedAt(null);
        setTimerLimitMs(null);
      }
      setWrongMessage(next.wrong);
      const advanced = Boolean(res.result) || Boolean(res.next_puzzle);
      if (advanced) {
        setAnswer("");
      }
    } catch {
      setWrongMessage("Something went wrong. Try again.");
    }
  }

  return (
    <div className="mx-auto flex max-w-xl flex-col gap-4 p-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-semibold tracking-tight">Picture Illustration</h1>
        <div className="flex flex-wrap items-center justify-end gap-4">
          {timerStartedAt !== null && timerLimitMs !== null ? (
            <SessionTimer
              sessionStartedAt={timerStartedAt}
              timeLimitMs={timerLimitMs}
              onExpired={handleSessionExpired}
            />
          ) : null}
          <div className="text-muted-foreground text-sm tabular-nums">{currentScore} pts</div>
        </div>
      </header>
      <p className="text-muted-foreground text-sm">
        {puzzle.puzzles_answered} / {puzzle.puzzles_total} puzzles solved — decode the image below.
      </p>
      <div className="relative aspect-video w-full overflow-hidden rounded-lg border bg-muted">
        <Image src={imgSrc} alt="Picture puzzle clue" fill className="object-contain" sizes="100vw" priority />
      </div>
      <form className="flex flex-col gap-3" onSubmit={handleSubmit}>
        <label className="text-sm font-medium" htmlFor="picture-answer">
          Your answer
        </label>
        <input
          id="picture-answer"
          className={cn(
            "rounded-md border bg-background px-3 py-2 text-sm outline-none ring-offset-background focus-visible:ring-2 focus-visible:ring-ring",
            inputShakeActive && "animate-picture-input-shake",
          )}
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          onAnimationEnd={(e) => {
            if (e.animationName === "picture-input-shake") {
              setInputShakeActive(false);
            }
          }}
          autoComplete="off"
          disabled={isPending}
        />
        {wrongMessage ? <p className="text-sm text-destructive">{wrongMessage}</p> : null}
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="submit"
            disabled={isPending || answer.trim().length === 0}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:pointer-events-none disabled:opacity-50"
          >
            Submit
          </button>
          <button
            type="button"
            disabled={isPending}
            className="border-border text-muted-foreground rounded-md border bg-transparent px-4 py-2 text-sm font-medium hover:bg-accent/60 disabled:pointer-events-none disabled:opacity-50"
            onClick={() => void handleSkip()}
          >
            Skip →
          </button>
        </div>
      </form>
    </div>
  );
}
