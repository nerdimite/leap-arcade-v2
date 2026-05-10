import { NavigationGuardProvider } from "@/hooks/use-navigation-guard"
import { GameNavigationGuardDialog } from "@/components/layout/GameNavigationGuardDialog"

export default function GamesLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <NavigationGuardProvider>
      {children}
      <GameNavigationGuardDialog />
    </NavigationGuardProvider>
  )
}
