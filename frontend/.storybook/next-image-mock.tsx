/**
 * Storybook-only stand-in for `next/image`.
 *
 * `@storybook/nextjs-vite`'s built-in next/image handling fails to resolve to a
 * component under this Next 16 / React 19 setup ("Element type is invalid …
 * got: object"), so stories that render images (FourPicsView, PictureView) crash.
 * This renders a plain <img>, stripping the next-specific props, and is aliased
 * in for `next/image` via `.storybook/main.ts` viteFinal. App code is unchanged.
 */

import type { CSSProperties, ImgHTMLAttributes } from "react"

type NextImageLikeProps = Omit<ImgHTMLAttributes<HTMLImageElement>, "src"> & {
  src: string | { src: string }
  alt?: string
  fill?: boolean
  priority?: boolean
  quality?: number
  sizes?: string
  placeholder?: string
  blurDataURL?: string
  loader?: unknown
}

export default function NextImageMock({
  src,
  alt = "",
  fill,
  priority: _priority,
  quality: _quality,
  sizes: _sizes,
  placeholder: _placeholder,
  blurDataURL: _blurDataURL,
  loader: _loader,
  style,
  ...rest
}: NextImageLikeProps) {
  const resolved = typeof src === "object" && src !== null ? src.src : src
  const fillStyle: CSSProperties | undefined = fill
    ? { position: "absolute", inset: 0, width: "100%", height: "100%" }
    : undefined

  // eslint-disable-next-line @next/next/no-img-element
  return (
    <img
      src={resolved}
      alt={alt}
      style={{ ...fillStyle, ...style }}
      {...rest}
    />
  )
}
