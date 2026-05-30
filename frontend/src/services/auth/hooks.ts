"use client"

import { useMutation } from "@tanstack/react-query"

import { postLogin, postLogout } from "@/lib/api/auth"

export function useLoginMutation() {
  return useMutation({
    mutationFn: postLogin,
  })
}

export function useLogoutMutation() {
  return useMutation({
    mutationFn: postLogout,
  })
}
