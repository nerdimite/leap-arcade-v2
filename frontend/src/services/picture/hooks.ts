"use client";

import { useMutation } from "@tanstack/react-query";

import { postPictureAnswer } from "@/lib/api/picture";
import type { AnswerRequest } from "./schema";

export type PostPictureAnswerBody = AnswerRequest;

export function useSubmitPictureAnswer() {
  return useMutation({
    mutationFn: (input: PostPictureAnswerBody) => postPictureAnswer(input),
  });
}