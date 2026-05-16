"use client";

import { useMutation } from "@tanstack/react-query";

import {
  type PostAnswerBody,
  postAbandon,
  postAnswer,
  postPlay,
} from "@/lib/api/rapid_fire";
import { rapidFireQueryKeys } from "./keys";

export { rapidFireQueryKeys };

export function usePlay() {
  return useMutation({
    mutationFn: () => postPlay(),
  });
}

export function useSubmitAnswer() {
  return useMutation({
    mutationFn: (input: PostAnswerBody) => postAnswer(input),
  });
}

export function useAbandon() {
  return useMutation({
    mutationFn: () => postAbandon(),
  });
}
