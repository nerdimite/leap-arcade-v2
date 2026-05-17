import type { Preview } from "@storybook/nextjs-vite"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { Geist_Mono, Space_Grotesk } from "next/font/google"
import * as React from "react"

import { ThemeProvider } from "../src/components/theme-provider"
import "../src/app/globals.css"

const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-sans" })
const fontMono = Geist_Mono({ subsets: ["latin"], variable: "--font-mono" })

const fontClasses = [spaceGrotesk.variable, fontMono.variable, "font-sans", "antialiased"]

// Portals (dropdowns, dialogs) mount to document.body which sits outside the
// decorator div. Syncing font classes to body ensures portal content inherits
// the same typeface as the rest of the story.
function FontSyncToBody({ children }: { children: React.ReactNode }) {
  React.useEffect(() => {
    document.body.classList.add(...fontClasses)
    return () => document.body.classList.remove(...fontClasses)
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
