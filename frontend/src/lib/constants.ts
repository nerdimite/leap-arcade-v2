export const FEEDBACK_DURATION_MS = 1500;
export const QUESTION_START_DELAY_MS = 500;
export const LEADERBOARD_POLL_INTERVAL_MS = 5000;

/** React Query stale time for lobby session prefetch/hydration (avoid instant refetch flash). */
export const PLAYER_SESSIONS_STALE_TIME_MS = 30_000;

/**
 * Max points shown on lobby tiles (not returned by the API; tuned to match backend rules).
 * Rapid Fire: up to 100 pts per correct answer at fastest time, × question pool size
 * (15 questions in seed → 1500).
 */
export const GAME_MAX_POINTS = {
  wiki: 1000,
  rapid_fire: 1500,
  picture: 800,
  four_pics: 600,
  crossword: 1200,
} as const;

export type LobbyGameId = keyof typeof GAME_MAX_POINTS;
