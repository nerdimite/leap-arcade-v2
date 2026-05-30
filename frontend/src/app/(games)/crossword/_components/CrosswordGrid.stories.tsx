import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { fn } from "storybook/test";

import { CrosswordGrid } from "./CrosswordGrid";
import {
  activeHighlightCells,
  allSolvedPuzzle,
  draftInProgress,
  emptyPuzzle,
  inProgressPuzzle,
  lockedCellsFromPuzzle,
  missFlashCells,
} from "../_lib/storyFixtures";

const meta = {
  component: CrosswordGrid,
  args: {
    onCellClick: fn(),
  },
} satisfies Meta<typeof CrosswordGrid>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Empty: Story = {
  args: {
    puzzle: emptyPuzzle,
    displayLetter: () => "",
    lockedCells: lockedCellsFromPuzzle(emptyPuzzle),
    selectedCell: null,
    activeEntryCells: new Set(),
    missFlashCells: new Set(),
  },
};

export const InProgress: Story = {
  args: {
    puzzle: inProgressPuzzle,
    displayLetter: (row, col) => {
      const cell = inProgressPuzzle.cells[row]?.[col];
      return cell?.letter ?? draftInProgress[`${row},${col}`] ?? "";
    },
    lockedCells: lockedCellsFromPuzzle(inProgressPuzzle),
    selectedCell: { row: 1, col: 0 },
    activeEntryCells: new Set(["1,0", "2,0"]),
    missFlashCells: new Set(),
  },
};

export const AllSolved: Story = {
  args: {
    puzzle: allSolvedPuzzle,
    displayLetter: (row, col) => allSolvedPuzzle.cells[row]?.[col]?.letter ?? "",
    lockedCells: lockedCellsFromPuzzle(allSolvedPuzzle),
    selectedCell: { row: 0, col: 0 },
    activeEntryCells: activeHighlightCells,
    missFlashCells: new Set(),
  },
};

export const MidEntryHighlight: Story = {
  args: {
    puzzle: emptyPuzzle,
    displayLetter: (row, col) => {
      const letters: Record<string, string> = { "0,0": "C", "0,1": "A" };
      return letters[`${row},${col}`] ?? "";
    },
    lockedCells: lockedCellsFromPuzzle(emptyPuzzle),
    selectedCell: { row: 0, col: 1 },
    activeEntryCells: activeHighlightCells,
    missFlashCells: new Set(),
  },
};

export const WrongFlash: Story = {
  args: {
    puzzle: inProgressPuzzle,
    displayLetter: (row, col) => {
      const cell = inProgressPuzzle.cells[row]?.[col];
      return cell?.letter ?? draftInProgress[`${row},${col}`] ?? "";
    },
    lockedCells: lockedCellsFromPuzzle(inProgressPuzzle),
    selectedCell: { row: 2, col: 0 },
    activeEntryCells: new Set(["1,0", "2,0"]),
    missFlashCells,
  },
};

export { Empty as Default };
