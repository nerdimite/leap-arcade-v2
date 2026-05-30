import type { Preview } from "@storybook/nextjs-vite"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { Geist_Mono, Inter, Press_Start_2P } from "next/font/google"
import * as React from "react"

import { ThemeProvider } from "../src/components/theme-provider"
import "../src/app/globals.css"

// Mirror the app's font wiring (layout.tsx) so pixel/body type passes through to stories.
const fontSans = Inter({ subsets: ["latin"], variable: "--font-sans" })
const fontPixel = Press_Start_2P({ subsets: ["latin"], weight: "400", variable: "--font-pixel" })
const fontMono = Geist_Mono({ subsets: ["latin"], variable: "--font-mono" })

const fontClasses = [
  fontSans.variable,
  fontPixel.variable,
  fontMono.variable,
  "font-sans",
  "antialiased",
]

// Portals (dropdowns, dialogs) mount to document.body which sits outside the
// decorator div. Syncing font classes — and the force-dark `.dark` class so the
// arcade palette and scanline/vignette overlays render — keeps portal content
// and the canvas consistent with the app.
function FontSyncToBody({ children }: { children: React.ReactNode }) {
  React.useEffect(() => {
    document.body.classList.add(...fontClasses, "dark")
    return () => document.body.classList.remove(...fontClasses, "dark")
  }, [])
  return <>{children}</>
}

function StoryProviders({ children }: { children: React.ReactNode }) {
  const queryClient = React.useMemo(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { retry: false },
        },
      }),
    [],
  )

  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </ThemeProvider>
  )
}

const preview: Preview = {
  decorators: [
    (Story, context) => (
      <FontSyncToBody>
        <div className={fontClasses.join(" ")}>
          <StoryProviders key={context.id}>
            <Story />
          </StoryProviders>
        </div>
      </FontSyncToBody>
    ),
  ],
  parameters: {
    nextjs: {
      appDirectory: true,
    },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
}

export default preview
