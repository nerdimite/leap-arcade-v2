import { GameNavigationGuardDialog } from "@/components/layout/GameNavigationGuardDialog"
import { NavigationGuardProvider } from "@/hooks/use-navigation-guard"

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
