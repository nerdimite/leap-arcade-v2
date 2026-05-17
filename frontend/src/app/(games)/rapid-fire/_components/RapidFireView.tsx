/** Assembled dumb Rapid Fire screen: switches on `viewState.status` and composes leaves. */

import type { MutableRefObject } from "react";

import { TimerBar } from "@/components/game/TimerBar";

import { FeedbackOverlay } from "./FeedbackOverlay";
import { QuestionCard } from "./QuestionCard";
import { RapidFireErrorState } from "./RapidFireErrorState";
import { ResultCard } from "./ResultCard";
import type { RapidFireViewState } from "./rapid-fire-view-state";

export type RapidFireViewProps = {
  viewState: RapidFireViewState;
  onSelectOption: (optionIndex1: number, timeMs: number) => void;
  onBackToLobby: () => void;
  /** Must match the smart layer interval anchor for this question (answer timing). */
  questionEnteredAtRef: MutableRefObject<number>;
};

function progressLabelFor(viewState: RapidFireViewState): string | null {
  if (viewState.status === "question" || viewState.status === "feedback") {
    if (viewState.questionsTotal > 0) {
      return `Question ${viewState.questionsAnswered + 1} of ${viewState.questionsTotal}`;
    }
  }
  return null;
}

export function RapidFireView(props: RapidFireViewProps) {
  const { viewState, onSelectOption, onBackToLobby, questionEnteredAtRef } = props;

  if (viewState.status === "error") {
    return (
      <div className="mx-auto max-w-lg p-6">
        <RapidFireErrorState message={viewState.message} onBackToLobby={onBackToLobby} />
      </div>
    );
  }

  if (viewState.status === "result") {
    const r = viewState.result;
    return (
      <div className="mx-auto max-w-lg space-y-6 p-6">
        <ResultCard
          score={r.score}
          correctCount={r.correct_count}
          wrongCount={r.wrong_count}
          skippedCount={r.skipped_count}
          timeTakenSeconds={r.time_taken_seconds}
          onBackToLobby={onBackToLobby}
        />
      </div>
    );
  }

  const progressLabel = progressLabelFor(viewState);
  const currentScore =
    viewState.status === "loading" ||
    viewState.status === "question" ||
    viewState.status === "feedback"
      ? viewState.currentScore
      : 0;

  return (
    <div className="mx-auto max-w-lg space-y-4 p-6">
      <header className="flex flex-col gap-1">
        <h1 className="font-semibold text-lg">Rapid Fire</h1>
        {progressLabel ? (
          <p className="text-muted-foreground text-sm">{progressLabel}</p>
        ) : null}
        <p className="font-medium text-sm tabular-nums">Score: {currentScore}</p>
      </header>

      {viewState.status === "loading" ? (
        <p className="text-muted-foreground text-sm">No question loaded.</p>
      ) : viewState.status === "question" ? (
        <QuestionCard
          question={viewState.question}
          options={viewState.question.options}
          phase="question"
          selected={viewState.submittedOption}
          correctOption={viewState.lastCorrectOption}
          lastCorrect={viewState.lastCorrect}
          locked={viewState.locked}
          currentScore={viewState.currentScore}
          timerBar={!viewState.locked ? <TimerBar percentage={viewState.timerBarPct} /> : undefined}
          questionEnteredAtRef={questionEnteredAtRef}
          onSelectOption={onSelectOption}
        />
      ) : (
        <QuestionCard
          question={viewState.question}
          options={viewState.question.options}
          phase="feedback"
          selected={viewState.submittedOption}
          correctOption={viewState.lastCorrectOption}
          lastCorrect={viewState.lastCorrect}
          locked={false}
          currentScore={viewState.currentScore}
          feedbackOverlay={
            <FeedbackOverlay lastCorrect={viewState.lastCorrect} currentScore={viewState.currentScore} />
          }
          questionEnteredAtRef={questionEnteredAtRef}
          onSelectOption={onSelectOption}
        />
      )}
    </div>
  );
}
