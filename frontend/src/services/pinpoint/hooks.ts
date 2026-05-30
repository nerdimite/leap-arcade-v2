"use client"

import { useMutation } from "@tanstack/react-query"

import {
  postPinpointAbandon,
  postPinpointGuess,
  postPinpointPlay,
} from "@/lib/api/pinpoint"
import type { GuessRequest } from "@/services/pinpoint/schema"

export function usePinpointPlay() {
  return useMutation({
    mutationFn: () => postPinpointPlay(),
  })
}

export function usePinpointGuess() {
  return useMutation({
    mutationFn: (input: GuessRequest) => postPinpointGuess(input),
  })
}

export function usePinpointAbandon() {
  return useMutation({
    mutationFn: () => postPinpointAbandon(),
  })
}
