/** Active question shell: timer slot, optional feedback overlay, prompt, and four options. */

import type { MutableRefObject, ReactNode } from "react";

import { Button } from "@/components/ui/button";
import type { Question } from "@/services/rapid_fire/schema";

function optionButtonClass(
  optionIndex1: number,
  ctx: {
    phase: "question" | "feedback";
    selected: number | null;
    correctOption: number | null;
    lastCorrect: boolean | null;
  },
): string {
  const base = "h-auto min-h-10 w-full justify-start whitespace-normal py-2 text-left";

  if (ctx.phase === "question") {
    return base;
  }

  const isCorrect = optionIndex1 === ctx.correctOption;
  const isWrongPick = ctx.selected != null && !ctx.lastCorrect && optionIndex1 === ctx.selected;

  if (isCorrect) {
    return `${base} border-green-600 bg-green-600/15 hover:bg-green-600/20`;
  }
  if (isWrongPick) {
    return `${base} border-red-600 bg-red-600/15 hover:bg-red-600/20`;
  }
  return `${base} opacity-60`;
}

export function QuestionCard(props: {
  question: Question;
  options: string[];
  phase: "question" | "feedback";
  selected: number | null;
  correctOption: number | null;
  lastCorrect: boolean | null;
  locked: boolean;
  currentScore: number;
  timerBar?: ReactNode;
  feedbackOverlay?: ReactNode;
  questionEnteredAtRef: MutableRefObject<number>;
  onSelectOption: (optionIndex1: number, timeMs: number) => void;
}) {
  void props.currentScore;
  const showFeedback = props.phase === "feedback";
  const disabled = props.locked || showFeedback;

  return (
    <div className="relative space-y-4 rounded-xl border border-border bg-card p-4 shadow-sm">
      {props.timerBar}
      {props.feedbackOverlay}
      <p className="pr-2 font-medium leading-snug">{props.question.question}</p>

      <div className="flex flex-col gap-2">
        {props.options.map((label, idx) => {
          const optionIndex1 = idx + 1;
          return (
            <Button
              key={optionIndex1}
              type="button"
              variant="outline"
              disabled={disabled}
              className={optionButtonClass(optionIndex1, {
                phase: props.phase,
                selected: props.selected,
                correctOption: props.correctOption,
                lastCorrect: props.lastCorrect,
              })}
              onClick={() => {
                const limit = props.question.time_limit_ms;
                const elapsed = Date.now() - props.questionEnteredAtRef.current;
                props.onSelectOption(
                  optionIndex1,
                  Math.min(limit, Math.max(0, elapsed)),
                );
              }}
            >
              <span className="mr-2 font-mono text-muted-foreground text-xs">{optionIndex1}.</span>
              {label}
            </Button>
          );
        })}
      </div>
    </div>
  );
}
