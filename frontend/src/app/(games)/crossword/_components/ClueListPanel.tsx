"use client"

import { Check } from "lucide-react"

import type { Clue } from "@/services/crossword/schema"

type Props = {
  clues: Clue[]
  activeEntryId: string | null
  onClueClick: (entryId: string) => void
}

function entryKey(clue: Clue): string {
  return `${clue.start_row},${clue.start_col},${clue.direction}`
}

export function ClueListPanel({ clues, activeEntryId, onClueClick }: Props) {
  const across = clues.filter((clue) => clue.direction === "across")
  const down = clues.filter((clue) => clue.direction === "down")

  const renderClue = (clue: Clue) => {
    const isActive = clue.entry_id === activeEntryId
    const isSolved = clue.solved

    return (
      <li key={entryKey(clue)}>
        <button
          type="button"
          onClick={() => onClueClick(clue.entry_id)}
          className={`w-full rounded-[var(--radius)] px-2.5 py-1.5 text-left text-[14px] transition-colors ${
            isSolved
              ? "text-four line-through opacity-70"
              : isActive
                ? "bg-rapid/15 font-medium text-ink"
                : "text-ink-dim hover:bg-panel-2"
          }`}
        >
          <span className="font-semibold text-ink">{clue.number}.</span>{" "}
          {clue.clue}
          {isSolved ? (
            <Check
              aria-hidden
              className="ml-1 inline size-3.5 animate-clue-check text-four motion-reduce:animate-none"
            />
          ) : null}
        </button>
      </li>
    )
  }

  return (
    <div className="space-y-5">
      <section>
        <h2 className="mb-2 text-[10px] font-bold tracking-[1px] text-ink-faint uppercase">
          Across
        </h2>
        <ul className="space-y-1">{across.map(renderClue)}</ul>
      </section>
      <section>
        <h2 className="mb-2 text-[10px] font-bold tracking-[1px] text-ink-faint uppercase">
          Down
        </h2>
        <ul className="space-y-1">{down.map(renderClue)}</ul>
      </section>
    </div>
  )
}
