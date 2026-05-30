import type { Clue, Coordinates } from "@/services/word_hunt/schema"

export const sampleGrid: string[][] = [
  ["D", "E", "V", "O", "P", "S"],
  ["Q", "M", "T", "B", "Y", "F"],
  ["S", "P", "R", "I", "N", "G"],
  ["Z", "X", "C", "V", "B", "N"],
  ["A", "N", "G", "U", "L", "R"],
  ["F", "G", "H", "J", "K", "L"],
]

export const devopsTrace: Coordinates = {
  start_row: 0,
  start_col: 0,
  end_row: 0,
  end_col: 5,
}

export const springTrace: Coordinates = {
  start_row: 2,
  start_col: 0,
  end_row: 2,
  end_col: 5,
}

export const allUnfoundClues: Clue[] = [
  {
    word_id: "w1",
    clue: "Culture where dev and ops stop pointing fingers.",
    found: false,
  },
  {
    word_id: "w2",
    clue: "Java framework that makes beans, not coffee.",
    found: false,
  },
  {
    word_id: "w3",
    clue: "Google's framework for building SPAs with TypeScript.",
    found: false,
  },
]

export const partialFoundClues: Clue[] = [
  {
    word_id: "w1",
    clue: "Culture where dev and ops stop pointing fingers.",
    found: true,
    word: "DEVOPS",
    coordinates: devopsTrace,
  },
  {
    word_id: "w2",
    clue: "Java framework that makes beans, not coffee.",
    found: false,
  },
  {
    word_id: "w3",
    clue: "Google's framework for building SPAs with TypeScript.",
    found: true,
    word: "ANGULAR",
    coordinates: { start_row: 4, start_col: 0, end_row: 4, end_col: 5 },
  },
]

export const allFoundClues: Clue[] = partialFoundClues.map((clue) => ({
  ...clue,
  found: true,
  word: clue.word ?? "FOUND",
}))

export const midDragPreview: Coordinates = {
  start_row: 2,
  start_col: 0,
  end_row: 2,
  end_col: 3,
}
