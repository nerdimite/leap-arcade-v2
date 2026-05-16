"use client"

import { useState } from "react"

import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button"
import { useNavigationGuard } from "@/hooks/use-navigation-guard"

export function GameNavigationGuardDialog() {
  const { cancelNavigation, confirmNavigation, dialogOpen } =
    useNavigationGuard()
  const [leaveBusy, setLeaveBusy] = useState(false)

  const handleLeave = async () => {
    setLeaveBusy(true)
    try {
      await confirmNavigation()
    } finally {
      setLeaveBusy(false)
    }
  }

  return (
    <AlertDialog
      open={dialogOpen}
      onOpenChange={(open) => {
        if (!open) cancelNavigation()
      }}
    >
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Game in progress</AlertDialogTitle>
          <AlertDialogDescription>
            You&apos;re in the middle of a game. Leaving now will forfeit your
            progress and the game will be locked.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={leaveBusy}>Stay in game</AlertDialogCancel>
          <Button
            type="button"
            variant="default"
            disabled={leaveBusy}
            onClick={() => {
              void handleLeave()
            }}
          >
            {leaveBusy ? "Leaving…" : "Leave anyway"}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
