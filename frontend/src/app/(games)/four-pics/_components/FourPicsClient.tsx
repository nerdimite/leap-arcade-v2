"use client"

import { useCallback, useEffect, useRef, useState } from "react"

import { elapsedMsFromStartedAt } from "@/app/(games)/four-pics/_lib/stopwatch"
import { useNavigationGuard } from "@/hooks/use-navigation-guard"
import { FOUR_PICS_ANSWER_OVERLAY_MS } from "@/lib/constants"
import {
  useAbandonFourPics,
  useSubmitFourPicsAnswer,
} from "@/services/four_pics/hooks"
import type {
  AnswerResponse,
  PlayResponse,
  QuestionState,
  Result,
} from "@/services/four_pics/schema"

import { type FourPicsOverlay, FourPicsView } from "./FourPicsView"

type Props = {
  initialPlay: PlayResponse
}

type OverlayState = FourPicsOverlay

export function FourPicsClient({ initialPlay }: Props) {
  const { setIsDirty, navigateSafe, registerBeforeNavigateConfirm } =
    useNavigationGuard()
  const { mutateAsync: submitAnswer, isPending } = useSubmitFourPicsAnswer()
  const { mutateAsync: abandonSession } = useAbandonFourPics()
  const advanceTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const pendingAdvanceRef = useRef<AnswerResponse | null>(null)
  const resultDirtyClearedRef = useRef(false)

  const [question, setQuestion] = useState<QuestionState | null>(() =>
    initialPlay.session_status === "active" ? initialPlay.question : null
  )
  const [result, setResult] = useState<Result | null>(() =>
    initialPlay.session_status !== "active" ? initialPlay.result : null
  )
  const [sessionScore, setSessionScore] = useState(initialPlay.session_score)
  const [overlay, setOverlay] = useState<OverlayState | null>(null)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const isInputLocked = isPending || overlay !== null

  useEffect(() => {
    const inPlay = question !== null && result === null
    setIsDirty(inPlay)
  }, [question, result, setIsDirty])

  useEffect(() => {
    const inPlay = question !== null && result === null
    if (!inPlay) {
      return undefined
    }
    return registerBeforeNavigateConfirm(async () => {
      await abandonSession()
    })
  }, [abandonSession, question, registerBeforeNavigateConfirm, result])

  useEffect(() => {
    if (result === null) {
      resultDirtyClearedRef.current = false
      return
    }
    if (resultDirtyClearedRef.current) return
    resultDirtyClearedRef.current = true
    setIsDirty(false)
  }, [result, setIsDirty])

  const applyAdvance = useCallback((res: AnswerResponse) => {
    setSessionScore(res.session_score)
    setOverlay(null)
    pendingAdvanceRef.current = null

    if (res.result) {
      setQuestion(null)
      setResult(res.result)
      return
    }

    if (res.question) {
      setQuestion(res.question)
    }
  }, [])

  useEffect(() => {
    return () => {
      if (advanceTimeoutRef.current !== null) {
        clearTimeout(advanceTimeoutRef.current)
      }
    }
  }, [])

  const scheduleAdvance = useCallback(
    (res: AnswerResponse) => {
      pendingAdvanceRef.current = res
      if (advanceTimeoutRef.current !== null) {
        clearTimeout(advanceTimeoutRef.current)
      }
      advanceTimeoutRef.current = setTimeout(() => {
        advanceTimeoutRef.current = null
        const pending = pendingAdvanceRef.current
        if (pending) {
          applyAdvance(pending)
        }
      }, FOUR_PICS_ANSWER_OVERLAY_MS)
    },
    [applyAdvance]
  )

  const handleSelect = useCallback(
    async (selectedIndex: number) => {
      if (question === null || isInputLocked) {
        return
      }

      setSubmitError(null)
      const timeMs = elapsedMsFromStartedAt(question.started_at)

      try {
        const res = await submitAnswer({
          question_id: question.question_id,
          selected_index: selectedIndex,
          time_ms: timeMs,
        })
        setSessionScore(res.session_score)
        setOverlay({
          correct: res.correct,
          score: res.score,
          timeBonus: res.time_bonus,
          selectedIndex,
        })
        scheduleAdvance(res)
      } catch {
        setSubmitError("Could not submit answer. Try again.")
      }
    },
    [isInputLocked, question, scheduleAdvance, submitAnswer]
  )

  if (result !== null) {
    return (
      <FourPicsView
        viewState={{ status: "result", result }}
        onSelect={() => {}}
        onBackToLobby={() => navigateSafe("/lobby")}
      />
    )
  }

  if (question === null) {
    return (
      <FourPicsView
        viewState={{ status: "empty" }}
        onSelect={() => {}}
        onBackToLobby={() => navigateSafe("/lobby")}
      />
    )
  }

  return (
    <FourPicsView
      viewState={{
        status: "playing",
        question,
        sessionScore,
        overlay,
        submitError,
        inputDisabled: isInputLocked,
      }}
      onSelect={(index) => void handleSelect(index)}
      onBackToLobby={() => navigateSafe("/lobby")}
    />
  )
}
