/** Assembled dumb Rapid Fire screen: feeds status-keyed slots to the shared GameShell. */

import type { MutableRefObject } from "react";

import { GameHeader } from "@/components/game/GameHeader";
import { GameShell } from "@/components/game/GameShell";
import { ScoreReadout } from "@/components/game/ScoreReadout";
import { TimerBar } from "@/components/game/TimerBar";

import { FeedbackBand } from "./FeedbackBand";
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

  /** loading / question / feedback share the stage: header + (notice | card). */
  const stage = (
    <div className="space-y-5">
      <GameHeader gameId="rapid_fire" progress={progressLabelFor(viewState)}>
        <ScoreReadout
          score={
            viewState.status === "loading" ||
            viewState.status === "question" ||
            viewState.status === "feedback"
              ? viewState.currentScore
              : 0
          }
        />
      </GameHeader>

      {viewState.status === "loading" ? (
        <p className="text-sm text-ink-faint">No question loaded.</p>
      ) : viewState.status === "question" ? (
        <QuestionCard
          question={viewState.question}
          options={viewState.question.options}
          phase="question"
          selected={viewState.submittedOption}
          correctOption={viewState.lastCorrectOption}
          lastCorrect={viewState.lastCorrect}
          locked={viewState.locked}
          timerBar={!viewState.locked ? <TimerBar percentage={viewState.timerBarPct} /> : undefined}
          questionEnteredAtRef={questionEnteredAtRef}
          onSelectOption={onSelectOption}
        />
      ) : viewState.status === "feedback" ? (
        <QuestionCard
          question={viewState.question}
          options={viewState.question.options}
          phase="feedback"
          selected={viewState.submittedOption}
          correctOption={viewState.lastCorrectOption}
          lastCorrect={viewState.lastCorrect}
          locked={false}
          feedbackOverlay={
            <FeedbackBand lastCorrect={viewState.lastCorrect} scoreDelta={viewState.scoreDelta} />
          }
          questionEnteredAtRef={questionEnteredAtRef}
          onSelectOption={onSelectOption}
        />
      ) : null}
    </div>
  );

  return (
    <GameShell
      gameId="rapid_fire"
      state={viewState.status}
      size="xl"
      bleedStates={["result", "error"]}
      slots={{
        loading: stage,
        question: stage,
        feedback: stage,
        result:
          viewState.status === "result" ? (
            <div className="mx-auto max-w-lg space-y-6 p-6">
              <ResultCard
                score={viewState.result.score}
                correctCount={viewState.result.correct_count}
                wrongCount={viewState.result.wrong_count}
                skippedCount={viewState.result.skipped_count}
                timeTakenSeconds={viewState.result.time_taken_seconds}
                onBackToLobby={onBackToLobby}
              />
            </div>
          ) : null,
        error:
          viewState.status === "error" ? (
            <div className="mx-auto max-w-lg p-6">
              <RapidFireErrorState message={viewState.message} onBackToLobby={onBackToLobby} />
            </div>
          ) : null,
      }}
    />
  );
}
