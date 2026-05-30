"use client";

import { type FormEvent, useCallback, useEffect, useRef, useState } from "react";

import { useNavigationGuard } from "@/hooks/use-navigation-guard";
import { postPictureAbandon } from "@/lib/api/picture";
import { useSubmitPictureAnswer } from "@/services/picture/hooks";
import type { AnswerResponse, PlayResponse, Puzzle, Result } from "@/services/picture/schema";

import type { Celebration } from "./PictureView";
import { PictureView } from "./PictureView";

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
/** How long the correct-answer celebration stays on screen before clearing. */
const CELEBRATION_CLEAR_MS = 900;

export function PictureClient({ initialPlay }: Props) {
  const { setIsDirty, navigateSafe, registerBeforeNavigateConfirm } = useNavigationGuard();
  const { mutateAsync: submitAnswer, isPending } = useSubmitPictureAnswer();
  const wrongAnswerClearTimerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const celebrationTimerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const celebrationTokenRef = useRef(0);
  const streakRef = useRef(0);

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
  const [celebration, setCelebration] = useState<Celebration | null>(null);

  const clearWrongAnswerTimer = useCallback(() => {
    if (wrongAnswerClearTimerRef.current !== undefined) {
      clearTimeout(wrongAnswerClearTimerRef.current);
      wrongAnswerClearTimerRef.current = undefined;
    }
  }, []);

  const celebrateCorrect = useCallback((scoreDelta: number) => {
    if (celebrationTimerRef.current !== undefined) {
      clearTimeout(celebrationTimerRef.current);
    }
    streakRef.current += 1;
    celebrationTokenRef.current += 1;
    setCelebration({
      token: celebrationTokenRef.current,
      scoreDelta,
      streak: streakRef.current,
    });
    celebrationTimerRef.current = setTimeout(() => {
      setCelebration(null);
      celebrationTimerRef.current = undefined;
    }, CELEBRATION_CLEAR_MS);
  }, []);

  useEffect(() => {
    return () => {
      clearWrongAnswerTimer();
      if (celebrationTimerRef.current !== undefined) {
        clearTimeout(celebrationTimerRef.current);
      }
    };
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
    return (
      <PictureView
        viewState={{ status: "result", result }}
        onAnswerChange={() => {}}
        onSubmit={(e) => e.preventDefault()}
        onSkip={() => {}}
        onInputAnimationEnd={() => {}}
        onSessionExpired={() => {}}
        onBackToLobby={() => navigateSafe("/lobby")}
      />
    );
  }

  if (puzzle === null) {
    return (
      <PictureView
        viewState={{ status: "empty" }}
        onAnswerChange={() => {}}
        onSubmit={(e) => e.preventDefault()}
        onSkip={() => {}}
        onInputAnimationEnd={() => {}}
        onSessionExpired={() => {}}
        onBackToLobby={() => navigateSafe("/lobby")}
      />
    );
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!puzzle || isPending) return;
    clearWrongAnswerTimer();
    setInputShakeActive(false);
    try {
      const res = await submitAnswer({ puzzle_id: puzzle.id, submitted_answer: answer });
      setCurrentScore(res.current_score);
      if (res.correct && res.result === null) {
        celebrateCorrect(res.score_earned);
      } else if (!res.correct) {
        streakRef.current = 0;
      }
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
    streakRef.current = 0;
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
    <PictureView
      viewState={{
        status: "playing",
        puzzle,
        currentScore,
        answer,
        wrongMessage,
        inputShakeActive,
        isPending,
        timer:
          timerStartedAt !== null && timerLimitMs !== null
            ? { startedAt: timerStartedAt, limitMs: timerLimitMs }
            : null,
        celebration,
      }}
      onAnswerChange={setAnswer}
      onSubmit={handleSubmit}
      onSkip={() => void handleSkip()}
      onInputAnimationEnd={(e) => {
        if (e.animationName === "picture-input-shake") {
          setInputShakeActive(false);
        }
      }}
      onSessionExpired={handleSessionExpired}
      onBackToLobby={() => navigateSafe("/lobby")}
    />
  );
}
