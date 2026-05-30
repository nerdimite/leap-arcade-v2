"use client";

import type { Clue } from "@/services/crossword/schema";

type Props = {
  clues: Clue[];
  activeEntryId: string | null;
  onClueClick: (entryId: string) => void;
};

function entryKey(clue: Clue): string {
  return `${clue.start_row},${clue.start_col},${clue.direction}`;
}

export function ClueListPanel({ clues, activeEntryId, onClueClick }: Props) {
  const across = clues.filter((clue) => clue.direction === "across");
  const down = clues.filter((clue) => clue.direction === "down");

  const renderClue = (clue: Clue) => {
    const isActive = clue.entry_id === activeEntryId;
    const isSolved = clue.solved;

    return (
      <li key={entryKey(clue)}>
        <button
          type="button"
          onClick={() => onClueClick(clue.entry_id)}
          className={`w-full rounded-md px-2 py-1 text-left transition-colors ${
            isSolved
              ? "text-green-700 opacity-60 line-through"
              : isActive
                ? "bg-amber-100 font-medium text-amber-950"
                : "hover:bg-neutral-100"
          }`}
        >
          <span className="font-semibold">{clue.number}.</span> {clue.clue}
          {isSolved ? " ✓" : null}
        </button>
      </li>
    );
  };

  return (
    <div className="space-y-4 text-sm">
      <section>
        <h2 className="mb-2 font-semibold">Across</h2>
        <ul className="space-y-1">{across.map(renderClue)}</ul>
      </section>
      <section>
        <h2 className="mb-2 font-semibold">Down</h2>
        <ul className="space-y-1">{down.map(renderClue)}</ul>
      </section>
    </div>
  );
}
