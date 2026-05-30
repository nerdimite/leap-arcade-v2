/** Assembled dumb wiki screen: switches on viewState.status and composes leaves. */

import { WikiActiveView } from "./WikiActiveView"
import { WikiFinalResults } from "./WikiFinalResults"
import { WikiPuzzleResultCard } from "./WikiPuzzleResultCard"
import type { WikiViewState } from "./wiki-view-state"

export type WikiViewProps = {
  viewState: WikiViewState
  onNavigate: (title: string) => Promise<void>
  onBack: () => Promise<void> | void
  onContinue: () => Promise<void> | void
}

export function WikiView(props: WikiViewProps) {
  const { viewState, onNavigate, onBack, onContinue } = props

  if (viewState.status === "none") {
    return null
  }

  if (viewState.status === "finalCompleted") {
    return (
      <WikiFinalResults
        totalScore={viewState.totalScore}
        results={viewState.results}
      />
    )
  }

  if (viewState.status === "finalAbandoned") {
    return (
      <WikiFinalResults
        totalScore={viewState.totalScore}
        results={viewState.results}
        title="Wikipedia Speed Run"
        subtitle="Session ended. Completed puzzles keep their scores; others count as zero."
      />
    )
  }

  if (viewState.status === "error") {
    return (
      <div className="mx-auto max-w-2xl p-6">
        <p className="rounded-[var(--radius)] border-2 border-cross bg-cross/12 px-3.5 py-3 text-[14px] text-ink">
          {viewState.message}
        </p>
      </div>
    )
  }

  if (viewState.status === "puzzleResult") {
    const r = viewState.result
    return (
      <WikiPuzzleResultCard
        targetTitle={r.target_title}
        steps={r.steps_taken}
        score={r.score}
        timeMs={r.time_ms}
        totalScore={viewState.totalScore}
        hasNext={viewState.hasNext}
        continuePending={viewState.continuePending}
        onContinue={() => void onContinue()}
      />
    )
  }

  if (viewState.status === "active") {
    return (
      <WikiActiveView
        current={viewState.current}
        pathRoot={viewState.pathRoot}
        timerRemainingMs={viewState.timerRemainingMs}
        completedCount={viewState.completedCount}
        totalScore={viewState.totalScore}
        navPending={viewState.navPending}
        onNavigate={onNavigate}
        onBack={() => void onBack()}
      />
    )
  }

  return null
}
