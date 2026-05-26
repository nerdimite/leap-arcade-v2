export const FEEDBACK_DURATION_MS = 1500;
export const QUESTION_START_DELAY_MS = 500;
export const LEADERBOARD_POLL_INTERVAL_MS = 5000;

/** Four Pics answer overlay auto-dismiss (PRD). */
export const FOUR_PICS_ANSWER_OVERLAY_MS = 2000;

/** Pinpoint terminal puzzle flash before auto-advance (PRD). */
export const PINPOINT_RESULT_FLASH_MS = 2000;

/** Matches backend `FOUR_PICS_BASE_SCORE` — shown in correct overlay breakdown. */
export const FOUR_PICS_BASE_SCORE = 100;

/** Matches backend `FOUR_PICS_TIME_DECAY_MS` — time bonus reaches zero at this elapsed. */
export const FOUR_PICS_TIME_DECAY_MS = 30_000;

/** Matches backend `PINPOINT_TIME_BONUS_DECAY_MS` — time bonus reaches zero at this elapsed. */
export const PINPOINT_TIME_BONUS_DECAY_MS = 90_000;

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
  pinpoint: 3000,
  picture: 800,
  four_pics: 600,
  crossword: 1200,
} as const;

export type LobbyGameId = keyof typeof GAME_MAX_POINTS;
