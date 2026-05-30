"use client";

import { useCallback, useEffect, useMemo, useReducer, useRef } from "react";

import { useNavigationGuard } from "@/hooks/use-navigation-guard";
import {
  CROSSWORD_MISS_FLASH_MS,
  CROSSWORD_SCORE_INCREMENT_MS,
} from "@/lib/constants";
import {
  useCrosswordCheck,
  useCrosswordPlay,
  useCrosswordSubmit,
} from "@/services/crossword/hooks";
import type { Clue, PlayResponse, Result } from "@/services/crossword/schema";

import {
  cellKey,
  collectEntryCellKeys,
  entryLetters,
  getActiveEntryCellKeys,
} from "../_lib/crosswordGrid";
import {
  crosswordPlayInitialState,
  crosswordPlayReducer,
  getActiveClueEntryId,
  getDisplayLetter,
} from "../_hooks/crosswordPlayReducer";
import { ClueListPanel } from "./ClueListPanel";
import { CrosswordGrid } from "./CrosswordGrid";
import { ResultView } from "./ResultView";
import { ScoreIncrementChip } from "./ScoreIncrementChip";

type Props = {
  initialPlay: PlayResponse;
};

function cellsForEntryIds(
  cluesById: Record<string, Clue>,
  entryIds: string[],
): Set<string> {
  const cells = new Set<string>();
  for (const entryId of entryIds) {
    const clue = cluesById[entryId];
    if (!clue) {
      continue;
    }
    for (const key of collectEntryCellKeys(clue)) {
      cells.add(key);
    }
  }
  return cells;
}

