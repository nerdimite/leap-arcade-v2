"use client"

import { useEffect, useRef, useState } from "react"

import { useNavigationGuard } from "@/hooks/use-navigation-guard"
import { FEEDBACK_DURATION_MS, QUESTION_START_DELAY_MS } from "@/lib/constants"
import { useAbandon, useSubmitAnswer } from "@/services/rapid_fire/hooks"
import type { PlayResponse } from "@/services/rapid_fire/schema"

import { useRapidFireReducer } from "../_hooks/useRapidFireReducer"
import { RapidFireView } from "./RapidFireView"
import { toRapidFireViewState } from "./rapid-fire-view-state"

export function RapidFireClient({
  initialPlay,
}: {
  initialPlay: PlayResponse
}) {
  const [state, dispatch] = useRapidFireReducer(initialPlay)
  const { setIsDirty, navigateSafe, registerBeforeNavigateConfirm } =
    useNavigationGuard()
  const { mutateAsync: submitAnswer } = useSubmitAnswer()
  const { mutateAsync: abandonSession } = useAbandon()

  const questionEnteredAtRef = useRef<number>(Date.now())
  const resultDirtyClearedRef = useRef(false)
  const [timerPulse, setTimerPulse] = useState(0)

  useEffect(() => {
    if (state.status === "question" && state.currentQuestion) {
      questionEnteredAtRef.current = Date.now()
    }
  }, [state.status, state.currentQuestion?.id, state.currentQuestion])

  useEffect(() => {
    const inProgress =
      state.status === "loading" ||
      state.status === "question" ||
      state.status === "submitting" ||
      state.status === "feedback"
    setIsDirty(inProgress)
  }, [state.status, setIsDirty])

  useEffect(() => {
    const inProgress =
      state.status === "loading" ||
      state.status === "question" ||
      state.status === "submitting" ||
      state.status === "feedback"
    if (!inProgress) {
      return undefined
    }
    return registerBeforeNavigateConfirm(async () => {
      await abandonSession()
    })
  }, [abandonSession, registerBeforeNavigateConfirm, state.status])

  useEffect(() => {
    if (state.status !== "result") {
      resultDirtyClearedRef.current = false
      return
    }
    if (resultDirtyClearedRef.current) return
    resultDirtyClearedRef.current = true
    dispatch({ type: "RESULT_SHOWN" })
    setIsDirty(false)
  }, [dispatch, setIsDirty, state.status])

  useEffect(() => {
    if (state.status !== "feedback") return
    const id = window.setTimeout(() => {
      dispatch({ type: "FEEDBACK_COMPLETE" })
    }, FEEDBACK_DURATION_MS)
    return () => window.clearTimeout(id)
  }, [dispatch, state.status])

  useEffect(() => {
    const question = state.currentQuestion
    if (state.status !== "submitting" || !question) return
    let cancelled = false
    void (async () => {
      try {
        const res = await submitAnswer({
          question_id: question.id,
          selected_option: state.submittedOption,
          time_ms: state.pendingTimeMs ?? 0,
        })
        if (cancelled) return
        dispatch({ type: "ANSWER_SUCCESS", payload: res })
      } catch {
        if (cancelled) return
        dispatch({ type: "ANSWER_ERROR" })
      }
    })()
    return () => {
      cancelled = true
    }
  }, [
    dispatch,
    state.currentQuestion,
    state.pendingTimeMs,
    state.status,
    state.submittedOption,
    submitAnswer,
  ])

  // Number keys 1-4 answer during the question phase, so speed players never reach for the mouse.
  useEffect(() => {
    const question = state.currentQuestion
    if (state.status !== "question" || !question) return undefined
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.metaKey || event.ctrlKey || event.altKey) return
      const choice = Number.parseInt(event.key, 10)
      if (
        !Number.isInteger(choice) ||
        choice < 1 ||
        choice > question.options.length
      )
        return
      event.preventDefault()
      const limit = question.time_limit_ms
      const elapsed = Date.now() - questionEnteredAtRef.current
      dispatch({
        type: "SELECT_OPTION",
        payload: {
          selected_option: choice,
          time_ms: Math.min(limit, Math.max(0, elapsed)),
        },
      })
    }
    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [dispatch, state.status, state.currentQuestion])

  useEffect(() => {
    if (state.status !== "question" || !state.currentQuestion) return
    const limit = state.currentQuestion.time_limit_ms
    const interval = window.setInterval(() => {
      const elapsed = Date.now() - questionEnteredAtRef.current
      const displayElapsed = Math.max(0, elapsed - QUESTION_START_DELAY_MS)
      if (displayElapsed >= limit) {
        dispatch({
          type: "TIMER_EXPIRE",
          payload: { time_ms: limit },
        })
      }
      setTimerPulse((n) => n + 1)
    }, 50)
    return () => window.clearInterval(interval)
  }, [dispatch, state.currentQuestion, state.status])

  let timerBarPct: number | null = null
  if (state.status === "question" && state.currentQuestion) {
    void timerPulse
    const limit = state.currentQuestion.time_limit_ms
    const elapsed = Date.now() - questionEnteredAtRef.current
    const displayElapsed = Math.max(0, elapsed - QUESTION_START_DELAY_MS)
    const frac = Math.min(1, displayElapsed / limit)
    timerBarPct = (1 - frac) * 100
  }

  const viewState = toRapidFireViewState(state, timerBarPct)

  return (
    <RapidFireView
      viewState={viewState}
      questionEnteredAtRef={questionEnteredAtRef}
      onSelectOption={(optionIndex1, timeMs) => {
        dispatch({
          type: "SELECT_OPTION",
          payload: { selected_option: optionIndex1, time_ms: timeMs },
        })
      }}
      onBackToLobby={() => navigateSafe("/lobby")}
    />
  )
}
