/** Assembled dumb Crossword screen: grid + clue panel play surface, or result. */

import type { CSSProperties, RefObject } from "react"

import { GameHeader } from "@/components/game/GameHeader"
import { ScoreReadout } from "@/components/game/ScoreReadout"
import type { PuzzleState, Result } from "@/services/crossword/schema"

import { ClueListPanel } from "./ClueListPanel"
import { CrosswordGrid } from "./CrosswordGrid"
import { ResultView } from "./ResultView"
import { ScoreIncrementChip } from "./ScoreIncrementChip"
import { Stopwatch } from "./Stopwatch"

export type CrosswordViewState =
  | {
      status: "playing"
      puzzle: PuzzleState
      sessionScore: number
      displayLetter: (row: number, col: number) => string
      lockedCells: Set<string>
      selectedCell: { row: number; col: number } | null
      activeEntryCells: Set<string>
      missFlashCells: Set<string>
      solveFlashOrder?: Map<string, number>
      activeEntryId: string | null
      showScoreIncrement: boolean
      submitDisabled: boolean
    }
  | { status: "result"; result: Result }

export type CrosswordViewProps = {
  viewState: CrosswordViewState
  onCellClick: (row: number, col: number) => void
  onClueClick: (entryId: string) => void
  onSubmit: () => void
  onBackToLobby: () => void
  gridRef?: RefObject<HTMLDivElement | null>
  hiddenInputRef?: RefObject<HTMLInputElement | null>
}

/** Crossword runs on its coral marquee accent. */
const CROSS_ACCENT = { "--accent": "var(--cross)" } as CSSProperties

export function CrosswordView(props: CrosswordViewProps) {
  const {
    viewState,
    onCellClick,
    onClueClick,
    onSubmit,
    onBackToLobby,
    gridRef,
    hiddenInputRef,
  } = props

  if (viewState.status === "result") {
    return (
      <div style={CROSS_ACCENT}>
        <ResultView result={viewState.result} onBackToLobby={onBackToLobby} />
      </div>
    )
  }

  const {
    puzzle,
    sessionScore,
    displayLetter,
    lockedCells,
    selectedCell,
    activeEntryCells,
    missFlashCells,
    solveFlashOrder,
    activeEntryId,
    showScoreIncrement,
    submitDisabled,
  } = viewState

  return (
    <div
      className="mx-auto flex max-w-6xl flex-col gap-8 p-4 sm:p-6"
      style={CROSS_ACCENT}
    >
      <GameHeader
        gameId="crossword"
        progress={`Solved ${puzzle.solved_count}/${puzzle.total_entries}`}
      >
        <Stopwatch startedAt={puzzle.started_at} />
        <ScoreReadout
          score={sessionScore}
          accessory={<ScoreIncrementChip visible={showScoreIncrement} />}
        />
        <button
          type="button"
          className="inline-flex h-11 items-center justify-center rounded-[var(--radius)] border-2 border-[var(--accent)] bg-[var(--accent)] px-5 text-[12px] font-extrabold tracking-[1.5px] text-bg uppercase shadow-[var(--shadow-cabinet-sm)] transition-[transform,box-shadow] duration-150 ease-[var(--ease-arcade)] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none disabled:pointer-events-none disabled:opacity-50 motion-reduce:transition-none"
          disabled={submitDisabled}
          onClick={onSubmit}
        >
          Submit
        </button>
      </GameHeader>

      <div className="overflow-x-auto">
        <div className="flex justify-center">
          <CrosswordGrid
            gridRef={gridRef}
            puzzle={puzzle}
            displayLetter={displayLetter}
            lockedCells={lockedCells}
            selectedCell={selectedCell}
            activeEntryCells={activeEntryCells}
            missFlashCells={missFlashCells}
            solveFlashOrder={solveFlashOrder}
            onCellClick={onCellClick}
            data-testid="crossword-grid"
          />
        </div>
      </div>
      <input
        ref={hiddenInputRef}
        aria-hidden
        tabIndex={-1}
        className="sr-only"
        onChange={() => {}}
      />

      <ClueListPanel
        clues={puzzle.clues}
        activeEntryId={activeEntryId}
        onClueClick={onClueClick}
      />
    </div>
  )
}
