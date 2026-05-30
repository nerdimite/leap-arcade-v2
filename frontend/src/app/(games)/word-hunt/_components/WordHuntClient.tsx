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
import { WordHuntView } from "./WordHuntView";

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
    return (
      <WordHuntView
        viewState={{ status: "result", result }}
        onDragStart={() => {}}
        onDragMove={() => {}}
        onDragEnd={() => {}}
        onSubmit={() => {}}
        onBackToLobby={() => navigateSafe("/lobby")}
      />
    );
  }

  if (!puzzle) {
    return null;
  }

  return (
    <WordHuntView
      viewState={{
        status: "playing",
        puzzle,
        sessionScore: play.session_score,
        highlights,
        dragPreview: dragState.dragPreview,
        missFlash: dragState.missFlash,
        landAnimation: dragState.landAnimation,
        showScoreIncrement: dragState.showScoreIncrement,
        disabled: isFindPending || isSubmitPending,
      }}
      onDragStart={handleDragStart}
      onDragMove={handleDragMove}
      onDragEnd={handleDragEnd}
      onSubmit={() => void handleSubmit()}
      onBackToLobby={() => navigateSafe("/lobby")}
    />
  );
}
