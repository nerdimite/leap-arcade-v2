/** Assembled dumb Picture Illustration screen: clue image, answer form, timer, result. */

import { ArrowRight } from "lucide-react"
import Image from "next/image"
import type { CSSProperties, FormEvent } from "react"

import { GameHeader } from "@/components/game/GameHeader"
import { ScoreReadout } from "@/components/game/ScoreReadout"
import { cn } from "@/lib/utils"
import type { Puzzle, Result } from "@/services/picture/schema"

import { CorrectBurst, ScorePop } from "./CorrectFeedback"
import { ResultScreen } from "./ResultScreen"
import { SessionTimer } from "./SessionTimer"

/** A win to celebrate, set on a correct answer and cleared on a timer. */
export type Celebration = { token: number; scoreDelta: number; streak: number }

export type PictureViewState =
  | {
      status: "playing"
      puzzle: Puzzle
      currentScore: number
      answer: string
      wrongMessage: string | null
      inputShakeActive: boolean
      isPending: boolean
      timer: { startedAt: string; limitMs: number } | null
      celebration: Celebration | null
    }
  | { status: "result"; result: Result }
  | { status: "empty" }

export type PictureViewProps = {
  viewState: PictureViewState
  onAnswerChange: (value: string) => void
  onSubmit: (e: FormEvent) => void
  onSkip: () => void
  onInputAnimationEnd: (e: React.AnimationEvent<HTMLInputElement>) => void
  onSessionExpired: () => void | Promise<void>
  onBackToLobby: () => void
}

/** Picture Illustration runs on its violet marquee accent. */
const PIC_ACCENT = { "--accent": "var(--pic)" } as CSSProperties

export function PictureView(props: PictureViewProps) {
  const {
    viewState,
    onAnswerChange,
    onSubmit,
    onSkip,
    onInputAnimationEnd,
    onSessionExpired,
  } = props

  if (viewState.status === "result") {
    return (
      <div style={PIC_ACCENT}>
        <ResultScreen
          result={viewState.result}
          onBackToLobby={props.onBackToLobby}
        />
      </div>
    )
  }

  if (viewState.status === "empty") {
    return (
      <div className="p-6" style={PIC_ACCENT}>
        <p className="text-[15px] text-ink-dim">No puzzle available.</p>
      </div>
    )
  }

  const {
    puzzle,
    currentScore,
    answer,
    wrongMessage,
    inputShakeActive,
    isPending,
    timer,
    celebration,
  } = viewState
  const imgSrc = `/games/picture/${puzzle.image_filename}`

  return (
    <div
      className="mx-auto flex max-w-xl flex-col gap-4 p-6"
      style={PIC_ACCENT}
    >
      <GameHeader
        gameId="picture"
        progress={`${puzzle.puzzles_answered} of ${puzzle.puzzles_total} solved`}
      >
        {timer !== null ? (
          <SessionTimer
            sessionStartedAt={timer.startedAt}
            timeLimitMs={timer.limitMs}
            onExpired={onSessionExpired}
          />
        ) : null}
        <ScoreReadout
          score={currentScore}
          accessory={
            celebration ? (
              <ScorePop
                key={celebration.token}
                scoreDelta={celebration.scoreDelta}
              />
            ) : undefined
          }
        />
      </GameHeader>

      <div className="relative aspect-video w-full overflow-hidden rounded-[var(--radius)] border-2 border-line bg-bg-2 shadow-[var(--shadow-cabinet)]">
        <Image
          src={imgSrc}
          alt="Picture puzzle clue"
          fill
          className="object-contain"
          sizes="100vw"
          priority
        />
        {celebration ? (
          <CorrectBurst
            key={celebration.token}
            token={celebration.token}
            scoreDelta={celebration.scoreDelta}
            streak={celebration.streak}
          />
        ) : null}
      </div>

      <form className="flex flex-col gap-3" onSubmit={onSubmit}>
        <label
          className="text-[10px] font-bold tracking-[1px] text-ink-faint uppercase"
          htmlFor="picture-answer"
        >
          Your answer
        </label>
        <input
          id="picture-answer"
          className={cn(
            "h-11 rounded-[var(--radius)] border-2 border-line bg-bg-2 px-3.5 text-[15px] text-ink outline-none placeholder:text-ink-faint focus-visible:border-[var(--accent)] disabled:opacity-60",
            inputShakeActive && "animate-picture-input-shake"
          )}
          value={answer}
          placeholder="Type what the image shows"
          onChange={(e) => onAnswerChange(e.target.value)}
          onAnimationEnd={onInputAnimationEnd}
          autoComplete="off"
          disabled={isPending}
        />
        {wrongMessage ? (
          <p className="text-[14px] text-cross">{wrongMessage}</p>
        ) : null}
        <div className="flex flex-wrap items-center gap-2.5">
          <button
            type="submit"
            disabled={isPending || answer.trim().length === 0}
            className="inline-flex h-11 items-center justify-center rounded-[var(--radius)] border-2 border-[var(--accent)] bg-[var(--accent)] px-5 text-[12px] font-extrabold tracking-[1.5px] text-bg uppercase shadow-[var(--shadow-cabinet-sm)] transition-[transform,box-shadow] duration-150 ease-[var(--ease-arcade)] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none disabled:pointer-events-none disabled:opacity-50 motion-reduce:transition-none"
          >
            Submit
          </button>
          <button
            type="button"
            disabled={isPending}
            className="inline-flex h-11 items-center justify-center gap-1.5 rounded-[var(--radius)] border-2 border-line bg-transparent px-5 text-[12px] font-bold tracking-[1px] text-ink-dim uppercase hover:bg-panel-2 disabled:pointer-events-none disabled:opacity-50"
            onClick={onSkip}
          >
            Skip
            <ArrowRight aria-hidden className="size-3.5" />
          </button>
        </div>
      </form>
    </div>
  )
}
