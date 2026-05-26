import type { PinpointState } from "../_hooks/usePinpointReducer";

export type PinpointOverlayView = {
  kind: "solved" | "failed";
  baseScore: number;
  timeBonus: number;
};

export type PinpointPlayingViewState = {
  status: "playing";
  sessionScore: number;
  puzzle: NonNullable<PinpointState["puzzle"]>;
  guess: string;
  inputDisabled: boolean;
  overlay: PinpointOverlayView | null;
  shakeBadgeIndex: number | null;
  errorMessage: string | null;
};

export type PinpointResultViewState = {
  status: "result";
  result: NonNullable<PinpointState["result"]>;
};

export type PinpointLoadingViewState = {
  status: "loading";
};

export type PinpointViewState =
  | PinpointPlayingViewState
  | PinpointResultViewState
  | PinpointLoadingViewState;

export function toPinpointViewState(
  state: PinpointState,
  inputLocked: boolean,
): PinpointViewState {
  if (state.phase === "result" && state.result) {
    return {
      status: "result",
      result: state.result,
    };
  }

  if (state.phase === "advancing" || state.puzzle === null) {
    return { status: "loading" };
  }

  const overlay =
    state.phase === "flashing" && state.flashKind !== null
      ? {
          kind: state.flashKind,
          baseScore: state.flashBaseScore ?? 0,
          timeBonus: state.flashTimeBonus ?? 0,
        }
      : null;

  return {
    status: "playing",
    sessionScore: state.sessionScore,
    puzzle: state.puzzle,
    guess: state.guess,
    inputDisabled: inputLocked || state.phase !== "playing",
    overlay,
    shakeBadgeIndex: state.shakeBadgeIndex,
    errorMessage: state.errorMessage,
  };
}
