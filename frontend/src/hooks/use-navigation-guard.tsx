"use client"

import { useRouter } from "next/navigation"
import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react"

import { useUnsavedChanges } from "./use-unsaved-changes"

type NavigationAction = () => void | Promise<void>

type PendingRequest =
  | { type: "href"; href: string; replace?: boolean }
  | { type: "action"; action: NavigationAction }
  | { type: "history-back" }

export interface NavigationGuardContextValue {
  isDirty: boolean
  setIsDirty: (dirty: boolean) => void
  navigateSafe: (href: string, options?: { replace?: boolean }) => void
  requestAction: (action: NavigationAction) => void
  registerBeforeNavigateConfirm: (fn: () => Promise<void>) => () => void
  dialogOpen: boolean
  confirmNavigation: () => Promise<void>
  cancelNavigation: () => void
}

const NavigationGuardContext =
  createContext<NavigationGuardContextValue | null>(null)

function createGuardStateId(): string {
  return `navigation-guard:${Math.random().toString(36).slice(2)}`
}

export function NavigationGuardProvider({ children }: { children: ReactNode }) {
  const router = useRouter()
  const [isDirty, setDirtyState] = useState(false)
  const [pendingRequest, setPendingRequest] = useState<PendingRequest | null>(
    null
  )
  const [dialogOpen, setDialogOpen] = useState(false)

  const isDirtyRef = useRef(false)
  const beforeNavigateConfirmRef = useRef<(() => Promise<void>) | null>(null)
  const historyTrapArmedRef = useRef(false)
  const suppressNextPopRef = useRef(false)
  const skipAutoCollapseRef = useRef(false)
  const guardStateIdRef = useRef(createGuardStateId())

  useUnsavedChanges(isDirty)

  const setIsDirty = useCallback((dirty: boolean) => {
    isDirtyRef.current = dirty
    setDirtyState(dirty)
  }, [])

  const registerBeforeNavigateConfirm = useCallback(
    (fn: () => Promise<void>) => {
      beforeNavigateConfirmRef.current = fn
      return () => {
        if (beforeNavigateConfirmRef.current === fn) {
          beforeNavigateConfirmRef.current = null
        }
      }
    },
    []
  )

  const armHistoryTrap = useCallback(() => {
    if (
      typeof window === "undefined" ||
      historyTrapArmedRef.current ||
      !isDirtyRef.current
    ) {
      return
    }

    const nextState =
      window.history.state && typeof window.history.state === "object"
        ? { ...window.history.state }
        : {}

    window.history.pushState(
      {
        ...nextState,
        __navigationGuard: guardStateIdRef.current,
      },
      "",
      window.location.href
    )
    historyTrapArmedRef.current = true
  }, [])

  const collapseHistoryTrap = useCallback((onAfterCollapse?: () => void) => {
    if (typeof window === "undefined" || !historyTrapArmedRef.current) {
      onAfterCollapse?.()
      return
    }

    suppressNextPopRef.current = true
    historyTrapArmedRef.current = false
    window.history.back()

    if (onAfterCollapse) {
      window.setTimeout(onAfterCollapse, 0)
    }
  }, [])

  const executeRequest = useCallback(
    (request: PendingRequest) => {
      if (request.type === "href") {
        if (request.replace) {
          router.replace(request.href)
        } else {
          router.push(request.href)
        }
        return
      }

      if (request.type === "action") {
        void request.action()
        return
      }

      suppressNextPopRef.current = true
      window.history.back()
    },
    [router]
  )

  const requestNavigation = useCallback(
    (request: PendingRequest) => {
      if (isDirtyRef.current) {
        setPendingRequest(request)
        setDialogOpen(true)
        return
      }

      executeRequest(request)
    },
    [executeRequest]
  )

  const navigateSafe = useCallback(
    (href: string, options?: { replace?: boolean }) => {
      requestNavigation({
        type: "href",
        href,
        replace: options?.replace,
      })
    },
    [requestNavigation]
  )

  const requestAction = useCallback(
    (action: NavigationAction) => {
      requestNavigation({ type: "action", action })
    },
    [requestNavigation]
  )

  const cancelNavigation = useCallback(() => {
    const request = pendingRequest
    setPendingRequest(null)
    setDialogOpen(false)

    if (request?.type === "history-back" && isDirtyRef.current) {
      armHistoryTrap()
    }
  }, [armHistoryTrap, pendingRequest])

  const confirmNavigation = useCallback(async () => {
    const request = pendingRequest
    if (!request) return

    try {
      if (beforeNavigateConfirmRef.current) {
        await beforeNavigateConfirmRef.current()
      }
    } catch {
      return
    }

    setPendingRequest(null)
    setDialogOpen(false)

    if (request.type === "history-back") {
      setIsDirty(false)
      executeRequest(request)
      return
    }

    skipAutoCollapseRef.current = true
    setIsDirty(false)
    collapseHistoryTrap(() => executeRequest(request))
  }, [collapseHistoryTrap, executeRequest, pendingRequest, setIsDirty])

  useEffect(() => {
    if (isDirty) {
      armHistoryTrap()
      return
    }

    if (skipAutoCollapseRef.current) {
      skipAutoCollapseRef.current = false
      return
    }

    collapseHistoryTrap()
  }, [armHistoryTrap, collapseHistoryTrap, isDirty])

  useEffect(() => {
    const handlePopState = () => {
      if (suppressNextPopRef.current) {
        suppressNextPopRef.current = false
        return
      }

      if (!isDirtyRef.current) {
        return
      }

      historyTrapArmedRef.current = false
      setPendingRequest({ type: "history-back" })
      setDialogOpen(true)
    }

    window.addEventListener("popstate", handlePopState)
    return () => window.removeEventListener("popstate", handlePopState)
  }, [])

  const value = useMemo<NavigationGuardContextValue>(
    () => ({
      isDirty,
      setIsDirty,
      navigateSafe,
      requestAction,
      registerBeforeNavigateConfirm,
      dialogOpen,
      confirmNavigation,
      cancelNavigation,
    }),
    [
      cancelNavigation,
      confirmNavigation,
      dialogOpen,
      isDirty,
      navigateSafe,
      registerBeforeNavigateConfirm,
      requestAction,
      setIsDirty,
    ]
  )

  return (
    <NavigationGuardContext.Provider value={value}>
      {children}
    </NavigationGuardContext.Provider>
  )
}

export function useNavigationGuard(): NavigationGuardContextValue {
  const ctx = useContext(NavigationGuardContext)
  if (!ctx) {
    throw new Error(
      "useNavigationGuard must be used within NavigationGuardProvider"
    )
  }
  return ctx
}
