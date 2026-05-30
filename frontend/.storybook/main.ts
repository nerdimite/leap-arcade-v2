import { fileURLToPath } from "node:url"

import type { StorybookConfig } from "@storybook/nextjs-vite"

const nextImageMock = fileURLToPath(
  new URL("./next-image-mock.tsx", import.meta.url)
)

const config: StorybookConfig = {
  stories: ["../src/**/*.stories.@(ts|tsx)"],
  addons: [
    "@storybook/addon-a11y",
    "@storybook/addon-docs",
    "@chromatic-com/storybook",
    "@storybook/addon-vitest",
  ],
  framework: "@storybook/nextjs-vite",
  staticDirs: ["../public"],
  // The framework's built-in next/image handling resolves to an object (not a
  // component) under Next 16 / React 19, crashing image stories. Alias it to a
  // plain-<img> mock; first-match-wins, so unshift ahead of the framework alias.
  async viteFinal(viteConfig) {
    viteConfig.resolve ??= {}
    const alias = viteConfig.resolve.alias
    if (Array.isArray(alias)) {
      alias.unshift({ find: /^next\/image$/, replacement: nextImageMock })
    } else {
      viteConfig.resolve.alias = {
        "next/image": nextImageMock,
        ...(alias ?? {}),
      }
    }
    return viteConfig
  },
}

export default config
