"use client";

import { useEffect, useRef } from "react";

import type { Coordinates } from "@/services/word_hunt/schema";

import { cellsInTrace } from "../_lib/traceSnap";

type Props = {
  rows: number;
  cols: number;
  grid: string[][];
  highlighted: Coordinates[];
  preview?: Coordinates | null;
  missFlash?: Coordinates | null;
  landAnimation?: Coordinates | null;
  onDragStart: (row: number, col: number) => void;
  onDragMove: (row: number, col: number) => void;
  onDragEnd: () => void;
  disabled?: boolean;
};

function cellKey(row: number, col: number): string {
  return `${row},${col}`;
}

function isCellInTrace(row: number, col: number, trace: Coordinates | null | undefined): boolean {
  if (!trace) {
    return false;
  }
  return cellsInTrace(trace).some((cell) => cell.row === row && cell.col === col);
}

export function LetterGrid({
  rows,
  cols,
  grid,
  highlighted,
  preview = null,
  missFlash = null,
  landAnimation = null,
  onDragStart,
  onDragMove,
  onDragEnd,
  disabled = false,
}: Props) {
  const gridRef = useRef<HTMLDivElement>(null);
  const draggingRef = useRef(false);

  const resolveCellFromPoint = (clientX: number, clientY: number): { row: number; col: number } | null => {
    const target = document.elementFromPoint(clientX, clientY);
    const button = target?.closest<HTMLButtonElement>("[data-cell-row]");
    if (!button || !gridRef.current?.contains(button)) {
      return null;
    }
    return {
      row: Number(button.dataset.cellRow),
      col: Number(button.dataset.cellCol),
    };
  };

  useEffect(() => {
    const handlePointerMove = (event: PointerEvent) => {
      if (!draggingRef.current) {
        return;
      }
      const cell = resolveCellFromPoint(event.clientX, event.clientY);
      if (cell) {
        onDragMove(cell.row, cell.col);
      }
    };

    const handlePointerUp = (event: PointerEvent) => {
      if (!draggingRef.current) {
        return;
      }
      draggingRef.current = false;
      const cell = resolveCellFromPoint(event.clientX, event.clientY);
      if (cell) {
        onDragMove(cell.row, cell.col);
      }
      onDragEnd();
    };

    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", handlePointerUp);
    window.addEventListener("pointercancel", handlePointerUp);

    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", handlePointerUp);
      window.removeEventListener("pointercancel", handlePointerUp);
    };
  }, [onDragMove, onDragEnd]);

  const handlePointerDown = (row: number, col: number) => {
    if (disabled) {
      return;
    }
    draggingRef.current = true;
    onDragStart(row, col);
  };

  return (
    <div
      ref={gridRef}
      className="inline-grid gap-1 select-none touch-none"
      style={{ gridTemplateColumns: `repeat(${cols}, minmax(2rem, 1fr))` }}
    >
      {Array.from({ length: rows }, (_, row) =>
        Array.from({ length: cols }, (_, col) => {
          const letter = grid[row]?.[col] ?? "";
          const found = highlighted.some((trace) => isCellInTrace(row, col, trace));
          const selecting = isCellInTrace(row, col, preview);
          const missing = isCellInTrace(row, col, missFlash);
          const landing = isCellInTrace(row, col, landAnimation);

          let cellClass = "border-border bg-background";
          if (found) {
            cellClass = "border-green-600 bg-green-100";
          } else if (missing) {
            cellClass = "border-red-500 bg-red-100";
          } else if (selecting) {
            cellClass = "border-primary bg-primary/15";
          }

          return (
            <button
              key={cellKey(row, col)}
              type="button"
              data-cell-row={row}
              data-cell-col={col}
              className={`flex aspect-square items-center justify-center rounded border text-sm font-semibold transition-colors duration-150 ${cellClass} ${
                landing ? "scale-105 shadow-sm" : ""
              }`}
              disabled={disabled}
              onPointerDown={() => handlePointerDown(row, col)}
            >
              {letter}
            </button>
          );
        }),
      )}
    </div>
  );
}
