"use client"

import { Check } from "lucide-react"

import type { Clue } from "@/services/word_hunt/schema"

type Props = {
  clues: Clue[]
}

export function ClueListPanel({ clues }: Props) {
  return (
    <ul className="grid grid-cols-1 gap-2.5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {clues.map((clue) => (
        <ClueRow key={clue.word_id} clue={clue} />
      ))}
    </ul>
  )
}

function ClueRow({ clue }: { clue: Clue }) {
  const { found, word } = clue

  return (
    <li
      className={`flex items-start gap-3 rounded-[var(--radius)] border-2 p-3.5 transition-colors duration-300 ease-[var(--ease-arcade)] ${
        found ? "border-four/45 bg-four/10" : "border-line bg-panel"
      }`}
    >
      <div className="min-w-0 flex-1">
        <p
          className={`text-[14px] leading-snug ${found ? "text-ink-faint" : "text-ink-dim"}`}
        >
          {clue.clue}
        </p>
        {found && word ? (
          <p className="mt-1.5 animate-clue-reveal text-[13px] font-bold tracking-[0.5px] text-four uppercase motion-reduce:animate-none">
            <span className="sr-only">Solved: </span>
            {word}
          </p>
        ) : null}
      </div>
      {found ? (
        <Check
          aria-hidden
          strokeWidth={3.5}
          className="mt-px size-5 shrink-0 animate-clue-check text-four motion-reduce:animate-none"
        />
      ) : null}
    </li>
  )
}
