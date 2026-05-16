import { Geist_Mono, Space_Grotesk } from "next/font/google"

import "./globals.css"
import { QueryClientProviderWrapper } from "@/components/query-client-provider"
import { ThemeProvider } from "@/components/theme-provider"
import { cn } from "@/lib/utils";

const spaceGrotesk = Space_Grotesk({subsets:['latin'],variable:'--font-sans'})

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
      className={cn("antialiased", fontMono.variable, "font-sans", spaceGrotesk.variable)}
    >
      <body>
        <ThemeProvider>
          <QueryClientProviderWrapper>{children}</QueryClientProviderWrapper>
        </ThemeProvider>
      </body>
    </html>
  )
}
