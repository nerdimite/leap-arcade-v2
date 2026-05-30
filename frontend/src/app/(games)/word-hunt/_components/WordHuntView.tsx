/** Assembled dumb Word Hunt screen: letter grid play surface + clue panel, or result. */

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
      className="mx-auto flex max-w-5xl flex-col gap-6 p-6 lg:flex-row"
      style={WORD_ACCENT}
    >
      <div>
        <GameHeader
          gameId="word_hunt"
          progress={`Found ${puzzle.found_count} / ${puzzle.total_words}`}
          className="mb-4"
        >
          <ScoreReadout
            score={sessionScore}
            accessory={<ScoreIncrementChip visible={showScoreIncrement} />}
          />
        </GameHeader>
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
      <div className="flex-1">
        <h2 className="mb-3 text-[10px] font-bold tracking-[1px] text-ink-faint uppercase">
          Clues
        </h2>
        <ClueListPanel clues={puzzle.clues} />
        <button
          type="button"
          className="mt-6 inline-flex h-11 items-center justify-center rounded-[var(--radius)] border-2 border-[var(--accent)] bg-[var(--accent)] px-5 text-[12px] font-extrabold tracking-[1.5px] text-bg uppercase shadow-[var(--shadow-cabinet-sm)] transition-[transform,box-shadow] duration-150 ease-[var(--ease-arcade)] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none disabled:pointer-events-none disabled:opacity-50 motion-reduce:transition-none"
          disabled={disabled}
          onClick={onSubmit}
        >
          Submit
        </button>
      </div>
    </div>
  )
}
