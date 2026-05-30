import { Geist_Mono, Inter, Press_Start_2P } from "next/font/google"

import "./globals.css"
import { QueryClientProviderWrapper } from "@/components/query-client-provider"
import { ThemeProvider } from "@/components/theme-provider"
import { cn } from "@/lib/utils"

// Inter carries everything a player must read; Press Start 2P is pixel punctuation.
const fontSans = Inter({ subsets: ["latin"], variable: "--font-sans" })

const fontPixel = Press_Start_2P({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-pixel",
})

const fontMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
})

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={cn(
        "antialiased",
        "font-sans",
        fontSans.variable,
        fontPixel.variable,
        fontMono.variable
      )}
    >
      <body>
        <ThemeProvider>
          <QueryClientProviderWrapper>{children}</QueryClientProviderWrapper>
        </ThemeProvider>
      </body>
    </html>
  )
}
