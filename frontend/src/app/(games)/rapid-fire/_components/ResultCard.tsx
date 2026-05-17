/** End-of-run score summary for Rapid Fire. */

import { Button } from "@/components/ui/button";
import type { Result } from "@/services/rapid_fire/schema";

export function ResultCard(props: {
  score: Result["score"];
  correctCount: Result["correct_count"];
  wrongCount: Result["wrong_count"];
  skippedCount: Result["skipped_count"];
  timeTakenSeconds: Result["time_taken_seconds"];
  onBackToLobby: () => void;
}) {
  return (
    <>
      <h1 className="font-semibold text-lg">Rapid Fire — Results</h1>
      <div className="space-y-2 rounded-xl border border-border bg-card p-4 shadow-sm">
        <p className="font-medium text-2xl tabular-nums">{props.score} points</p>
        <ul className="space-y-1 text-muted-foreground text-sm">
          <li>Correct: {props.correctCount}</li>
          <li>Wrong: {props.wrongCount}</li>
          <li>Skipped: {props.skippedCount}</li>
          <li>Time: {props.timeTakenSeconds.toFixed(1)}s</li>
        </ul>
        <Button type="button" className="mt-4 w-full" onClick={props.onBackToLobby}>
          Back to Lobby
        </Button>
      </div>
    </>
  );
}
