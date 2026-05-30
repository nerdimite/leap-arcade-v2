import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import type { CSSProperties } from "react"

import { GameHeader } from "@/components/game/GameHeader"
import { ScoreReadout } from "@/components/game/ScoreReadout"

import { ClueBadgeRow } from "./ClueBadgeRow"
import { PinpointResultOverlay } from "./PinpointResultOverlay"
import type { PinpointViewState } from "./pinpoint-view-state"
import { Stopwatch } from "./Stopwatch"

/** Pinpoint runs on its magenta marquee accent. */
const PIN_ACCENT = { "--accent": "var(--pin)" } as CSSProperties

function formatResultScoreBreakdown(row: {
  status: "solved" | "failed" | "not_reached"
  score: number
  time_bonus: number
}): string {
  if (row.status === "failed" || row.status === "not_reached") {
    return "0"
  }
  const base = row.score - row.time_bonus
  return `${base} + ${row.time_bonus} = ${row.score}`
}

const RESULT_TONE: Record<"solved" | "failed" | "not_reached", string> = {
  solved: "text-four",
  failed: "text-cross",
  not_reached: "text-ink-faint",
}

export type PinpointViewProps = {
  viewState: PinpointViewState
  onGuessChange: (guess: string) => void
  onSubmitGuess: () => void
}

export function PinpointView(props: PinpointViewProps) {
  const { viewState, onGuessChange, onSubmitGuess } = props

  if (viewState.status === "result") {
    return (
      <main
        className="mx-auto flex max-w-lg flex-col gap-6 p-6"
        style={PIN_ACCENT}
      >
        <div className="overflow-hidden rounded-[var(--radius)] border-2 border-line bg-panel shadow-[var(--shadow-cabinet)]">
          <div
            className="h-2 bg-[var(--accent)]"
            style={{ boxShadow: "0 0 18px var(--accent)" }}
          />
          <div className="p-6">
            <p className="font-pixel text-[9px] tracking-[2px] text-[var(--accent)] uppercase">
              ▸ Pinpoint complete
            </p>
            <p className="mt-4 font-pixel text-[26px] leading-none text-four tabular-nums">
              {viewState.result.score}
            </p>
            <p className="mt-2 text-[11px] font-bold tracking-[1px] text-ink-faint uppercase">
              Total score
            </p>

            <ul className="mt-6 flex flex-col gap-px overflow-hidden rounded-[var(--radius)] border-2 border-line">
              {viewState.result.puzzles.map((row) => (
                <li
                  key={row.puzzle_id}
                  className="flex items-center justify-between gap-3 bg-bg-2 px-4 py-3 text-[14px]"
                >
                  <span className="text-ink-dim capitalize">
                    {row.status.replace("_", " ")}
                    {row.clues_used !== null
                      ? ` · ${row.clues_used} clues`
                      : ""}
                  </span>
                  <span
                    className={`font-pixel text-[11px] tabular-nums ${RESULT_TONE[row.status]}`}
                  >
                    {formatResultScoreBreakdown(row)}
                  </span>
                </li>
              ))}
            </ul>

            <Link
              href="/lobby"
              className="mt-6 inline-flex h-11 w-full items-center justify-center gap-1.5 rounded-[var(--radius)] border-2 border-[var(--accent)] bg-[var(--accent)] text-[12px] font-extrabold tracking-[1.5px] text-bg uppercase shadow-[var(--shadow-cabinet-sm)]"
            >
              <ArrowLeft aria-hidden className="size-4" />
              Back to Lobby
            </Link>
          </div>
        </div>
      </main>
    )
  }

  if (viewState.status === "loading") {
    return (
      <main
        className="mx-auto flex max-w-lg flex-col gap-4 p-6"
        style={PIN_ACCENT}
      >
        <p className="text-[15px] text-ink-dim">Loading next puzzle…</p>
      </main>
    )
  }

  const {
    puzzle,
    sessionScore,
    guess,
    inputDisabled,
    overlay,
    shakeBadgeIndex,
    errorMessage,
  } = viewState

  return (
    <main
      className="mx-auto flex max-w-lg flex-col gap-6 p-6"
      style={PIN_ACCENT}
    >
      <GameHeader
        gameId="pinpoint"
        progress={`Puzzle ${puzzle.puzzle_number} of ${puzzle.total_puzzles}`}
      >
        <ScoreReadout score={sessionScore} />
      </GameHeader>

      <div className="relative flex flex-col gap-6">
        <section aria-label="Revealed clues">
          <div className="mb-2.5 flex items-end justify-between gap-3">
            <h2 className="text-[10px] font-bold tracking-[1px] text-ink-faint uppercase">
              Clues
            </h2>
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
            event.preventDefault()
            onSubmitGuess()
          }}
        >
          <label className="flex flex-col gap-2 text-[10px] font-bold tracking-[1px] text-ink-faint uppercase">
            Your guess
            <input
              type="text"
              value={guess}
              onChange={(event) => onGuessChange(event.target.value)}
              disabled={inputDisabled}
              placeholder="Type the hidden category"
              className="h-11 rounded-[var(--radius)] border-2 border-line bg-bg-2 px-3.5 text-[15px] font-normal tracking-normal text-ink normal-case outline-none placeholder:text-ink-faint focus-visible:border-[var(--accent)] disabled:opacity-60"
              autoComplete="off"
            />
          </label>
          <button
            type="submit"
            disabled={inputDisabled || guess.trim() === ""}
            className="inline-flex h-11 items-center justify-center rounded-[var(--radius)] border-2 border-[var(--accent)] bg-[var(--accent)] text-[12px] font-extrabold tracking-[1.5px] text-bg uppercase shadow-[var(--shadow-cabinet-sm)] transition-[transform,box-shadow] duration-150 ease-[var(--ease-arcade)] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none disabled:pointer-events-none disabled:opacity-50 motion-reduce:transition-none"
          >
            Guess
          </button>
        </form>

        {overlay ? (
          <PinpointResultOverlay
            kind={overlay.kind}
            baseScore={overlay.baseScore}
            timeBonus={overlay.timeBonus}
            cluesUsed={overlay.cluesUsed}
          />
        ) : null}
      </div>

      {errorMessage ? (
        <p className="text-[14px] text-cross">{errorMessage}</p>
      ) : null}
    </main>
  )
}
