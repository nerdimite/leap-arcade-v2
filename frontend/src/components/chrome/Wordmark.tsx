/**
 * Glitch & Giggle wordmark — pixel display type with a single rose offset shadow.
 * Use `default` on attract screens; `compact` in chrome (AppBar).
 */

import type { CSSProperties } from "react"

import { cn } from "@/lib/utils"

export type WordmarkProps = {
  size?: "default" | "compact"
  className?: string
}

const SIZE_CLASS = {
  default: "text-2xl tracking-wider",
  compact: "text-[13px] tracking-wide",
} as const

const SIZE_SHADOW: Record<NonNullable<WordmarkProps["size"]>, CSSProperties> = {
  default: { textShadow: "3px 3px 0 var(--pin)" },
  compact: { textShadow: "2px 2px 0 var(--pin)" },
}

export function Wordmark({ size = "default", className }: WordmarkProps) {
  return (
    <span
      aria-hidden
      className={cn(
        "font-pixel leading-none text-ink select-none",
        SIZE_CLASS[size],
        className
      )}
      style={SIZE_SHADOW[size]}
    >
      GLITCH &amp; GIGGLE
    </span>
  )
}
