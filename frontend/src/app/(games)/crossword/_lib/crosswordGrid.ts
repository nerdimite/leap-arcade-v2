import type {
  CellSkeleton,
  Clue,
  PuzzleState,
} from "@/services/crossword/schema"

export type CrosswordDirection = "across" | "down"

export type CellKey = string

export function cellKey(row: number, col: number): CellKey {
  return `${row},${col}`
}

export function parseCellKey(key: CellKey): { row: number; col: number } {
  const [row, col] = key.split(",").map(Number)
  return { row, col }
}

export function entryKey(clue: Clue): string {
  return `${clue.start_row},${clue.start_col},${clue.direction}`
}

export function collectEntryCellKeys(clue: Clue): CellKey[] {
  const keys: CellKey[] = []
  for (let i = 0; i < clue.length; i += 1) {
    if (clue.direction === "across") {
      keys.push(cellKey(clue.start_row, clue.start_col + i))
    } else {
      keys.push(cellKey(clue.start_row + i, clue.start_col))
    }
  }
  return keys
}

export type CellMembership = {
  acrossEntryId: string | null
  downEntryId: string | null
}

export type PuzzleContext = {
  rows: number
  cols: number
  openCells: Set<CellKey>
  lockedCells: Set<CellKey>
  cellLetters: Record<CellKey, string>
  membership: Record<CellKey, CellMembership>
  cluesById: Record<string, Clue>
  clues: Clue[]
}

export function buildPuzzleContext(puzzle: PuzzleState): PuzzleContext {
  const openCells = new Set<CellKey>()
  const lockedCells = new Set<CellKey>()
  const cellLetters: Record<CellKey, string> = {}
  const membership: Record<CellKey, CellMembership> = {}

  for (const row of puzzle.cells) {
    for (const cell of row) {
      if (cell === null) {
        continue
      }
      const key = cellKey(cell.row, cell.col)
      openCells.add(key)
      if (cell.letter) {
        lockedCells.add(key)
        cellLetters[key] = cell.letter.toUpperCase()
      }
      membership[key] = { acrossEntryId: null, downEntryId: null }
    }
  }

  const cluesById: Record<string, Clue> = {}
  for (const clue of puzzle.clues) {
    cluesById[clue.entry_id] = clue
    const keys = collectEntryCellKeys(clue)
    for (const key of keys) {
      const entry = membership[key] ?? {
        acrossEntryId: null,
        downEntryId: null,
      }
      if (clue.direction === "across") {
        entry.acrossEntryId = clue.entry_id
      } else {
        entry.downEntryId = clue.entry_id
      }
      membership[key] = entry
    }
    if (clue.solved && clue.cells && clue.answer) {
      for (let i = 0; i < clue.cells.length; i += 1) {
        const coord = clue.cells[i]
        const key = cellKey(coord.row, coord.col)
        lockedCells.add(key)
        cellLetters[key] = clue.answer[i]?.toUpperCase() ?? ""
      }
    }
  }

  return {
    rows: puzzle.rows,
    cols: puzzle.cols,
    openCells,
    lockedCells,
    cellLetters,
    membership,
    cluesById,
    clues: puzzle.clues,
  }
}

export function getActiveEntryId(
  context: PuzzleContext,
  cursor: { row: number; col: number } | null,
  direction: CrosswordDirection
): string | null {
  if (!cursor) {
    return null
  }
  const member = context.membership[cellKey(cursor.row, cursor.col)]
  if (!member) {
    return null
  }
  if (direction === "across") {
    return member.acrossEntryId
  }
  return member.downEntryId
}

export function getActiveEntryCellKeys(
  context: PuzzleContext,
  cursor: { row: number; col: number } | null,
  direction: CrosswordDirection
): CellKey[] {
  const entryId = getActiveEntryId(context, cursor, direction)
  if (!entryId) {
    return []
  }
  const clue = context.cluesById[entryId]
  return clue ? collectEntryCellKeys(clue) : []
}

export function resolveDirectionForCell(
  context: PuzzleContext,
  row: number,
  col: number,
  preferred: CrosswordDirection
): CrosswordDirection {
  const member = context.membership[cellKey(row, col)]
  if (!member) {
    return preferred
  }
  const hasAcross = member.acrossEntryId !== null
  const hasDown = member.downEntryId !== null
  if (hasAcross && hasDown) {
    return preferred
  }
  if (hasAcross) {
    return "across"
  }
  if (hasDown) {
    return "down"
  }
  return preferred
}

export function isSharedCell(
  context: PuzzleContext,
  row: number,
  col: number
): boolean {
  const member = context.membership[cellKey(row, col)]
  if (!member) {
    return false
  }
  return member.acrossEntryId !== null && member.downEntryId !== null
}

export function getCellLetter(
  context: PuzzleContext,
  draft: Record<CellKey, string>,
  key: CellKey
): string {
  if (context.lockedCells.has(key)) {
    return context.cellLetters[key] ?? ""
  }
  return draft[key] ?? ""
}

export function isEntryComplete(
  context: PuzzleContext,
  draft: Record<CellKey, string>,
  entryId: string
): boolean {
  const clue = context.cluesById[entryId]
  if (!clue || clue.solved) {
    return false
  }
  const keys = collectEntryCellKeys(clue)
  return keys.every((key) => getCellLetter(context, draft, key) !== "")
}

export function entryLetters(
  context: PuzzleContext,
  draft: Record<CellKey, string>,
  entryId: string
): string {
  const clue = context.cluesById[entryId]
  if (!clue) {
    return ""
  }
  return collectEntryCellKeys(clue)
    .map((key) => getCellLetter(context, draft, key))
    .join("")
}

export function firstOpenCellInEntry(
  context: PuzzleContext,
  entryId: string
): { row: number; col: number } | null {
  const clue = context.cluesById[entryId]
  if (!clue) {
    return null
  }
  for (const key of collectEntryCellKeys(clue)) {
    if (!context.lockedCells.has(key)) {
      return parseCellKey(key)
    }
  }
  return null
}

export function findOpenCellInDirection(
  context: PuzzleContext,
  from: { row: number; col: number },
  deltaRow: number,
  deltaCol: number
): { row: number; col: number } | null {
  let row = from.row + deltaRow
  let col = from.col + deltaCol
  while (row >= 0 && row < context.rows && col >= 0 && col < context.cols) {
    const key = cellKey(row, col)
    if (context.openCells.has(key)) {
      return { row, col }
    }
    row += deltaRow
    col += deltaCol
  }
  return null
}

export function nextCellInEntry(
  context: PuzzleContext,
  clue: Clue,
  from: { row: number; col: number },
  forward: boolean
): { row: number; col: number } | null {
  const keys = collectEntryCellKeys(clue)
  const fromKey = cellKey(from.row, from.col)
  const index = keys.indexOf(fromKey)
  if (index === -1) {
    return null
  }
  const step = forward ? 1 : -1
  for (let i = index + step; i >= 0 && i < keys.length; i += step) {
    const key = keys[i]
    if (context.openCells.has(key)) {
      return parseCellKey(key)
    }
  }
  return null
}

export function cellSkeletonAt(
  puzzle: PuzzleState,
  row: number,
  col: number
): CellSkeleton | null {
  return puzzle.cells[row]?.[col] ?? null
}
