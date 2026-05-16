"use client";

import { useMutation } from "@tanstack/react-query";

import { postLogin } from "@/lib/api/auth";

export function useLoginMutation() {
  return useMutation({
    mutationFn: postLogin,
  });
}
