"use client"

import { useCallback, useEffect, useRef, useState } from "react"

import { useNavigationGuard } from "@/hooks/use-navigation-guard"
import {
  postWikiAbandon,
  postWikiBack,
  postWikiNavigate,
  postWikiPlay,
  postWikiTimeout,
} from "@/lib/api/wiki"

import type { WikiPlayResponse } from "@/services/wiki/schema"

import { useWikiReducer } from "../_hooks/useWikiReducer"
import { WikiView } from "./WikiView"
import { toWikiViewState } from "./wiki-view-state"

export function WikiClient({ initialPlay }: { initialPlay: WikiPlayResponse }) {
  const [state, dispatch] = useWikiReducer(initialPlay)
  const { setIsDirty, registerBeforeNavigateConfirm } = useNavigationGuard()
  const tickRef = useRef<number | null>(null)
  const [navPending, setNavPending] = useState(false)
  const [continuePending, setContinuePending] = useState(false)
  const attemptIdRef = useRef<string | null>(null)
  const [pathRoot, setPathRoot] = useState("")
  const serverTimeoutSyncRef = useRef(false)

  useEffect(() => {
    if (state.phase !== "active" || state.timerRemainingMs == null) {
      serverTimeoutSyncRef.current = false
      return
    }
    if (state.timerRemainingMs > 0) {
      serverTimeoutSyncRef.current = false
      return
    }
    if (serverTimeoutSyncRef.current) {
      return
    }
    serverTimeoutSyncRef.current = true
    void postWikiTimeout()
      .then((res) => {
        dispatch({ type: "PLAY_OK", payload: res })
      })
      .catch(() => {
        dispatch({
          type: "PLAY_ERROR",
          payload: { message: "Could not sync timer — please try again." },
        })
      })
  }, [state.phase, state.timerRemainingMs, dispatch])

  useEffect(() => {
    return registerBeforeNavigateConfirm(async () => {
      await postWikiAbandon()
    })
  }, [registerBeforeNavigateConfirm])

  useEffect(() => {
    const dirty = state.phase === "active" || state.phase === "puzzleResult"
    setIsDirty(dirty)
  }, [state.phase, setIsDirty])

  useEffect(() => {
    if (state.phase !== "active") {
      if (tickRef.current != null) {
        window.clearInterval(tickRef.current)
        tickRef.current = null
      }
      return undefined
    }
    tickRef.current = window.setInterval(() => {
      dispatch({ type: "TICK", payload: { nowMs: Date.now() } })
    }, 250)
    return () => {
      if (tickRef.current != null) {
        window.clearInterval(tickRef.current)
        tickRef.current = null
      }
    }
  }, [state.phase, dispatch])

  useEffect(() => {
    if (state.play?.state !== "active") {
      return
    }
    const aid = state.play.current.attempt_id
    if (attemptIdRef.current !== aid) {
      attemptIdRef.current = aid
      setPathRoot(state.play.current.current_title)
    }
  }, [state.play])

  const navigateToTitle = useCallback(
    async (title: string) => {
      setNavPending(true)
      try {
        const res = await postWikiNavigate(title)
        dispatch({ type: "NAVIGATE_OK", payload: res })
      } catch {
        dispatch({
          type: "NAVIGATE_ERROR",
          payload: { message: "Navigation failed — please try again." },
        })
      } finally {
        setNavPending(false)
      }
    },
    [dispatch]
  )

  const continueViaPlay = useCallback(async () => {
    setContinuePending(true)
    try {
      const res = await postWikiPlay()
      dispatch({ type: "PLAY_OK", payload: res })
    } catch {
      dispatch({
        type: "PLAY_ERROR",
        payload: { message: "Could not continue — please try again." },
      })
    } finally {
      setContinuePending(false)
    }
  }, [dispatch])

  const wikiBack = useCallback(async () => {
    setNavPending(true)
    try {
      const res = await postWikiBack()
      dispatch({ type: "NAVIGATE_OK", payload: res })
    } catch {
      dispatch({
        type: "NAVIGATE_ERROR",
        payload: { message: "Back navigation failed — please try again." },
      })
    } finally {
      setNavPending(false)
    }
  }, [dispatch])

  const viewState = toWikiViewState(state, {
    pathRoot,
    navPending,
    continuePending,
  })

  return (
    <WikiView
      viewState={viewState}
      onNavigate={navigateToTitle}
      onBack={wikiBack}
      onContinue={continueViaPlay}
    />
  )
}
