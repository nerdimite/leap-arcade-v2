"use client";

import { useCallback, useEffect, useRef } from "react";

import { useNavigationGuard } from "@/hooks/use-navigation-guard";
import { PINPOINT_RESULT_FLASH_MS } from "@/lib/constants";
import { usePinpointAbandon, usePinpointGuess, usePinpointPlay } from "@/services/pinpoint/hooks";
import type { PlayResponse } from "@/services/pinpoint/schema";

import { usePinpointReducer } from "../_hooks/usePinpointReducer";
import { PinpointView } from "./PinpointView";
import { toPinpointViewState } from "./pinpoint-view-state";

type Props = {
  initialPlay: PlayResponse;
};

const SHAKE_DURATION_MS = 450;

export function PinpointClient({ initialPlay }: Props) {
  const { mutateAsync: playNext, isPending: isPlayPending } = usePinpointPlay();
  const { mutateAsync: submitGuess, isPending: isGuessPending } = usePinpointGuess();
  const { mutateAsync: abandonSession } = usePinpointAbandon();
  const { setIsDirty, registerBeforeNavigateConfirm } = useNavigationGuard();
  const [state, dispatch] = usePinpointReducer(initialPlay);

  const flashTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const shakeTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const advanceStartedRef = useRef(false);
  const resultDirtyClearedRef = useRef(false);

  const isMutationPending = isPlayPending || isGuessPending;
  const viewState = toPinpointViewState(state, isMutationPending);
  const sessionInProgress = state.phase !== "result";

  useEffect(() => {
    setIsDirty(sessionInProgress);
  }, [sessionInProgress, setIsDirty]);

  useEffect(() => {
    if (!sessionInProgress) {
      return undefined;
    }
    return registerBeforeNavigateConfirm(async () => {
      const res = await abandonSession();
      dispatch({ type: "ABANDON_SUCCESS", payload: res });
    });
  }, [abandonSession, dispatch, registerBeforeNavigateConfirm, sessionInProgress]);

  useEffect(() => {
    if (state.phase !== "result") {
      resultDirtyClearedRef.current = false;
      return;
    }
    if (resultDirtyClearedRef.current) {
      return;
    }
    resultDirtyClearedRef.current = true;
    setIsDirty(false);
  }, [setIsDirty, state.phase]);

  useEffect(() => {
    return () => {
      if (flashTimeoutRef.current !== null) {
        clearTimeout(flashTimeoutRef.current);
      }
      if (shakeTimeoutRef.current !== null) {
        clearTimeout(shakeTimeoutRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (state.shakeBadgeIndex === null) {
      return undefined;
    }

    if (shakeTimeoutRef.current !== null) {
      clearTimeout(shakeTimeoutRef.current);
    }

    shakeTimeoutRef.current = setTimeout(() => {
      shakeTimeoutRef.current = null;
      dispatch({ type: "CLEAR_SHAKE" });
    }, SHAKE_DURATION_MS);

    return () => {
      if (shakeTimeoutRef.current !== null) {
        clearTimeout(shakeTimeoutRef.current);
      }
    };
  }, [state.shakeBadgeIndex, dispatch]);

  useEffect(() => {
    if (state.phase !== "flashing") {
      return undefined;
    }

    if (flashTimeoutRef.current !== null) {
      clearTimeout(flashTimeoutRef.current);
    }

    flashTimeoutRef.current = setTimeout(() => {
      flashTimeoutRef.current = null;
      dispatch({ type: "FLASH_COMPLETE" });
    }, PINPOINT_RESULT_FLASH_MS);

    return () => {
      if (flashTimeoutRef.current !== null) {
        clearTimeout(flashTimeoutRef.current);
      }
    };
  }, [state.phase, dispatch]);

  useEffect(() => {
    if (state.phase !== "advancing") {
      advanceStartedRef.current = false;
      return;
    }

    if (advanceStartedRef.current) {
      return;
    }

    advanceStartedRef.current = true;

    void (async () => {
      try {
        const next = await playNext();
        dispatch({ type: "ADVANCE_SUCCESS", payload: next });
      } catch {
        dispatch({
          type: "ADVANCE_ERROR",
          payload: { message: "Could not load next puzzle. Try again." },
        });
      }
    })();
  }, [state.phase, playNext, dispatch]);

  const handleGuessChange = useCallback(
    (guess: string) => {
      dispatch({ type: "SET_GUESS", payload: { guess } });
    },
    [dispatch],
  );

  const handleSubmitGuess = useCallback(async () => {
    if (
      state.phase !== "playing" ||
      state.puzzle === null ||
      state.puzzle.status !== "active" ||
      state.guess.trim() === "" ||
      isMutationPending
    ) {
      return;
    }

    try {
      const res = await submitGuess({
        puzzle_id: state.puzzle.puzzle_id,
        guess: state.guess.trim(),
      });
      dispatch({ type: "GUESS_SUCCESS", payload: res });
    } catch {
      dispatch({
        type: "GUESS_ERROR",
        payload: { message: "Could not submit guess. Try again." },
      });
    }
  }, [dispatch, isMutationPending, state.guess, state.phase, state.puzzle, submitGuess]);

  return (
    <PinpointView
      viewState={viewState}
      onGuessChange={handleGuessChange}
      onSubmitGuess={() => {
        void handleSubmitGuess();
      }}
    />
  );
}
