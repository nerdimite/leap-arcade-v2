/**
 * Story/test fixtures built from the real Rapid Fire seed (vendored via
 * `npm run sync:seeds`). The seed is the authoring shape; these helpers strip
 * the answer to the runtime `Question` shape and wrap it with fabricated runtime
 * fields (score, counts, timer) to express each `RapidFireViewState` variant.
 *
 * Rapid Fire option indices are 1-based end to end (wire, view-state, and seed),
 * so `correct_option_index` copies straight into `lastCorrectOption`.
 */

import type { Question } from "@/services/rapid_fire/schema"
import rapidFireSeed from "@/test/seeds/rapid_fire.json"

import type { RapidFireViewState } from "../_components/rapid-fire-view-state"

type RapidFireSeedEntry = {
  id: string
  question: string
  options: string[]
  correct_option_index: number // 1-based
  category: string
  time_limit_ms: number
}

const seed = rapidFireSeed as RapidFireSeedEntry[]

/** Real total in the seeded set. */
export const RAPID_FIRE_TOTAL = seed.length

/** Seed content mapped to the runtime `Question` shape (answer/category dropped). */
export const seedQuestions: Question[] = seed.map((q) => ({
  id: q.id,
  question: q.question,
  options: q.options,
  time_limit_ms: q.time_limit_ms,
}))

/** 1-based correct option for each seed question. */
export const seedCorrectOptions: number[] = seed.map(
  (q) => q.correct_option_index
)

export function buildQuestionState(opts?: {
  index?: number
  timerBarPct?: number
  locked?: boolean
  submittedOption?: number | null
  currentScore?: number
}): Extract<RapidFireViewState, { status: "question" }> {
  const index = opts?.index ?? 0
  return {
    status: "question",
    question: seedQuestions[index],
    timerBarPct: opts?.timerBarPct ?? 70,
    currentScore: opts?.currentScore ?? 1240,
    questionsAnswered: index,
    questionsTotal: RAPID_FIRE_TOTAL,
    locked: opts?.locked ?? false,
    submittedOption: opts?.submittedOption ?? null,
    lastCorrect: null,
    lastCorrectOption: null,
  }
}

export function buildFeedbackState(opts: {
  index?: number
  correct: boolean
  currentScore?: number
  scoreDelta?: number
}): Extract<RapidFireViewState, { status: "feedback" }> {
  const index = opts.index ?? 0
  const correctOption = seedCorrectOptions[index]
  // A plausible wrong pick: the first option that isn't the correct one.
  const wrongOption = correctOption === 1 ? 2 : 1
  return {
    status: "feedback",
    question: seedQuestions[index],
    lastCorrect: opts.correct,
    lastCorrectOption: correctOption,
    submittedOption: opts.correct ? correctOption : wrongOption,
    currentScore: opts.currentScore ?? (opts.correct ? 1440 : 1240),
    scoreDelta: opts.scoreDelta ?? (opts.correct ? 120 : 0),
    questionsAnswered: index + 1,
    questionsTotal: RAPID_FIRE_TOTAL,
  }
}

/** Result is pure runtime (score/timing aren't in seeds); counts sum to the real total. */
export function buildResultState(): Extract<
  RapidFireViewState,
  { status: "result" }
> {
  return {
    status: "result",
    result: {
      score: 2360,
      correct_count: 11,
      wrong_count: 3,
      skipped_count: RAPID_FIRE_TOTAL - 11 - 3,
      time_taken_seconds: 142.3,
    },
  }
}
