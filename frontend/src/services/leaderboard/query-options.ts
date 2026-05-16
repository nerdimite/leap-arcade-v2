import { getLeaderboard, LEADERBOARD_QUERY_KEY } from "@/lib/api/leaderboard";
import {
  LEADERBOARD_POLL_INTERVAL_MS,
  PLAYER_SESSIONS_STALE_TIME_MS,
} from "@/lib/constants";

export function getLeaderboardQueryOptions(init?: RequestInit) {
  return {
    queryKey: LEADERBOARD_QUERY_KEY,
    queryFn: () => getLeaderboard(init),
    staleTime: PLAYER_SESSIONS_STALE_TIME_MS,
    refetchInterval: LEADERBOARD_POLL_INTERVAL_MS,
  } as const;
}
