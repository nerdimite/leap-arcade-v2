"use client";

import type { Clue } from "@/services/word_hunt/schema";

type Props = {
  clues: Clue[];
};

export function ClueListPanel({ clues }: Props) {
  return (
    <ul className="space-y-3">
      {clues.map((clue) => (
        <li key={clue.word_id} className="[perspective:1000px]">
          <div
            className={`relative min-h-20 transition-[transform,opacity] duration-500 [transform-style:preserve-3d] ${
              clue.found ? "[transform:rotateY(180deg)] opacity-60" : ""
            }`}
          >
            <div className="absolute inset-0 flex items-center rounded-[var(--radius)] border-2 border-line bg-panel p-4 [backface-visibility:hidden]">
              <p className="text-[14px] leading-snug text-ink-dim">{clue.clue}</p>
            </div>
            <div className="absolute inset-0 flex items-center gap-2 rounded-[var(--radius)] border-2 border-four/40 bg-four/12 p-4 line-through [backface-visibility:hidden] [transform:rotateY(180deg)]">
              <span className="font-semibold text-four">{clue.word}</span>
              <span aria-hidden="true" className="text-four">
                ✓
              </span>
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}
