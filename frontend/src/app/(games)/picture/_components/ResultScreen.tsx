"use client";

import Image from "next/image";

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
      return {
        label: "Correct",
        className: "border-emerald-600/25 bg-emerald-600/10 text-emerald-900 dark:text-emerald-100",
      };
    case "skipped":
      return {
        label: "Skipped",
        className: "border-amber-600/25 bg-amber-600/10 text-amber-950 dark:text-amber-100",
      };
    case "wrong":
      return {
        label: "Wrong",
        className: "border-destructive/30 bg-destructive/10 text-destructive",
      };
    case "not_reached":
      return {
        label: "Not reached",
        className: "border-muted-foreground/25 bg-muted text-muted-foreground",
      };
  }
}

export function ResultScreen({ result, onBackToLobby }: ResultScreenProps) {
  const clockLine = formatPictureResultClockLine(
    result.time_remaining_seconds,
    result.time_bonus,
  );

  return (
    <div className="mx-auto flex max-w-lg flex-col gap-8 p-6 pb-10">
      <header className="space-y-1">
        <h1 className="text-xl font-semibold tracking-tight">Picture Illustration</h1>
        <p className="text-muted-foreground text-sm">You&apos;re done — here&apos;s how you scored.</p>
      </header>

      <section className="rounded-2xl border bg-card p-6 shadow-sm">
        <p className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
          Total score
        </p>
        <p className="mt-1 text-5xl font-bold tracking-tight tabular-nums text-primary">
          {result.score}
        </p>
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border bg-background/60 p-4">
            <p className="text-muted-foreground text-xs font-medium uppercase">Accuracy</p>
            <p className="mt-1 text-2xl font-semibold tabular-nums">{result.accuracy_score}</p>
            <p className="text-muted-foreground mt-1 text-xs">Points from correct guesses</p>
          </div>
          <div className="rounded-xl border bg-background/60 p-4">
            <p className="text-muted-foreground text-xs font-medium uppercase">Time bonus</p>
            <p className="mt-1 text-2xl font-semibold tabular-nums">{result.time_bonus}</p>
            <p className="text-muted-foreground mt-1 text-xs">Extra points for speed</p>
          </div>
        </div>
        <p className="text-muted-foreground mt-6 border-t pt-4 text-sm leading-relaxed">
          {clockLine}
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold tracking-tight">Puzzle breakdown</h2>
        <ul className="flex flex-col gap-2">
          {result.puzzles.map((puzzle) => {
            const meta = statusMeta(puzzle.status);
            const thumb = `/games/picture/${puzzle.image_filename}`;
            return (
              <li
                key={puzzle.puzzle_id}
                className="flex items-center gap-3 rounded-xl border bg-card p-3 shadow-sm"
              >
                <div className="relative size-14 shrink-0 overflow-hidden rounded-lg border bg-muted">
                  <Image
                    src={thumb}
                    alt=""
                    fill
                    className="object-cover"
                    sizes="56px"
                  />
                </div>
                <div className="min-w-0 flex-1">
                  <span
                    className={cn(
                      "inline-flex rounded-full border px-2.5 py-0.5 text-xs font-medium",
                      meta.className,
                    )}
                  >
                    {meta.label}
                  </span>
                  {puzzle.score_earned > 0 ? (
                    <p className="text-muted-foreground mt-1 text-xs tabular-nums">
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
        Back to Lobby
      </Button>
    </div>
  );
}
