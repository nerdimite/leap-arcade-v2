"use client";

import { useQuery } from "@tanstack/react-query";

import { getPlayerSessions, PLAYER_SESSIONS_QUERY_KEY } from "@/lib/api/players";
import { PLAYER_SESSIONS_STALE_TIME_MS } from "@/lib/constants";

export function usePlayerSessions() {
  return useQuery({
    queryKey: PLAYER_SESSIONS_QUERY_KEY,
    queryFn: () => getPlayerSessions(),
    staleTime: PLAYER_SESSIONS_STALE_TIME_MS,
  });
}
