/** Assembled dumb Word Hunt screen: header + letter grid + clue grid, or result. */

import type { CSSProperties } from "react"

import { GameHeader } from "@/components/game/GameHeader"
import { ScoreReadout } from "@/components/game/ScoreReadout"
import type {
  Coordinates,
  PuzzleState,
  Result,
} from "@/services/word_hunt/schema"

import { ClueListPanel } from "./ClueListPanel"
import { LetterGrid } from "./LetterGrid"
import { ResultView } from "./ResultView"
import { ScoreIncrementChip } from "./ScoreIncrementChip"
import { Stopwatch } from "./Stopwatch"

export type WordHuntViewState =
  | {
      status: "playing"
      puzzle: PuzzleState
      sessionScore: number
      highlights: Coordinates[]
      dragPreview: Coordinates | null
      missFlash: Coordinates | null
      landAnimation: Coordinates | null
      showScoreIncrement: boolean
      disabled: boolean
    }
  | { status: "result"; result: Result }

export type WordHuntViewProps = {
  viewState: WordHuntViewState
  onDragStart: (row: number, col: number) => void
  onDragMove: (row: number, col: number) => void
  onDragEnd: () => void
  onSubmit: () => void
  onBackToLobby: () => void
}

/** Word Hunt runs on its teal marquee accent. */
const WORD_ACCENT = { "--accent": "var(--word)" } as CSSProperties

export function WordHuntView(props: WordHuntViewProps) {
  const {
    viewState,
    onDragStart,
    onDragMove,
    onDragEnd,
    onSubmit,
    onBackToLobby,
  } = props

  if (viewState.status === "result") {
    return (
      <div style={WORD_ACCENT}>
        <ResultView result={viewState.result} onBackToLobby={onBackToLobby} />
      </div>
    )
  }

  const {
    puzzle,
    sessionScore,
    highlights,
    dragPreview,
    missFlash,
    landAnimation,
    showScoreIncrement,
    disabled,
  } = viewState

  return (
    <div
      className="mx-auto flex max-w-6xl flex-col gap-8 p-4 sm:p-6"
      style={WORD_ACCENT}
    >
      <GameHeader
        gameId="word_hunt"
        progress={`Found ${puzzle.found_count} / ${puzzle.total_words}`}
      >
        <Stopwatch startedAt={puzzle.started_at} />
        <ScoreReadout
          score={sessionScore}
          accessory={<ScoreIncrementChip visible={showScoreIncrement} />}
        />
        <button
          type="button"
          className="inline-flex h-11 items-center justify-center rounded-[var(--radius)] border-2 border-[var(--accent)] bg-[var(--accent)] px-5 text-[12px] font-extrabold tracking-[1.5px] text-bg uppercase shadow-[var(--shadow-cabinet-sm)] transition-[transform,box-shadow] duration-150 ease-[var(--ease-arcade)] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none disabled:pointer-events-none disabled:opacity-50 motion-reduce:transition-none"
          disabled={disabled}
          onClick={onSubmit}
        >
          Submit
        </button>
      </GameHeader>

      <div className="overflow-x-auto">
        <div className="flex justify-center">
          <div className="rounded-[var(--radius)] border-2 border-line bg-panel p-3 shadow-[var(--shadow-cabinet)] sm:p-4">
            <LetterGrid
              rows={puzzle.rows}
              cols={puzzle.cols}
              grid={puzzle.grid}
              highlighted={highlights}
              preview={dragPreview}
              missFlash={missFlash}
              landAnimation={landAnimation}
              onDragStart={onDragStart}
              onDragMove={onDragMove}
              onDragEnd={onDragEnd}
              disabled={disabled}
            />
          </div>
        </div>
      </div>

      <section aria-labelledby="word-hunt-clues-heading">
        <h2
          id="word-hunt-clues-heading"
          className="mb-3 text-[10px] font-bold tracking-[1px] text-ink-faint uppercase"
        >
          Clues
        </h2>
        <ClueListPanel clues={puzzle.clues} />
      </section>
    </div>
  )
}
