import { useMutation, useQueryClient } from "@tanstack/react-query"

import { postFind, postPlay, postSubmit } from "@/lib/api/word-hunt"

import { wordHuntQueryKeys } from "./keys"
import type {
  FindRequest,
  FindResponse,
  PlayResponse,
  SubmitResponse,
} from "./schema"

export function useWordHuntPlay() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (): Promise<PlayResponse> => postPlay(),
    onSuccess: (data) => {
      queryClient.setQueryData(wordHuntQueryKeys.play(), data)
    },
  })
}

export function useWordHuntFind() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (input: FindRequest): Promise<FindResponse> => postFind(input),
    onSuccess: (data) => {
      if (data.session_status === "completed" && data.result) {
        queryClient.setQueryData(wordHuntQueryKeys.play(), {
          session_status: data.session_status,
          session_score: data.session_score,
          puzzle: null,
          result: data.result,
        })
      }
    },
  })
}

export function useWordHuntSubmit() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (): Promise<SubmitResponse> => postSubmit(),
    onSuccess: (data) => {
      queryClient.setQueryData(wordHuntQueryKeys.play(), {
        session_status: "completed",
        session_score: data.result.score,
        puzzle: null,
        result: data.result,
      })
    },
  })
}
