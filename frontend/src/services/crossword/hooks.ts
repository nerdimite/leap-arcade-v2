import { useMutation } from "@tanstack/react-query"

import { postCheck, postPlay, postSubmit } from "@/lib/api/crossword"

import { crosswordQueryKeys } from "./keys"
import type {
  CheckRequest,
  CheckResponse,
  PlayResponse,
  SubmitResponse,
} from "./schema"

export function useCrosswordPlay() {
  return useMutation<PlayResponse>({
    mutationKey: crosswordQueryKeys.play(),
    mutationFn: () => postPlay(),
  })
}

export function useCrosswordCheck() {
  return useMutation<CheckResponse, Error, CheckRequest>({
    mutationFn: (input) => postCheck(input),
  })
}

export function useCrosswordSubmit() {
  return useMutation<SubmitResponse>({
    mutationFn: () => postSubmit(),
  })
}
