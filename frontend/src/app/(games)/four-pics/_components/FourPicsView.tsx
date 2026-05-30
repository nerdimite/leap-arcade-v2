/** Assembled dumb Four Pics screen: image grid play surface, answer overlay, result. */

import Image from "next/image";
import type { CSSProperties } from "react";

import { GameHeader } from "@/components/game/GameHeader";
import { ScoreReadout } from "@/components/game/ScoreReadout";
import { cn } from "@/lib/utils";
import type { QuestionState, Result } from "@/services/four_pics/schema";

import { AnswerOverlay } from "./AnswerOverlay";
import { ResultView } from "./ResultView";
import { Stopwatch } from "./Stopwatch";

export type FourPicsOverlay = {
  correct: boolean;
  score: number;
  timeBonus: number;
  selectedIndex: number;
};

export type FourPicsViewState =
  | {
      status: "playing";
      question: QuestionState;
      sessionScore: number;
      overlay: FourPicsOverlay | null;
      submitError: string | null;
      inputDisabled: boolean;
    }
  | { status: "result"; result: Result }
  | { status: "empty" };

export type FourPicsViewProps = {
  viewState: FourPicsViewState;
  onSelect: (index: number) => void;
  onBackToLobby: () => void;
};

/** Four Pics runs on its lime marquee accent. */
const FOUR_ACCENT = { "--accent": "var(--four)" } as CSSProperties;

export function FourPicsView({ viewState, onSelect, onBackToLobby }: FourPicsViewProps) {
  if (viewState.status === "result") {
    return (
      <div style={FOUR_ACCENT}>
        <ResultView result={viewState.result} onBackToLobby={onBackToLobby} />
      </div>
    );
  }

  if (viewState.status === "empty") {
    return (
      <div className="p-6" style={FOUR_ACCENT}>
        <p className="text-[15px] text-ink-dim">No question available.</p>
      </div>
    );
  }

  const { question, sessionScore, overlay, submitError, inputDisabled } = viewState;

  return (
    <div className="mx-auto flex max-w-lg flex-col gap-5 p-6" style={FOUR_ACCENT}>
      <GameHeader
        gameId="four_pics"
        progress={`Round ${question.question_number} of ${question.total_questions}`}
      >
        <Stopwatch startedAt={question.started_at} />
        <ScoreReadout score={sessionScore} />
      </GameHeader>

      {submitError !== null ? (
        <p
          role="alert"
          className="rounded-[var(--radius)] border-2 border-cross bg-cross/12 px-3.5 py-3 text-[14px] text-ink"
        >
          {submitError}
        </p>
      ) : null}

      <div className="relative">
        <div className="grid grid-cols-2 gap-3">
          {question.image_paths.map((path, index) => (
            <button
              key={path}
              type="button"
              disabled={inputDisabled}
              className={cn(
                "relative aspect-square overflow-hidden rounded-[var(--radius)] border-2 border-line bg-bg-2 shadow-[var(--shadow-cabinet-sm)] transition-[transform] duration-150 ease-[var(--ease-arcade)] disabled:pointer-events-none disabled:opacity-60 hover:not-disabled:-translate-y-0.5 motion-reduce:transition-none motion-reduce:hover:translate-y-0",
                overlay?.correct && overlay.selectedIndex === index
                  ? "ring-2 ring-[var(--accent)] ring-offset-2 ring-offset-bg"
                  : null,
              )}
              onClick={() => onSelect(index)}
            >
              <Image
                src={path}
                alt={`Option ${index + 1}`}
                fill
                className="object-cover"
                sizes="(max-width: 512px) 50vw, 256px"
              />
            </button>
          ))}
        </div>
        {overlay !== null ? (
          <AnswerOverlay
            correct={overlay.correct}
            score={overlay.score}
            timeBonus={overlay.timeBonus}
            selectedIndex={overlay.selectedIndex}
          />
        ) : null}
      </div>
    </div>
  );
}
