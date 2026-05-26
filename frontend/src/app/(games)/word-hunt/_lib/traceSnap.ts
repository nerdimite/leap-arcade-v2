import type { Coordinates } from "@/services/word_hunt/schema";

function sign(value: number): number {
  if (value > 0) {
    return 1;
  }
  if (value < 0) {
    return -1;
  }
  return 0;
}

export function snapTraceFromPointer(
  startRow: number,
  startCol: number,
  pointerRow: number,
  pointerCol: number,
  rows: number,
  cols: number,
): Coordinates | null {
  const dr = pointerRow - startRow;
  const dc = pointerCol - startCol;

  if (dr === 0 && dc === 0) {
    return null;
  }

  const absDr = Math.abs(dr);
  const absDc = Math.abs(dc);

  let snapDr: number;
  let snapDc: number;

  if (absDr > absDc * 2) {
    snapDr = sign(dr);
    snapDc = 0;
  } else if (absDc > absDr * 2) {
    snapDr = 0;
    snapDc = sign(dc);
  } else {
    snapDr = sign(dr);
    snapDc = sign(dc);
  }

  let length: number;
  if (snapDr === 0) {
    length = absDc;
  } else if (snapDc === 0) {
    length = absDr;
  } else {
    length = Math.max(absDr, absDc);
  }

  while (length > 0) {
    const endRow = startRow + snapDr * length;
    const endCol = startCol + snapDc * length;
    if (endRow >= 0 && endRow < rows && endCol >= 0 && endCol < cols) {
      return {
        start_row: startRow,
        start_col: startCol,
        end_row: endRow,
        end_col: endCol,
      };
    }
    length -= 1;
  }

  return null;
}

export function isSingleCellTrace(trace: Coordinates): boolean {
  return trace.start_row === trace.end_row && trace.start_col === trace.end_col;
}

export function cellsInTrace(trace: Coordinates): { row: number; col: number }[] {
  const dr = sign(trace.end_row - trace.start_row);
  const dc = sign(trace.end_col - trace.start_col);
  const cells: { row: number; col: number }[] = [];
  let row = trace.start_row;
  let col = trace.start_col;

  while (true) {
    cells.push({ row, col });
    if (row === trace.end_row && col === trace.end_col) {
      break;
    }
    row += dr;
    col += dc;
  }

  return cells;
}
