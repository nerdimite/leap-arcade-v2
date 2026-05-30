"use client"

import type { RefObject } from "react"

import type { PuzzleState } from "@/services/crossword/schema"

import { cellKey } from "../_lib/crosswordGrid"

type Props = {
  puzzle: PuzzleState
  displayLetter: (row: number, col: number) => string
  lockedCells: Set<string>
  selectedCell: { row: number; col: number } | null
  activeEntryCells: Set<string>
  missFlashCells: Set<string>
  solveFlashOrder?: Map<string, number>
  onCellClick: (row: number, col: number) => void
  gridRef?: RefObject<HTMLDivElement | null>
  "data-testid"?: string
}

export function CrosswordGrid({
  puzzle,
  displayLetter,
  lockedCells,
  selectedCell,
  activeEntryCells,
  missFlashCells,
  solveFlashOrder,
  onCellClick,
  gridRef,
  "data-testid": dataTestId,
}: Props) {
  return (
    <div
      ref={gridRef}
      data-testid={dataTestId}
      className="inline-grid gap-0.5 rounded-[var(--radius)] border-2 border-line bg-panel p-2 outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
      style={{
        gridTemplateColumns: `repeat(${puzzle.cols}, minmax(2rem, 2.5rem))`,
        gridTemplateRows: `repeat(${puzzle.rows}, minmax(2rem, 2.5rem))`,
      }}
      // biome-ignore lint/a11y/noNoninteractiveTabindex: grid is intentionally focusable to capture keyboard entry for crossword cells
      tabIndex={0}
    >
      {puzzle.cells.flatMap((row) =>
        row.map((cell) => {
          if (cell === null) {
            return null
          }

          const key = cellKey(cell.row, cell.col)
          const isSelected =
            selectedCell?.row === cell.row && selectedCell?.col === cell.col
          const isLocked = lockedCells.has(key)
          const isActive = activeEntryCells.has(key)
          const isMissFlash = missFlashCells.has(key)
          const solveIndex = solveFlashOrder?.get(key)
          const isSolveFlash = solveIndex !== undefined
          const letter = displayLetter(cell.row, cell.col)

          let cellClass = "border-line bg-bg-2 text-ink"
          if (isLocked) {
            cellClass = "border-four bg-four/15 text-four"
          } else if (isMissFlash) {
            cellClass = "border-cross bg-cross/25 text-ink"
          } else if (isSelected) {
            cellClass = "border-wiki bg-wiki/20 text-ink"
          } else if (isActive) {
            cellClass = "border-rapid bg-rapid/15 text-ink"
          }

          return (
            <button
              key={key}
              type="button"
              data-cell-row={cell.row}
              data-cell-col={cell.col}
              onClick={() => onCellClick(cell.row, cell.col)}
              style={{
                gridRow: cell.row + 1,
                gridColumn: cell.col + 1,
                ...(isSolveFlash
                  ? { animationDelay: `${solveIndex * 45}ms` }
                  : {}),
              }}
              className={`relative flex aspect-square items-center justify-center border text-sm font-semibold uppercase transition-colors duration-150 ${cellClass} ${
                isSolveFlash
                  ? "animate-cell-solve motion-reduce:animate-none"
                  : ""
              }`}
            >
              {cell.number != null ? (
                <span className="absolute top-0 left-0.5 text-[0.55rem] leading-none font-normal text-ink-faint">
                  {cell.number}
                </span>
              ) : null}
              <span>{letter}</span>
            </button>
          )
        })
      )}
    </div>
  )
}
