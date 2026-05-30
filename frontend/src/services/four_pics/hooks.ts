"use client"

import { useMutation } from "@tanstack/react-query"

import { postAbandon, postAnswer } from "@/lib/api/four-pics"
import type { AnswerRequest } from "@/services/four_pics/schema"

export function useSubmitFourPicsAnswer() {
  return useMutation({
    mutationFn: (input: AnswerRequest) => postAnswer(input),
  })
}

export function useAbandonFourPics() {
  return useMutation({
    mutationFn: () => postAbandon(),
  })
}