export function CrosswordClient({ initialPlay }: Props) {
  const { mutateAsync: refreshPlay } = useCrosswordPlay();
  const { mutateAsync: submitCheck } = useCrosswordCheck();
  const { mutateAsync: submitSession, isPending: isSubmitPending } = useCrosswordSubmit();
  const { setIsDirty, registerBeforeNavigateConfirm, navigateSafe } = useNavigationGuard();

  const [play, setPlay] = useReducer(
    (state: PlayResponse, next: PlayResponse) => next,
    initialPlay,
  );
  const [playState, dispatchPlay] = useReducer(
    crosswordPlayReducer,
    crosswordPlayInitialState,
  );

  const gridRef = useRef<HTMLDivElement>(null);
  const hiddenInputRef = useRef<HTMLInputElement>(null);
  const checkSeqRef = useRef(0);
  const submitInFlightRef = useRef(false);
  const playStateRef = useRef(playState);
  const submitCheckRef = useRef(submitCheck);
  const refreshPlayRef = useRef(refreshPlay);
  playStateRef.current = playState;
  submitCheckRef.current = submitCheck;
  refreshPlayRef.current = refreshPlay;

  const puzzle = play.puzzle;
  const result: Result | null = play.result;
  const inProgress = play.session_status === "active" && puzzle !== null;

  useEffect(() => {
    setIsDirty(inProgress);
  }, [inProgress, setIsDirty]);

  useEffect(() => {
    if (puzzle) {
      dispatchPlay({ type: "SET_PUZZLE", payload: { puzzle } });
    }
  }, [puzzle]);

  const lockedCells = useMemo(() => {
    if (!playState.context) {
      return new Set<string>();
    }
    return playState.context.lockedCells;
  }, [playState.context]);

  const activeEntryCells = useMemo(() => {
    if (!playState.context) {
      return new Set<string>();
    }
    return new Set(
      getActiveEntryCellKeys(
        playState.context,
        playState.cursor,
        playState.direction,
      ),
    );
  }, [playState.context, playState.cursor, playState.direction]);

  const missFlashCells = useMemo(() => {
    if (!playState.context) {
      return new Set<string>();
    }
    return cellsForEntryIds(
      playState.context.cluesById,
      playState.missFlashEntryIds,
    );
  }, [playState.context, playState.missFlashEntryIds]);

  const displayLetter = useCallback(
    (row: number, col: number) => getDisplayLetter(playState, cellKey(row, col)),
    [playState],
  );

  const applyPlay = useCallback((next: PlayResponse) => {
    setPlay(next);
  }, []);

  const runCheck = useCallback(
    async (entryId: string, seq: number) => {
      const { context, draft } = playStateRef.current;
      if (!context) {
        return;
      }
      const letters = entryLetters(context, draft, entryId);
      try {
        const response = await submitCheckRef.current({
          entry_id: entryId,
          letters,
        });
        if (seq !== checkSeqRef.current) {
          return;
        }

        if (response.correct) {
          dispatchPlay({ type: "CHECK_HIT", payload: { entryId } });
        } else {
          dispatchPlay({ type: "CHECK_MISS", payload: { entryId } });
        }

        if (response.session_status === "completed" && response.result) {
          applyPlay({
            session_status: response.session_status,
            session_score: response.session_score,
            puzzle: null,
            result: response.result,
          });
          return;
        }

        const refreshed = await refreshPlayRef.current();
        if (seq !== checkSeqRef.current) {
          return;
        }
        applyPlay(refreshed);
      } finally {
        if (seq === checkSeqRef.current) {
          dispatchPlay({ type: "CHECK_FINISHED", payload: { entryId } });
        }
      }
    },
    [applyPlay],
  );

  useEffect(() => {
    if (!inProgress || playState.checkQueue.length === 0) {
      return;
    }

    const seq = ++checkSeqRef.current;
    const queue = playState.checkQueue;
    const pending = new Set(playState.pendingCheckEntryIds);

    dispatchPlay({ type: "CLEAR_CHECK_QUEUE" });

    for (const entryId of queue) {
      if (pending.has(entryId)) {
        continue;
      }
      pending.add(entryId);
      dispatchPlay({ type: "CHECK_STARTED", payload: { entryId } });
      void runCheck(entryId, seq);
    }
  }, [inProgress, playState.checkQueue, playState.pendingCheckEntryIds, runCheck]);

  useEffect(() => {
    if (playState.missFlashEntryIds.length === 0) {
      return undefined;
    }
    const timeout = window.setTimeout(() => {
      dispatchPlay({ type: "MISS_FLASH_COMPLETE" });
    }, CROSSWORD_MISS_FLASH_MS);
    return () => {
      window.clearTimeout(timeout);
    };
  }, [playState.missFlashEntryIds]);

  useEffect(() => {
    if (!playState.showScoreIncrement) {
      return undefined;
    }
    const timeout = window.setTimeout(() => {
      dispatchPlay({ type: "SCORE_INCREMENT_COMPLETE" });
    }, CROSSWORD_SCORE_INCREMENT_MS);
    return () => {
      window.clearTimeout(timeout);
    };
  }, [playState.showScoreIncrement]);

  useEffect(() => {
    if (!inProgress) {
      return undefined;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      if (
        target &&
        (target.tagName === "INPUT" || target.tagName === "TEXTAREA") &&
        target !== hiddenInputRef.current
      ) {
        return;
      }

      if (event.key === "Tab" || event.key === " ") {
        event.preventDefault();
        dispatchPlay({ type: "TOGGLE_DIRECTION" });
        return;
      }

      if (event.key === "Backspace") {
        event.preventDefault();
        dispatchPlay({ type: "BACKSPACE" });
        return;
      }

      if (event.key === "ArrowLeft") {
        event.preventDefault();
        dispatchPlay({ type: "ARROW", payload: { deltaRow: 0, deltaCol: -1 } });
        return;
      }
      if (event.key === "ArrowRight") {
        event.preventDefault();
        dispatchPlay({ type: "ARROW", payload: { deltaRow: 0, deltaCol: 1 } });
        return;
      }
      if (event.key === "ArrowUp") {
        event.preventDefault();
        dispatchPlay({ type: "ARROW", payload: { deltaRow: -1, deltaCol: 0 } });
        return;
      }
      if (event.key === "ArrowDown") {
        event.preventDefault();
        dispatchPlay({ type: "ARROW", payload: { deltaRow: 1, deltaCol: 0 } });
        return;
      }

      if (/^[a-zA-Z]$/.test(event.key)) {
        event.preventDefault();
        dispatchPlay({ type: "TYPE_LETTER", payload: { letter: event.key } });
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [inProgress]);

  const handleCellClick = useCallback((row: number, col: number) => {
    dispatchPlay({ type: "SELECT_CELL", payload: { row, col } });
    hiddenInputRef.current?.focus();
    gridRef.current?.focus();
  }, []);

  const handleClueClick = useCallback((entryId: string) => {
    dispatchPlay({ type: "SELECT_CLUE", payload: { entryId } });
    hiddenInputRef.current?.focus();
    gridRef.current?.focus();
  }, []);

  const handleSubmit = useCallback(async () => {
    if (submitInFlightRef.current || isSubmitPending) {
      return;
    }
    submitInFlightRef.current = true;
    try {
      const response = await submitSession();
      applyPlay({
        session_status: "completed",
        session_score: response.result.score,
        puzzle: null,
        result: response.result,
      });
      setIsDirty(false);
    } finally {
      submitInFlightRef.current = false;
    }
  }, [applyPlay, isSubmitPending, setIsDirty, submitSession]);

  useEffect(() => {
    if (!inProgress) {
      return undefined;
    }
    return registerBeforeNavigateConfirm(handleSubmit);
  }, [handleSubmit, inProgress, registerBeforeNavigateConfirm]);

  if (result) {
    return (
      <ResultView result={result} onBackToLobby={() => navigateSafe("/lobby")} />
    );
  }

  if (!puzzle) {
    return null;
  }

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6 p-4 lg:flex-row">
      <div className="space-y-4">
        <div className="flex items-center justify-between gap-4">
          <p className="relative text-sm text-neutral-600">
            Score: {play.session_score} · Solved {puzzle.solved_count}/{puzzle.total_entries}
            <ScoreIncrementChip visible={playState.showScoreIncrement} />
          </p>
          <button
            type="button"
            className="rounded-md bg-neutral-900 px-4 py-2 text-sm text-white disabled:opacity-50"
            disabled={isSubmitPending}
            onClick={() => void handleSubmit()}
          >
            Submit
          </button>
        </div>
        <CrosswordGrid
          gridRef={gridRef}
          puzzle={puzzle}
          displayLetter={displayLetter}
          lockedCells={lockedCells}
          selectedCell={playState.cursor}
          activeEntryCells={activeEntryCells}
          missFlashCells={missFlashCells}
          onCellClick={handleCellClick}
          data-testid="crossword-grid"
        />
        <input
          ref={hiddenInputRef}
          aria-hidden
          tabIndex={-1}
          className="sr-only"
          onChange={() => {}}
        />
      </div>
      <div className="min-w-[16rem] flex-1">
        <ClueListPanel
          clues={puzzle.clues}
          activeEntryId={getActiveClueEntryId(playState)}
          onClueClick={handleClueClick}
        />
      </div>
    </div>
  );
}
