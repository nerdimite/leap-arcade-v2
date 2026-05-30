"use client";

import Image from "next/image";
import { ArrowLeft } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { Result, ResultPuzzle } from "@/services/picture/schema";

import { formatPictureResultClockLine } from "../_lib/format-picture-result-clock";

export type ResultScreenProps = {
  result: Result;
  onBackToLobby: () => void;
};

function statusMeta(status: ResultPuzzle["status"]): { label: string; className: string } {
  switch (status) {
    case "correct":
      return { label: "Correct", className: "border-four/40 bg-four/12 text-four" };
    case "skipped":
      return { label: "Skipped", className: "border-rapid/40 bg-rapid/12 text-rapid" };
    case "wrong":
      return { label: "Wrong", className: "border-cross/40 bg-cross/12 text-cross" };
    case "not_reached":
      return { label: "Not reached", className: "border-line bg-bg-2 text-ink-faint" };
  }
}

export function ResultScreen({ result, onBackToLobby }: ResultScreenProps) {
  const clockLine = formatPictureResultClockLine(
    result.time_remaining_seconds,
    result.time_bonus,
  );

  return (
    <div className="mx-auto flex max-w-lg flex-col gap-6 p-6 pb-10">
      <div className="overflow-hidden rounded-[var(--radius)] border-2 border-line bg-panel shadow-[var(--shadow-cabinet)]">
        <div
          className="h-2 bg-[var(--accent,var(--pic))]"
          style={{ boxShadow: "0 0 18px var(--accent, var(--pic))" }}
        />
        <div className="p-6">
          <p className="font-pixel text-[9px] uppercase tracking-[2px] text-[var(--accent,var(--pic))]">
            ▸ You&apos;re done
          </p>
          <p className="mt-4 font-pixel text-[26px] leading-none tabular-nums text-four">
            {result.score}
          </p>
          <p className="mt-2 text-[11px] font-bold uppercase tracking-[1px] text-ink-faint">
            Total score
          </p>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            <div className="rounded-[var(--radius)] border-2 border-line bg-bg-2 p-4">
              <p className="text-[10px] font-bold uppercase tracking-[1px] text-ink-faint">Accuracy</p>
              <p className="mt-1.5 font-pixel text-[16px] tabular-nums text-ink">
                {result.accuracy_score}
              </p>
              <p className="mt-1.5 text-[12px] text-ink-dim">Points from correct guesses</p>
            </div>
            <div className="rounded-[var(--radius)] border-2 border-line bg-bg-2 p-4">
              <p className="text-[10px] font-bold uppercase tracking-[1px] text-ink-faint">
                Time bonus
              </p>
              <p className="mt-1.5 font-pixel text-[16px] tabular-nums text-ink">{result.time_bonus}</p>
              <p className="mt-1.5 text-[12px] text-ink-dim">Extra points for speed</p>
            </div>
          </div>
          <p className="mt-6 border-t-[1.5px] border-line pt-4 text-[14px] leading-relaxed text-ink-dim">
            {clockLine}
          </p>
        </div>
      </div>

      <section className="space-y-3">
        <h2 className="text-[10px] font-bold uppercase tracking-[1px] text-ink-faint">
          Puzzle breakdown
        </h2>
        <ul className="flex flex-col gap-2">
          {result.puzzles.map((puzzle) => {
            const meta = statusMeta(puzzle.status);
            const thumb = `/games/picture/${puzzle.image_filename}`;
            return (
              <li
                key={puzzle.puzzle_id}
                className="flex items-center gap-3 rounded-[var(--radius)] border-2 border-line bg-panel p-3"
              >
                <div className="relative size-14 shrink-0 overflow-hidden rounded-[var(--radius)] border-2 border-line bg-bg-2">
                  <Image src={thumb} alt="" fill className="object-cover" sizes="56px" />
                </div>
                <div className="min-w-0 flex-1">
                  <span
                    className={cn(
                      "inline-flex rounded-full border-2 px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-[0.5px]",
                      meta.className,
                    )}
                  >
                    {meta.label}
                  </span>
                  {puzzle.score_earned > 0 ? (
                    <p className="mt-1.5 text-[12px] tabular-nums text-ink-dim">
                      +{puzzle.score_earned} pts this puzzle
                    </p>
                  ) : null}
                </div>
              </li>
            );
          })}
        </ul>
      </section>

      <Button type="button" size="lg" className="w-full sm:w-auto" onClick={onBackToLobby}>
        <ArrowLeft aria-hidden className="size-4" />
        Back to Lobby
      </Button>
    </div>
  );
}
