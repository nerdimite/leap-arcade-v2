export const FEEDBACK_DURATION_MS = 1500
export const QUESTION_START_DELAY_MS = 500
export const LEADERBOARD_POLL_INTERVAL_MS = 5000

/** Four Pics answer overlay auto-dismiss (PRD). */
export const FOUR_PICS_ANSWER_OVERLAY_MS = 2000

/** Pinpoint terminal puzzle flash before auto-advance (PRD). */
export const PINPOINT_RESULT_FLASH_MS = 2000

/** Matches backend `FOUR_PICS_BASE_SCORE` — shown in correct overlay breakdown. */
export const FOUR_PICS_BASE_SCORE = 100

/** Matches backend `FOUR_PICS_TIME_DECAY_MS` — time bonus reaches zero at this elapsed. */
export const FOUR_PICS_TIME_DECAY_MS = 30_000

/** Matches backend `PINPOINT_TIME_BONUS_DECAY_MS` — time bonus reaches zero at this elapsed. */
export const PINPOINT_TIME_BONUS_DECAY_MS = 90_000

/** Matches backend `WORD_HUNT_TIME_DECAY_MS` — time bonus reaches zero at this elapsed. */
export const WORD_HUNT_TIME_DECAY_MS = 600_000

/** Matches backend `WORD_HUNT_BASE_PER_WORD` — shown in find hit feedback. */
export const WORD_HUNT_BASE_PER_WORD = 100

/** Miss flash duration on failed grid traces (PRD). */
export const WORD_HUNT_MISS_FLASH_MS = 250

/** Score increment chip visibility after a successful find. */
export const WORD_HUNT_SCORE_INCREMENT_MS = 800

/** Staggered letter-pop celebration after a successful find (covers the per-letter delay tail). */
export const WORD_HUNT_LAND_ANIMATION_MS = 750

/** Matches backend `CROSSWORD_TIME_DECAY_MS` — time bonus reaches zero at this elapsed. */
export const CROSSWORD_TIME_DECAY_MS = 600_000

/** Matches backend `CROSSWORD_BASE_PER_ENTRY` — shown in solve hit feedback. */
export const CROSSWORD_BASE_PER_ENTRY = 100

/** Miss flash duration on wrong completed entries (PRD). */
export const CROSSWORD_MISS_FLASH_MS = 250

/** Score increment chip visibility after a successful solve. */
export const CROSSWORD_SCORE_INCREMENT_MS = 800

/** Staggered letter-pop celebration when an entry locks in (covers the per-letter delay tail). */
export const CROSSWORD_SOLVE_FLASH_MS = 750

/** React Query stale time for lobby session prefetch/hydration (avoid instant refetch flash). */
export const PLAYER_SESSIONS_STALE_TIME_MS = 30_000

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
  word_hunt: 1000,
  crossword: 1500,
} as const

export type LobbyGameId = keyof typeof GAME_MAX_POINTS
