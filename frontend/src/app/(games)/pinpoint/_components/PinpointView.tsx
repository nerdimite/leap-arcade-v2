import Link from "next/link";

import { ClueBadgeRow } from "./ClueBadgeRow";
import { PinpointResultOverlay } from "./PinpointResultOverlay";
import { Stopwatch } from "./Stopwatch";
import type { PinpointViewState } from "./pinpoint-view-state";

function formatResultScoreBreakdown(row: {
  status: "solved" | "failed" | "not_reached";
  score: number;
  time_bonus: number;
}): string {
  if (row.status === "failed" || row.status === "not_reached") {
    return "0";
  }
  const base = row.score - row.time_bonus;
  return `${base} + ${row.time_bonus} = ${row.score}`;
}

export type PinpointViewProps = {
  viewState: PinpointViewState;
  onGuessChange: (guess: string) => void;
  onSubmitGuess: () => void;
};

export function PinpointView(props: PinpointViewProps) {
  const { viewState, onGuessChange, onSubmitGuess } = props;

  if (viewState.status === "result") {
    return (
      <main className="mx-auto flex max-w-lg flex-col gap-6 p-6">
        <h1 className="text-2xl font-semibold">Pinpoint complete</h1>
        <p className="text-lg">Total score: {viewState.result.score}</p>
        <ul className="space-y-2 text-sm">
          {viewState.result.puzzles.map((row) => (
            <li key={row.puzzle_id} className="flex justify-between border-b pb-2">
              <span>
                {row.status}
                {row.clues_used !== null ? ` · ${row.clues_used} clues` : ""}
              </span>
              <span className="font-mono tabular-nums">{formatResultScoreBreakdown(row)}</span>
            </li>
          ))}
        </ul>
        <Link href="/lobby" className="text-primary underline">
          Back to Lobby
        </Link>
      </main>
    );
  }

  if (viewState.status === "loading") {
    return (
      <main className="mx-auto flex max-w-lg flex-col gap-4 p-6">
        <p>Loading next puzzle…</p>
      </main>
    );
  }

  const { puzzle, sessionScore, guess, inputDisabled, overlay, shakeBadgeIndex, errorMessage } =
    viewState;

  return (
    <main className="mx-auto flex max-w-lg flex-col gap-6 p-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Pinpoint</h1>
        <p className="text-sm text-muted-foreground">Score: {sessionScore}</p>
      </header>

      <p className="text-sm text-muted-foreground">
        Puzzle {puzzle.puzzle_number} of {puzzle.total_puzzles}
      </p>

      <div className="relative flex flex-col gap-6">
        <section aria-label="Revealed clues">
          <div className="mb-2 flex items-end justify-between gap-3">
            <h2 className="text-sm font-medium">Clues</h2>
            <Stopwatch startedAt={puzzle.started_at} />
          </div>
          <ClueBadgeRow
            cluesRevealed={puzzle.clues_revealed}
            clues={puzzle.clues}
            shakeBadgeIndex={shakeBadgeIndex}
          />
        </section>

        <form
          className="flex flex-col gap-3"
          onSubmit={(event) => {
            event.preventDefault();
            onSubmitGuess();
          }}
        >
          <label className="flex flex-col gap-1 text-sm">
            Your guess
            <input
              type="text"
              value={guess}
              onChange={(event) => onGuessChange(event.target.value)}
              disabled={inputDisabled}
              className="rounded-md border px-3 py-2"
              autoComplete="off"
            />
          </label>
          <button
            type="submit"
            disabled={inputDisabled || guess.trim() === ""}
            className="rounded-md bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50"
          >
            Guess
          </button>
        </form>

        {overlay ? (
          <PinpointResultOverlay
            kind={overlay.kind}
            baseScore={overlay.baseScore}
            timeBonus={overlay.timeBonus}
          />
        ) : null}
      </div>

      {errorMessage ? <p className="text-sm text-destructive">{errorMessage}</p> : null}
    </main>
  );
}
