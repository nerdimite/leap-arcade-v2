/** Smart wiring: login mutation, redirect on success, delegates UI to LoginView. */

"use client"

import { useRouter } from "next/navigation"
import { type FormEvent, useState } from "react"

import { LoginApiError } from "@/lib/api/auth"
import { useLoginMutation } from "@/services/auth/hooks"

import { LoginView } from "./LoginView"

export function LoginClient() {
  const router = useRouter()
  const [corpId, setCorpId] = useState("")
  const [eventCode, setEventCode] = useState("")
  const login = useLoginMutation()

  const showInvalidCreds =
    login.isError &&
    login.error instanceof LoginApiError &&
    (login.error.status === 401 || login.error.status === 404)

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    login.mutate(
      { corp_id: corpId, event_code: eventCode },
      {
        onSuccess: () => {
          router.replace("/lobby")
        },
      }
    )
  }

  return (
    <LoginView
      corpId={corpId}
      eventCode={eventCode}
      isPending={login.isPending}
      showInvalidCreds={showInvalidCreds}
      onCorpIdChange={setCorpId}
      onEventCodeChange={setEventCode}
      onSubmit={handleSubmit}
    />
  )
}
