/** Active wiki puzzle layout: header stats + article pane. */

import { Button } from "@/components/ui/button";
import { formatMs } from "@/lib/utils";
import type { WikiActivePuzzle } from "@/services/wiki/schema";

import { WikiArticlePane } from "./WikiArticlePane";
import { WikiClickBreadcrumb } from "./WikiClickBreadcrumb";
import { WikiProgressBar } from "./WikiProgressBar";

export type WikiActiveViewProps = {
  current: WikiActivePuzzle;
  pathRoot: string;
  timerRemainingMs: number;
  completedCount: number;
  totalScore: number;
  navPending: boolean;
  onNavigate: (title: string) => Promise<void>;
  /** Caller wraps async work with `void` at the boundary. */
  onBack: () => void;
};

export function WikiActiveView(props: WikiActiveViewProps) {
  const {
    current,
    pathRoot,
    timerRemainingMs,
    completedCount,
    totalScore,
    navPending,
    onNavigate,
    onBack,
  } = props;
  const displayMs = timerRemainingMs;

  return (
    <div className="mx-auto flex min-h-svh w-full max-w-[min(100%,1680px)] flex-col gap-0 px-3 pb-8 pt-4 sm:px-5 lg:px-7">
      <header className="sticky top-0 z-30 space-y-2 border-b border-border/80 bg-background/95 pb-3 backdrop-blur supports-[backdrop-filter]:bg-background/88">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex min-w-0 flex-wrap items-center gap-2">
            {current.back_enabled ? (
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={navPending}
                onClick={onBack}
              >
                Back
              </Button>
            ) : null}
            <h1 className="text-lg font-semibold">Wikipedia Speed Run</h1>
          </div>
          <span className="text-sm font-medium text-muted-foreground">
            Puzzle {current.puzzle_index} of {current.puzzle_count}
          </span>
        </div>
        <WikiProgressBar
          puzzleCount={current.puzzle_count}
          puzzleIndex={current.puzzle_index}
          completedCount={completedCount}
        />
        <p className="text-sm font-medium leading-snug">{current.clue}</p>
        <WikiClickBreadcrumb pathRoot={pathRoot} clickPath={current.click_path} />
        <div className="flex flex-wrap gap-4 text-sm">
          <span className="rounded-md border px-2 py-1 font-mono tabular-nums">
            ⏱ {formatMs(displayMs)}
          </span>
          <span className="text-muted-foreground">
            Clicks: {current.steps_taken} · Completed rounds: {completedCount} · Score:{" "}
            {totalScore}
          </span>
        </div>
      </header>
      <WikiArticlePane
        currentTitle={current.current_title}
        articleHtml={current.article_html}
        navPending={navPending}
        onNavigate={onNavigate}
      />
    </div>
  );
}
