"use client";

import { useCallback, useEffect, useReducer, useRef, useState } from "react";

import { useNavigationGuard } from "@/hooks/use-navigation-guard";
import {
  WORD_HUNT_MISS_FLASH_MS,
  WORD_HUNT_SCORE_INCREMENT_MS,
} from "@/lib/constants";
import {
  useWordHuntFind,
  useWordHuntPlay,
  useWordHuntSubmit,
} from "@/services/word_hunt/hooks";
import type { Coordinates, PlayResponse, Result } from "@/services/word_hunt/schema";

import {
  wordHuntDragInitialState,
  wordHuntDragReducer,
} from "../_hooks/useWordHuntDragReducer";
import { ClueListPanel } from "./ClueListPanel";
import { LetterGrid } from "./LetterGrid";
import { ResultView } from "./ResultView";
import { ScoreIncrementChip } from "./ScoreIncrementChip";

type Props = {
  initialPlay: PlayResponse;
};

export function WordHuntClient({ initialPlay }: Props) {
  const { mutateAsync: refreshPlay } = useWordHuntPlay();
  const { mutateAsync: submitFind, isPending: isFindPending } = useWordHuntFind();
  const { mutateAsync: submitSession, isPending: isSubmitPending } = useWordHuntSubmit();
  const { setIsDirty, registerBeforeNavigateConfirm, navigateSafe } = useNavigationGuard();

  const [play, setPlay] = useState(initialPlay);
  const [highlights, setHighlights] = useState<Coordinates[]>([]);
  const [dragState, dispatchDrag] = useReducer(wordHuntDragReducer, wordHuntDragInitialState);
  const submitInFlightRef = useRef(false);
  const findCommitSeqRef = useRef(0);
  const submitFindRef = useRef(submitFind);
  const refreshPlayRef = useRef(refreshPlay);
  submitFindRef.current = submitFind;
  refreshPlayRef.current = refreshPlay;

  const result: Result | null = play.result;
  const puzzle = play.puzzle;
  const inProgress = play.session_status === "active" && puzzle !== null;

  useEffect(() => {
    setIsDirty(inProgress);
  }, [inProgress, setIsDirty]);

  const handleSubmit = useCallback(async () => {
    if (submitInFlightRef.current || isSubmitPending) {
      return;
    }
    submitInFlightRef.current = true;
    try {
      const response = await submitSession();
      setPlay({
        session_status: "completed",
        session_score: response.result.score,
        puzzle: null,
        result: response.result,
      });
      setIsDirty(false);
    } finally {
      submitInFlightRef.current = false;
    }
  }, [isSubmitPending, setIsDirty, submitSession]);

  useEffect(() => {
    if (!inProgress) {
      return undefined;
    }
    return registerBeforeNavigateConfirm(handleSubmit);
  }, [handleSubmit, inProgress, registerBeforeNavigateConfirm]);

  useEffect(() => {
    if (puzzle) {
      const foundCoords = puzzle.clues
        .filter((clue) => clue.found && clue.coordinates)
        .map((clue) => clue.coordinates as Coordinates);
      setHighlights(foundCoords);
    }
  }, [puzzle]);

  useEffect(() => {
    const trace = dragState.pendingCommit;
    if (!trace || !inProgress) {
      return;
    }

    const commitSeq = ++findCommitSeqRef.current;

    const commitTrace = async () => {
      try {
        const response = await submitFindRef.current(trace);
        if (commitSeq !== findCommitSeqRef.current) {
          return;
        }

        if (response.matched && response.word) {
          dispatchDrag({ type: "FIND_HIT", payload: { trace: response.word.coordinates } });
          setHighlights((prev) => [...prev, response.word!.coordinates]);
        } else {
          dispatchDrag({ type: "FIND_MISS", payload: { trace } });
        }

        if (response.session_status === "completed" && response.result) {
          setPlay({
            session_status: response.session_status,
            session_score: response.session_score,
            puzzle: null,
            result: response.result,
          });
          setIsDirty(false);
          dispatchDrag({ type: "CLEAR_PENDING_COMMIT" });
          return;
        }

        const refreshed = await refreshPlayRef.current();
        if (commitSeq !== findCommitSeqRef.current) {
          return;
        }
        setPlay(refreshed);
      } finally {
        if (commitSeq === findCommitSeqRef.current) {
          dispatchDrag({ type: "CLEAR_PENDING_COMMIT" });
        }
      }
    };

    void commitTrace();
  }, [dragState.pendingCommit, inProgress, setIsDirty]);

  useEffect(() => {
    if (!dragState.missFlash) {
      return undefined;
    }
    const timeout = window.setTimeout(() => {
      dispatchDrag({ type: "MISS_FLASH_COMPLETE" });
    }, WORD_HUNT_MISS_FLASH_MS);
    return () => {
      window.clearTimeout(timeout);
    };
  }, [dragState.missFlash]);

  useEffect(() => {
    if (!dragState.showScoreIncrement) {
      return undefined;
    }
    const timeout = window.setTimeout(() => {
      dispatchDrag({ type: "SCORE_INCREMENT_COMPLETE" });
    }, WORD_HUNT_SCORE_INCREMENT_MS);
    return () => {
      window.clearTimeout(timeout);
    };
  }, [dragState.showScoreIncrement]);

  useEffect(() => {
    if (!dragState.landAnimation) {
      return undefined;
    }
    const timeout = window.setTimeout(() => {
      dispatchDrag({ type: "LAND_ANIMATION_COMPLETE" });
    }, WORD_HUNT_MISS_FLASH_MS);
    return () => {
      window.clearTimeout(timeout);
    };
  }, [dragState.landAnimation]);

  const handleDragStart = useCallback((row: number, col: number) => {
    dispatchDrag({ type: "DRAG_START", payload: { row, col } });
  }, []);

  const handleDragMove = useCallback(
    (row: number, col: number) => {
      if (!puzzle) {
        return;
      }
      dispatchDrag({
        type: "DRAG_MOVE",
        payload: { row, col, rows: puzzle.rows, cols: puzzle.cols },
      });
    },
    [puzzle],
  );

  const handleDragEnd = useCallback(() => {
    if (!puzzle) {
      return;
    }
    dispatchDrag({
      type: "DRAG_END",
      payload: { rows: puzzle.rows, cols: puzzle.cols },
    });
  }, [puzzle]);

  if (result) {
    return <ResultView result={result} onBackToLobby={() => navigateSafe("/lobby")} />;
  }

  if (!puzzle) {
    return null;
  }

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6 p-6 lg:flex-row">
      <div>
        <h1 className="mb-4 text-2xl font-semibold">Word Hunt</h1>
        <p className="relative mb-4 inline-block text-sm text-muted-foreground">
          Score: {play.session_score} · Found {puzzle.found_count} / {puzzle.total_words}
          <ScoreIncrementChip visible={dragState.showScoreIncrement} />
        </p>
        <LetterGrid
          rows={puzzle.rows}
          cols={puzzle.cols}
          grid={puzzle.grid}
          highlighted={highlights}
          preview={dragState.dragPreview}
          missFlash={dragState.missFlash}
          landAnimation={dragState.landAnimation}
          onDragStart={handleDragStart}
          onDragMove={handleDragMove}
          onDragEnd={handleDragEnd}
          disabled={isFindPending || isSubmitPending}
        />
      </div>
      <div className="flex-1">
        <h2 className="mb-3 text-lg font-medium">Clues</h2>
        <ClueListPanel clues={puzzle.clues} />
        <button
          type="button"
          className="mt-6 rounded-md bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50"
          disabled={isSubmitPending || isFindPending}
          onClick={() => void handleSubmit()}
        >
          Submit
        </button>
      </div>
    </div>
  );
}
