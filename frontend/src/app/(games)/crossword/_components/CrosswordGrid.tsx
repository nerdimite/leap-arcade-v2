"use client";

import type { RefObject } from "react";

import type { PuzzleState } from "@/services/crossword/schema";

import { cellKey } from "../_lib/crosswordGrid";

type Props = {
  puzzle: PuzzleState;
  displayLetter: (row: number, col: number) => string;
  lockedCells: Set<string>;
  selectedCell: { row: number; col: number } | null;
  activeEntryCells: Set<string>;
  missFlashCells: Set<string>;
  onCellClick: (row: number, col: number) => void;
  gridRef?: RefObject<HTMLDivElement | null>;
  "data-testid"?: string;
};

export function CrosswordGrid({
  puzzle,
  displayLetter,
  lockedCells,
  selectedCell,
  activeEntryCells,
  missFlashCells,
  onCellClick,
  gridRef,
  "data-testid": dataTestId,
}: Props) {
  return (
    <div
      ref={gridRef}
      data-testid={dataTestId}
      className="inline-grid gap-0.5 border border-border p-2 outline-none"
      style={{
        gridTemplateColumns: `repeat(${puzzle.cols}, minmax(2rem, 2.5rem))`,
        gridTemplateRows: `repeat(${puzzle.rows}, minmax(2rem, 2.5rem))`,
      }}
      tabIndex={0}
    >
      {puzzle.cells.flatMap((row) =>
        row.map((cell) => {
          if (cell === null) {
            return null;
          }

          const key = cellKey(cell.row, cell.col);
          const isSelected =
            selectedCell?.row === cell.row && selectedCell?.col === cell.col;
          const isLocked = lockedCells.has(key);
          const isActive = activeEntryCells.has(key);
          const isMissFlash = missFlashCells.has(key);
          const letter = displayLetter(cell.row, cell.col);

          let cellClass = "border-neutral-300 bg-white";
          if (isLocked) {
            cellClass = "border-green-600 bg-green-100 text-green-900";
          } else if (isMissFlash) {
            cellClass = "border-red-500 bg-red-100 text-red-900";
          } else if (isSelected) {
            cellClass = "border-blue-500 bg-blue-50";
          } else if (isActive) {
            cellClass = "border-amber-400 bg-amber-50";
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
              }}
              className={`relative aspect-square border text-center text-sm font-semibold uppercase transition-colors duration-150 ${cellClass}`}
            >
              {cell.number != null ? (
                <span className="absolute left-0.5 top-0 text-[0.55rem] font-normal leading-none text-neutral-500">
                  {cell.number}
                </span>
              ) : null}
              <span>{letter}</span>
            </button>
          );
        }),
      )}
    </div>
  );
}
