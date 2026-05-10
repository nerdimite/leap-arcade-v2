"use client"

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { useNavigationGuard } from "@/hooks/use-navigation-guard"

export function GameNavigationGuardDialog() {
  const { cancelNavigation, confirmNavigation, dialogOpen } =
    useNavigationGuard()

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
          <AlertDialogCancel>Stay in game</AlertDialogCancel>
          <AlertDialogAction onClick={confirmNavigation}>
            Leave anyway
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
