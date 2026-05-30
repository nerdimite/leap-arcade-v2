"use client"

import { useQuery } from "@tanstack/react-query"

import { getLeaderboardQueryOptions } from "./query-options"

export function useLeaderboard() {
  return useQuery(getLeaderboardQueryOptions())
}
